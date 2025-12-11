"""BLE接続とデータ受信機能"""

import asyncio
import logging
from typing import Callable, Optional
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from .constants import (
    DARTSLIVE_UART_UUID,
    CONNECTION_TIMEOUT,
    RECONNECT_RETRY_MAX,
    RECONNECT_DELAY,
    DATA_PACKET_SIZE,
    SEGMENT_BYTE_INDEX
)

logger = logging.getLogger(__name__)


class DartsLiveClient:
    """DARTSLIVE HOMEデバイスとBLE通信を行うクライアント"""

    def __init__(
        self,
        device: BLEDevice,
        uart_uuid: str = DARTSLIVE_UART_UUID,
        connection_timeout: float = CONNECTION_TIMEOUT,
        reconnect_retry_max: int = RECONNECT_RETRY_MAX,
        reconnect_delay: float = RECONNECT_DELAY
    ):
        """
        Args:
            device: 接続するBLEデバイス
            uart_uuid: UART サービスのUUID
            connection_timeout: 接続タイムアウト(秒)
            reconnect_retry_max: 再接続最大リトライ回数
            reconnect_delay: 再接続間隔(秒)
        """
        self.device = device
        self.uart_uuid = uart_uuid
        self.connection_timeout = connection_timeout
        self.reconnect_retry_max = reconnect_retry_max
        self.reconnect_delay = reconnect_delay
        self.client: Optional[BleakClient] = None
        self._is_connected = False
        self._data_callback: Optional[Callable[[int], None]] = None

    @property
    def is_connected(self) -> bool:
        """接続状態を取得"""
        return self._is_connected and self.client is not None and self.client.is_connected

    def _notification_handler(self, sender: int, data: bytearray) -> None:
        """
        BLE通知ハンドラー

        Args:
            sender: 送信元の識別子
            data: 受信データ
        """
        try:
            if len(data) != DATA_PACKET_SIZE:
                logger.warning(
                    f"予期しないデータサイズ: {len(data)} bytes (期待値: {DATA_PACKET_SIZE} bytes)"
                )
                return

            # データ形式: a1 03 XX 00 00 (XXがセグメント番号)
            segment_code = data[SEGMENT_BYTE_INDEX]
            logger.debug(f"受信データ: {data.hex()} -> セグメントコード: 0x{segment_code:02x}")

            if self._data_callback:
                self._data_callback(segment_code)

        except Exception as e:
            logger.error(f"通知ハンドラーでエラーが発生: {e}")

    def set_data_callback(self, callback: Callable[[int], None]) -> None:
        """
        データ受信時のコールバック関数を設定

        Args:
            callback: セグメントコードを引数に取るコールバック関数
        """
        self._data_callback = callback

    async def connect(self) -> bool:
        """
        デバイスに接続

        Returns:
            接続成功時True、失敗時False
        """
        try:
            logger.info(f"デバイスに接続中: {self.device.name} ({self.device.address})")
            self.client = BleakClient(
                self.device.address,
                timeout=self.connection_timeout
            )
            await self.client.connect()

            if self.client.is_connected:
                logger.info(f"接続成功: {self.device.name}")
                self._is_connected = True
                return True
            else:
                logger.error("接続に失敗しました")
                return False

        except BleakError as e:
            logger.error(f"BLE接続エラー: {e}")
            return False
        except Exception as e:
            logger.error(f"接続中に予期しないエラー: {e}")
            return False

    async def disconnect(self) -> None:
        """デバイスから切断"""
        if self.client and self.client.is_connected:
            try:
                await self.client.disconnect()
                logger.info("デバイスから切断しました")
            except Exception as e:
                logger.error(f"切断中にエラーが発生: {e}")
            finally:
                self._is_connected = False

    async def start_notify(self) -> bool:
        """
        通知の受信を開始

        Returns:
            開始成功時True、失敗時False
        """
        if not self.is_connected or not self.client:
            logger.error("デバイスが接続されていません")
            return False

        try:
            logger.info(f"UUID {self.uart_uuid} の通知受信を開始")
            await self.client.start_notify(self.uart_uuid, self._notification_handler)
            logger.info("通知受信を開始しました")
            return True

        except BleakError as e:
            logger.error(f"通知開始エラー: {e}")
            return False
        except Exception as e:
            logger.error(f"通知開始中に予期しないエラー: {e}")
            return False

    async def stop_notify(self) -> None:
        """通知の受信を停止"""
        if self.is_connected and self.client:
            try:
                await self.client.stop_notify(self.uart_uuid)
                logger.info("通知受信を停止しました")
            except Exception as e:
                logger.error(f"通知停止中にエラーが発生: {e}")

    async def connect_with_retry(self) -> bool:
        """
        リトライ付きで接続

        Returns:
            接続成功時True、失敗時False
        """
        for attempt in range(1, self.reconnect_retry_max + 1):
            logger.info(f"接続試行 {attempt}/{self.reconnect_retry_max}")

            if await self.connect():
                return True

            if attempt < self.reconnect_retry_max:
                logger.info(f"{self.reconnect_delay}秒後に再接続します...")
                await asyncio.sleep(self.reconnect_delay)

        logger.error(f"{self.reconnect_retry_max}回の接続試行に失敗しました")
        return False

    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリー"""
        if not await self.connect():
            raise BleakError("デバイスへの接続に失敗しました")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了"""
        await self.disconnect()
