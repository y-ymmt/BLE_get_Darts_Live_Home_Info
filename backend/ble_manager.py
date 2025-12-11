"""BLE接続を管理し、イベントバスでデータを配信"""

import asyncio
import logging
import threading
import queue
from datetime import datetime
from typing import Optional

from src.ble.scanner import DartsLiveScanner
from src.ble.client import DartsLiveClient
from src.data.mapper import SegmentMapper
from src.data.storage import DartDatabase
from src.data.models import DartThrow
from src.core.config import AppConfig
from backend.event_bus import EventBus

logger = logging.getLogger(__name__)


class BLEManager:
    """BLE接続をシングルトンとして管理"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # スレッドセーフな初期化チェック
        with self._lock:
            if hasattr(self, '_initialized'):
                return
            self._initialized = True

        # 初期化処理
        self.config = AppConfig()
        self.scanner = DartsLiveScanner(
            scan_timeout=self.config.scan_timeout,
            retry_max=self.config.scan_retry_max,
            retry_delay=self.config.scan_retry_delay
        )
        self.client: Optional[DartsLiveClient] = None
        self.mapper = SegmentMapper()
        self.database = DartDatabase(self.config.db_path)
        self.event_bus = EventBus()

        self.is_running = False
        self._worker_running = True
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.device_address = ""
        self.device_name = ""

        # 投擲データ処理用のキューとワーカースレッド（最大1000件）
        self._processing_queue: queue.Queue = queue.Queue(maxsize=1000)
        self._processing_thread = threading.Thread(
            target=self._process_throws_worker,
            daemon=True
        )
        self._processing_thread.start()
        logger.debug("投擲データ処理ワーカースレッドを開始しました")

    def start_background(self) -> None:
        """バックグラウンドスレッドでBLE接続を開始"""
        if self.is_running:
            logger.warning("BLE接続は既に実行中です")
            return

        self.is_running = True
        self._thread = threading.Thread(target=self._run_ble_loop, daemon=True)
        self._thread.start()
        logger.info("BLEマネージャーをバックグラウンドで開始しました")

    def _run_ble_loop(self) -> None:
        """BLEイベントループを別スレッドで実行"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            logger.error(f"BLEループでエラーが発生: {e}")
        finally:
            self._loop.close()

    async def _connect_and_listen(self) -> None:
        """デバイスに接続してデータをリッスン（自動再接続付き）"""
        reconnect_attempt = 0

        while self.is_running or reconnect_attempt == 0:
            try:
                logger.info("DARTSLIVE HOMEデバイスを検索中...")
                device = await self.scanner.scan_with_retry()

                if not device:
                    logger.error("デバイスが見つかりませんでした")
                    self.event_bus.publish('ble_error', {
                        'error': 'device_not_found',
                        'message': 'DARTSLIVE HOMEデバイスが見つかりません'
                    })

                    if not self.is_running:
                        break

                    # 再スキャン前に待機
                    logger.info("5秒後に再スキャンします...")
                    await asyncio.sleep(5)
                    continue

                self.device_address = device.address
                self.device_name = device.name or "Unknown"

                logger.info(f"デバイスに接続中: {self.device_name} ({self.device_address})")
                self.client = DartsLiveClient(
                    device=device,
                    connection_timeout=self.config.connection_timeout,
                    reconnect_retry_max=self.config.reconnect_retry_max,
                    reconnect_delay=self.config.reconnect_delay
                )

                self.client.set_data_callback(self._on_throw_data)

                if not await self.client.connect_with_retry():
                    logger.error("BLE接続に失敗しました")
                    self.event_bus.publish('ble_error', {
                        'error': 'connection_failed',
                        'message': 'デバイスへの接続に失敗しました'
                    })

                    if not self.is_running:
                        break

                    # 再接続前に待機
                    logger.info("5秒後に再接続を試みます...")
                    await asyncio.sleep(5)
                    continue

                # 接続成功
                logger.info("BLE接続成功")
                self.event_bus.publish('ble_connected', {
                    'device_address': self.device_address,
                    'device_name': self.device_name
                })

                await self.client.start_notify()
                self.is_running = True
                reconnect_attempt = 0

                # 接続監視ループ
                logger.info("接続を監視中...")
                while self.is_running:
                    # 接続状態をチェック
                    if not self.client.is_connected:
                        logger.warning("BLE接続が切断されました")
                        self.event_bus.publish('ble_error', {
                            'error': 'connection_lost',
                            'message': 'BLE接続が切断されました'
                        })
                        break

                    await asyncio.sleep(1)

                # クリーンアップ
                logger.info("接続をクリーンアップ中...")
                try:
                    await self.client.stop_notify()
                    logger.info("通知を停止しました")
                except Exception as e:
                    logger.error(f"通知停止中にエラー: {e}")

                try:
                    await self.client.disconnect()
                    logger.info("切断しました")
                except Exception as e:
                    logger.error(f"切断中にエラー: {e}")

                # 手動停止の場合は終了
                if not self.is_running:
                    logger.info("BLE接続を終了します")
                    break

                # 自動再接続
                reconnect_attempt += 1
                logger.info(f"再接続を試みます (試行 {reconnect_attempt})...")
                await asyncio.sleep(3)

            except Exception as e:
                logger.error(f"BLE接続中に予期しないエラー: {e}")
                self.event_bus.publish('ble_error', {
                    'error': 'unexpected_error',
                    'message': f'予期しないエラー: {str(e)}'
                })

                if not self.is_running:
                    break

                logger.info("5秒後に再接続を試みます...")
                await asyncio.sleep(5)

    def _on_throw_data(self, segment_code: int) -> None:
        """
        投擲データを受信してキューに追加（ノンブロッキング）

        Args:
            segment_code: BLEデバイスから受信したセグメントコード
        """
        try:
            # キューに入れるだけ（BLE通知ハンドラーをブロックしない）
            self._processing_queue.put_nowait({
                'segment_code': segment_code,
                'timestamp': datetime.now(),
                'device_address': self.device_address,
                'device_name': self.device_name
            })
            logger.debug(f"投擲データをキューに追加: 0x{segment_code:02x}")
        except queue.Full:
            logger.error("処理キューが満杯です。投擲データを破棄しました")
        except Exception as e:
            logger.error(f"投擲データのキューイング中にエラー: {e}")

    def _process_throws_worker(self) -> None:
        """
        投擲データを処理するワーカースレッド
        キューから投擲データを取り出してDB保存とイベント配信を行う
        """
        logger.info("投擲データ処理ワーカーを開始しました")

        while self._worker_running:
            try:
                # キューから取得（タイムアウト付き）
                try:
                    throw_data = self._processing_queue.get(timeout=1.0)
                except queue.Empty:
                    continue  # タイムアウト時は停止フラグを再チェック

                try:
                    segment_code = throw_data['segment_code']
                    timestamp = throw_data['timestamp']
                    device_address = throw_data['device_address']
                    device_name = throw_data['device_name']

                    # セグメント情報を取得
                    base_number, multiplier, segment_name = self.mapper.get_segment_info(segment_code)
                    score = self.mapper.get_score(segment_code)

                    # プレイヤー交代ボタンの特殊処理
                    if segment_code == 0x54:
                        logger.info("プレイヤー交代ボタンが押されました")
                        self.event_bus.publish('player_change', {
                            'segment_code': segment_code,
                            'timestamp': timestamp.isoformat()
                        })

                        # プレイヤー交代もDBに記録
                        throw = DartThrow(
                            timestamp=timestamp,
                            segment_code=segment_code,
                            segment_name=segment_name,
                            base_number=base_number,
                            multiplier=multiplier,
                            score=score,
                            device_address=device_address,
                            device_name=device_name
                        )
                        self.database.save_throw(throw)
                        continue

                    # DartThrowモデルを作成
                    throw = DartThrow(
                        timestamp=timestamp,
                        segment_code=segment_code,
                        segment_name=segment_name,
                        base_number=base_number,
                        multiplier=multiplier,
                        score=score,
                        device_address=device_address,
                        device_name=device_name
                    )

                    # データベースに保存
                    throw_id = self.database.save_throw(throw)
                    throw.id = throw_id

                    logger.info(f"投擲検出: {segment_name} ({score}点) [ID: {throw_id}]")

                    # イベントバスで配信
                    self.event_bus.publish('throw', throw.to_dict())

                finally:
                    # 必ずtask_done()を呼ぶ
                    self._processing_queue.task_done()

            except Exception as e:
                logger.error(f"投擲データ処理中にエラーが発生: {e}")
                # エラーが発生してもワーカースレッドは停止しない

        logger.info("投擲データ処理ワーカーを停止しました")

    def stop(self) -> None:
        """BLE接続を停止"""
        logger.info("BLE接続を停止中...")
        self.is_running = False
        self._worker_running = False

        # BLE接続をクリーンアップ
        if self.client and self._loop and self._loop.is_running():
            # 通知を停止してから切断する
            async def cleanup():
                try:
                    await self.client.stop_notify()
                    logger.info("通知を停止しました")
                except Exception as e:
                    logger.error(f"通知停止中にエラー: {e}")

                try:
                    await self.client.disconnect()
                except Exception as e:
                    logger.error(f"切断中にエラー: {e}")

            future = asyncio.run_coroutine_threadsafe(cleanup(), self._loop)
            try:
                future.result(timeout=10)
            except Exception as e:
                logger.error(f"クリーンアップ中にエラーが発生: {e}")

        # ワーカースレッドの停止を待つ
        if self._processing_thread and self._processing_thread.is_alive():
            logger.info("投擲データ処理ワーカーの停止を待機中...")
            self._processing_thread.join(timeout=5)

        logger.info("BLE接続を停止しました")

    def get_status(self) -> dict:
        """BLE接続状態を取得"""
        return {
            'is_running': self.is_running,
            'is_connected': self.client.is_connected if self.client else False,
            'device_address': self.device_address,
            'device_name': self.device_name
        }
