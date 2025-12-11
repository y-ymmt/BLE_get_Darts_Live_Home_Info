"""ログ設定"""

import logging
import sys
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_format: Optional[str] = None
) -> None:
    """
    ロガーを設定

    Args:
        log_level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: ログフォーマット
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ルートロガーの設定
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # 外部ライブラリのログレベルを調整
    logging.getLogger("bleak").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得

    Args:
        name: ロガー名

    Returns:
        ロガーインスタンス
    """
    return logging.getLogger(name)
