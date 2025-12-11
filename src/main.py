"""DARTSLIVE HOME データ取得アプリケーションのメインエントリーポイント"""

import asyncio
import signal
import sys
from datetime import datetime
from typing import Optional

from src.core.config import AppConfig
from src.core.logger import setup_logger, get_logger
from src.ble.scanner import DartsLiveScanner
from src.ble.client import DartsLiveClient
from src.data.models import DartThrow
from src.data.mapper import SegmentMapper
from src.data.storage import DartDatabase
from src.data.analyzer import DartAnalyzer

logger = get_logger(__name__)


class DartLiveApp:
    """DARTSLIVE HOME データ取得アプリケーション"""

    def __init__(self, config: Optional[AppConfig] = None):
        """
        Args:
            config: アプリケーション設定
        """
        self.config = config or AppConfig()
        self.scanner = DartsLiveScanner(
            scan_timeout=self.config.scan_timeout,
            retry_max=self.config.scan_retry_max,
            retry_delay=self.config.scan_retry_delay
        )
        self.client: Optional[DartsLiveClient] = None
        self.mapper = SegmentMapper()
        self.database = DartDatabase(self.config.db_path)
        self.analyzer = DartAnalyzer(self.database)
        self.is_running = False
        self.device_address = ""
        self.device_name = ""

    def _handle_dart_throw(self, segment_code: int) -> None:
        """
        ダーツ投擲データを処理

        Args:
            segment_code: セグメントコード
        """
        try:
            # セグメント情報を取得
            base_number, multiplier, segment_name = self.mapper.get_segment_info(segment_code)
            score = self.mapper.get_score(segment_code)

            # データモデルを作成
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

            # コンソールに表示
            logger.info(f"🎯 投擲検出: {segment_name} ({score}点) [ID: {throw_id}]")

        except Exception as e:
            logger.error(f"投擲データの処理中にエラーが発生: {e}")

    async def run(self) -> None:
        """アプリケーションを実行"""
        logger.info("=" * 60)
        logger.info("DARTSLIVE HOME データ取得アプリケーション")
        logger.info("=" * 60)
        logger.info("")

        try:
            # デバイスをスキャン
            logger.info("📡 DARTSLIVE HOMEデバイスを検索中...")
            device = await self.scanner.scan_with_retry()

            if not device:
                logger.error("❌ デバイスが見つかりませんでした")
                logger.info("以下を確認してください:")
                logger.info("  1. DARTSLIVE HOMEの電源が入っているか")
                logger.info("  2. Bluetoothがオンになっているか")
                logger.info("  3. デバイスが近くにあるか")
                return

            self.device_address = device.address
            self.device_name = device.name or "Unknown"

            # デバイスに接続
            self.client = DartsLiveClient(
                device=device,
                connection_timeout=self.config.connection_timeout,
                reconnect_retry_max=self.config.reconnect_retry_max,
                reconnect_delay=self.config.reconnect_delay
            )

            logger.info("🔗 デバイスに接続中...")
            if not await self.client.connect_with_retry():
                logger.error("❌ デバイスへの接続に失敗しました")
                return

            # コールバックを設定
            self.client.set_data_callback(self._handle_dart_throw)

            # 通知の受信を開始
            logger.info("🎯 データ受信を開始...")
            if not await self.client.start_notify():
                logger.error("❌ データ受信の開始に失敗しました")
                await self.client.disconnect()
                return

            logger.info("")
            logger.info("✅ 準備完了! ダーツを投げてください")
            logger.info("   (終了するには Ctrl+C を押してください)")
            logger.info("")

            self.is_running = True

            # 無限ループでデータを受信
            while self.is_running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("")
            logger.info("⏹️  ユーザーによる停止")
        except Exception as e:
            logger.error(f"❌ エラーが発生しました: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """クリーンアップ処理"""
        logger.info("")
        logger.info("🧹 クリーンアップ中...")

        if self.client:
            await self.client.stop_notify()
            await self.client.disconnect()

        # 統計情報を表示
        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 セッションサマリー")
        logger.info("=" * 60)

        stats = self.analyzer.get_statistics(device_address=self.device_address)
        logger.info(f"総投擲数: {stats['total_throws']}回")
        logger.info(f"合計得点: {stats['total_score']}点")
        if stats['total_throws'] > 0:
            logger.info(f"平均得点: {stats['average_score']:.2f}点")
            logger.info(f"最高得点: {stats['max_score']}点")

            # 最近の投擲を表示
            logger.info("")
            logger.info("直近の投擲:")
            recent_throws = self.analyzer.get_recent_throws_summary(
                limit=5,
                device_address=self.device_address
            )
            for i, throw in enumerate(recent_throws, 1):
                logger.info(f"  {i}. {throw['segment']} ({throw['score']}点) - {throw['timestamp']}")

        logger.info("")
        logger.info("👋 ありがとうございました!")

    def stop(self) -> None:
        """アプリケーションを停止"""
        self.is_running = False


def signal_handler(app: DartLiveApp):
    """シグナルハンドラー"""
    def handler(signum, frame):
        app.stop()
    return handler


async def main():
    """メイン関数"""
    # 設定の読み込み
    config = AppConfig()

    # ロガーのセットアップ
    setup_logger(config.log_level, config.log_format)

    # アプリケーションの作成と実行
    app = DartLiveApp(config)

    # シグナルハンドラーの設定
    signal.signal(signal.SIGINT, signal_handler(app))
    signal.signal(signal.SIGTERM, signal_handler(app))

    # アプリケーション実行
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)
