"""ゲーム基底クラス"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


class Player:
    """プレイヤークラス"""

    def __init__(self, player_id: int, name: str, order: int):
        self.id = player_id
        self.name = name
        self.order = order
        self.is_current = False

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'order': self.order,
            'is_current': self.is_current
        }


class BaseGame(ABC):
    """ゲーム基底クラス"""

    def __init__(self, game_id: str, players: List[Player], settings: dict):
        self.game_id = game_id
        self.players = players
        self.current_player_index = 0
        self.settings = settings
        self.state = 'waiting'  # 'waiting', 'playing', 'finished'
        self.winner: Optional[Player] = None
        self.created_at = datetime.now()

        # 最初のプレイヤーを現在プレイヤーに設定
        if self.players:
            self.players[0].is_current = True

    @abstractmethod
    def handle_throw(self, throw_data: dict) -> Dict:
        """
        投擲を処理

        Args:
            throw_data: 投擲データ

        Returns:
            処理結果
        """
        pass

    def next_player(self) -> Player:
        """次のプレイヤーに交代"""
        # 現在のプレイヤーのフラグをオフ
        self.players[self.current_player_index].is_current = False

        # 次のプレイヤーに移動
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # 新しい現在プレイヤーのフラグをオン
        self.players[self.current_player_index].is_current = True

        return self.get_current_player()

    def get_current_player(self) -> Player:
        """現在のプレイヤーを取得"""
        return self.players[self.current_player_index]

    def get_state(self) -> dict:
        """ゲーム状態を取得"""
        return {
            'game_id': self.game_id,
            'state': self.state,
            'players': [p.to_dict() for p in self.players],
            'current_player_index': self.current_player_index,
            'winner': self.winner.to_dict() if self.winner else None,
            'created_at': self.created_at.isoformat()
        }

    def is_finished(self) -> bool:
        """ゲームが終了しているか"""
        return self.state == 'finished'
