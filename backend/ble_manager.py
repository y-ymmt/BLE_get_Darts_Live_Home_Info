"""BLE接続を管理し、イベントバスでデータを配信"""

import asyncio
import logging
import threading
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
        # 初回のみ初期化
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
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
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.device_address = ""
        self.device_name = ""

    def start_background(self) -> None:
        """バックグラウンドスレッドでBLE接続を開始"""
        if self.is_running:
            logger.warning("BLE接続は既に実行中です")
            return

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
        """デバイスに接続してデータをリッスン"""
        logger.info("DARTSLIVE HOMEデバイスを検索中...")
        device = await self.scanner.scan_with_retry()

        if not device:
            logger.error("デバイスが見つかりませんでした")
            self.event_bus.publish('ble_error', {
                'error': 'device_not_found',
                'message': 'DARTSLIVE HOMEデバイスが見つかりません'
            })
            return

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

        if await self.client.connect_with_retry():
            logger.info("BLE接続成功")
            self.event_bus.publish('ble_connected', {
                'device_address': self.device_address,
                'device_name': self.device_name
            })

            await self.client.start_notify()
            self.is_running = True

            # 接続を維持
            while self.is_running:
                await asyncio.sleep(1)
        else:
            logger.error("BLE接続に失敗しました")
            self.event_bus.publish('ble_error', {
                'error': 'connection_failed',
                'message': 'デバイスへの接続に失敗しました'
            })

    def _on_throw_data(self, segment_code: int) -> None:
        """
        投擲データを受信してイベントバスに配信

        Args:
            segment_code: BLEデバイスから受信したセグメントコード
        """
        try:
            # セグメント情報を取得
            base_number, multiplier, segment_name = self.mapper.get_segment_info(segment_code)
            score = self.mapper.get_score(segment_code)

            # プレイヤー交代ボタンの特殊処理
            if segment_code == 0x54:
                logger.info("プレイヤー交代ボタンが押されました")
                self.event_bus.publish('player_change', {
                    'segment_code': segment_code,
                    'timestamp': datetime.now().isoformat()
                })

                # プレイヤー交代もDBに記録
                throw = DartThrow(
                    timestamp=datetime.now(),
                    segment_code=segment_code,
                    segment_name=segment_name,
                    base_number=base_number,
                    multiplier=multiplier,
                    score=score,
                    device_address=self.device_address,
                    device_name=self.device_name
                )
                throw_id = self.database.save_throw(throw)
                return

            # DartThrowモデルを作成
            throw = DartThrow(
                timestamp=datetime.now(),
                segment_code=segment_code,
                segment_name=segment_name,
                base_number=base_number,
                multiplier=multiplier,
                score=score,
                device_address=self.device_address,
                device_name=self.device_name
            )

            # データベースに保存
            throw_id = self.database.save_throw(throw)
            throw.id = throw_id

            logger.info(f"投擲検出: {segment_name} ({score}点) [ID: {throw_id}]")

            # イベントバスで配信
            self.event_bus.publish('throw', throw.to_dict())

        except Exception as e:
            logger.error(f"投擲データ処理中にエラーが発生: {e}")

    def stop(self) -> None:
        """BLE接続を停止"""
        logger.info("BLE接続を停止中...")
        self.is_running = False

        if self.client and self._loop:
            future = asyncio.run_coroutine_threadsafe(
                self.client.disconnect(),
                self._loop
            )
            try:
                future.result(timeout=5)
            except Exception as e:
                logger.error(f"切断中にエラーが発生: {e}")

        logger.info("BLE接続を停止しました")

    def get_status(self) -> dict:
        """BLE接続状態を取得"""
        return {
            'is_running': self.is_running,
            'is_connected': self.client.is_connected if self.client else False,
            'device_address': self.device_address,
            'device_name': self.device_name
        }
