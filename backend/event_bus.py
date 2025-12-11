"""Pub/Subパターンによるイベントバス"""

import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """イベント駆動アーキテクチャのためのイベントバス"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        イベントタイプに対してコールバックを登録

        Args:
            event_type: イベントの種類（例: 'throw', 'player_change'）
            callback: イベント発生時に呼び出される関数
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(callback)
        logger.debug(f"イベント購読: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        イベント購読を解除

        Args:
            event_type: イベントの種類
            callback: 登録解除するコールバック関数
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"イベント購読解除: {event_type}")
            except ValueError:
                logger.warning(f"購読解除: コールバックが見つかりません: {event_type}")

    def publish(self, event_type: str, data: dict) -> None:
        """
        イベントを発行し、すべての購読者に通知

        Args:
            event_type: イベントの種類
            data: イベントデータ
        """
        if event_type not in self._subscribers:
            logger.debug(f"購読者なし: {event_type}")
            return

        logger.info(f"イベント発行: {event_type}, 購読者数: {len(self._subscribers[event_type])}")

        for callback in self._subscribers[event_type]:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"イベントハンドラーでエラー: {event_type}, {e}")
