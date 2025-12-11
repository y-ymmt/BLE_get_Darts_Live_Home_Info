"""ゲーム状態管理"""

import logging
import threading
import uuid
from typing import Dict, Optional, List
from backend.games.zero_one import ZeroOneGame
from backend.games.base import Player

logger = logging.getLogger(__name__)


class GameStateManager:
    """アクティブなゲームの状態を管理"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.active_games: Dict[str, ZeroOneGame] = {}

    def create_game(
        self,
        game_type: str,
        player_names: List[str],
        settings: dict
    ) -> str:
        """
        新しいゲームを作成

        Args:
            game_type: ゲームタイプ（現在は'zero_one'のみ）
            player_names: プレイヤー名のリスト
            settings: ゲーム設定

        Returns:
            ゲームID
        """
        game_id = str(uuid.uuid4())

        # プレイヤー作成
        players = [
            Player(player_id=idx, name=name, order=idx)
            for idx, name in enumerate(player_names)
        ]

        # ゲームインスタンス作成
        if game_type == 'zero_one':
            game = ZeroOneGame(
                game_id=game_id,
                players=players,
                starting_score=settings.get('starting_score', 501),
                finish_type=settings.get('finish_type', 'double')
            )
        else:
            raise ValueError(f"未対応のゲームタイプ: {game_type}")

        self.active_games[game_id] = game
        logger.info(f"ゲーム作成: {game_id}, タイプ: {game_type}, プレイヤー数: {len(players)}")

        return game_id

    def get_game(self, game_id: str) -> Optional[ZeroOneGame]:
        """ゲームを取得"""
        return self.active_games.get(game_id)

    def delete_game(self, game_id: str) -> bool:
        """ゲームを削除"""
        if game_id in self.active_games:
            del self.active_games[game_id]
            logger.info(f"ゲーム削除: {game_id}")
            return True
        return False

    def list_games(self) -> List[dict]:
        """アクティブなゲーム一覧を取得"""
        return [
            {
                'game_id': game_id,
                'game_type': 'zero_one',
                'state': game.state,
                'player_count': len(game.players),
                'created_at': game.created_at.isoformat()
            }
            for game_id, game in self.active_games.items()
        ]

    def handle_throw_for_game(self, game_id: str, throw_data: dict) -> Optional[Dict]:
        """
        ゲームに投擲データを適用

        Args:
            game_id: ゲームID
            throw_data: 投擲データ

        Returns:
            処理結果（ゲームが見つからない場合はNone）
        """
        game = self.get_game(game_id)
        if not game:
            return None

        return game.handle_throw(throw_data)
