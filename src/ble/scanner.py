"""BLEデバイスのスキャン機能"""

import asyncio
import logging
from typing import Optional, List
from bleak import BleakScanner
from bleak.backends.device import BLEDevice

from .constants import (
    DARTSLIVE_DEVICE_NAME_PATTERNS,
    SCAN_TIMEOUT,
    SCAN_RETRY_MAX,
    SCAN_RETRY_DELAY
)

logger = logging.getLogger(__name__)


class DartsLiveScanner:
    """DARTSLIVE HOMEデバイスをスキャンするクラス"""

    def __init__(
        self,
        device_name_patterns: Optional[List[str]] = None,
        scan_timeout: float = SCAN_TIMEOUT,
        retry_max: int = SCAN_RETRY_MAX,
        retry_delay: float = SCAN_RETRY_DELAY
    ):
        """
        Args:
            device_name_patterns: デバイス名のパターンリスト
            scan_timeout: スキャンタイムアウト(秒)
            retry_max: 最大リトライ回数
            retry_delay: リトライ間隔(秒)
        """
        self.device_name_patterns = device_name_patterns or DARTSLIVE_DEVICE_NAME_PATTERNS
        self.scan_timeout = scan_timeout
        self.retry_max = retry_max
        self.retry_delay = retry_delay

    def _is_dartslive_device(self, device: BLEDevice) -> bool:
        """
        デバイスがDARTSLIVE HOMEかどうかを判定

        Args:
            device: BLEデバイス

        Returns:
            DARTSLIVE HOMEの場合True
        """
        if not device.name:
            return False

        return any(
            pattern.lower() in device.name.lower()
            for pattern in self.device_name_patterns
        )

    async def scan_once(self) -> Optional[BLEDevice]:
        """
        1回のスキャンを実行してDARTSLIVE HOMEデバイスを探す

        Returns:
            見つかったデバイス、見つからなければNone
        """
        logger.info(f"BLEデバイスをスキャン中... (タイムアウト: {self.scan_timeout}秒)")

        try:
            devices = await BleakScanner.discover(timeout=self.scan_timeout)
            logger.info(f"{len(devices)}個のBLEデバイスが見つかりました")

            for device in devices:
                logger.debug(f"検出: {device.name} ({device.address})")
                if self._is_dartslive_device(device):
                    logger.info(f"DARTSLIVE HOMEデバイスを発見: {device.name} ({device.address})")
                    return device

            logger.warning("DARTSLIVE HOMEデバイスが見つかりませんでした")
            return None

        except Exception as e:
            logger.error(f"スキャン中にエラーが発生: {e}")
            return None

    async def scan_with_retry(self) -> Optional[BLEDevice]:
        """
        リトライ付きでDARTSLIVE HOMEデバイスをスキャン

        Returns:
            見つかったデバイス、見つからなければNone
        """
        for attempt in range(1, self.retry_max + 1):
            logger.info(f"スキャン試行 {attempt}/{self.retry_max}")

            device = await self.scan_once()
            if device:
                return device

            if attempt < self.retry_max:
                logger.info(f"{self.retry_delay}秒後に再スキャンします...")
                await asyncio.sleep(self.retry_delay)

        logger.error(f"{self.retry_max}回のスキャンでデバイスが見つかりませんでした")
        return None

    async def scan_all_devices(self) -> List[BLEDevice]:
        """
        すべてのDARTSLIVE HOMEデバイスをスキャン(将来の複数デバイス対応用)

        Returns:
            見つかったDARTSLIVE HOMEデバイスのリスト
        """
        logger.info("すべてのDARTSLIVE HOMEデバイスをスキャン中...")

        try:
            devices = await BleakScanner.discover(timeout=self.scan_timeout)
            dartslive_devices = [
                device for device in devices
                if self._is_dartslive_device(device)
            ]

            logger.info(f"{len(dartslive_devices)}個のDARTSLIVE HOMEデバイスが見つかりました")
            for device in dartslive_devices:
                logger.info(f"  - {device.name} ({device.address})")

            return dartslive_devices

        except Exception as e:
            logger.error(f"スキャン中にエラーが発生: {e}")
            return []
