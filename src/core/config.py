"""設定管理"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """アプリケーション設定"""

    # データベース設定
    db_path: str = "data/dartslive.db"

    # BLE設定
    scan_timeout: float = 10.0
    scan_retry_max: int = 3
    scan_retry_delay: float = 5.0
    connection_timeout: float = 15.0
    reconnect_retry_max: int = 3
    reconnect_delay: float = 3.0

    # ログ設定
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # データ保持設定
    data_retention_days: int = 365  # データ保持期間(日)

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> 'AppConfig':
        """
        設定ファイルから読み込み (将来の機能拡張用)

        Args:
            config_path: 設定ファイルのパス

        Returns:
            設定インスタンス
        """
        # 現在はデフォルト設定を返す
        # 将来的にはJSON/YAML/TOML等から読み込む
        return cls()

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'db_path': self.db_path,
            'scan_timeout': self.scan_timeout,
            'scan_retry_max': self.scan_retry_max,
            'scan_retry_delay': self.scan_retry_delay,
            'connection_timeout': self.connection_timeout,
            'reconnect_retry_max': self.reconnect_retry_max,
            'reconnect_delay': self.reconnect_delay,
            'log_level': self.log_level,
            'log_format': self.log_format,
            'data_retention_days': self.data_retention_days,
        }
