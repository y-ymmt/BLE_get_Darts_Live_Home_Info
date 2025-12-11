"""ゼロワンゲーム実装"""

import logging
from typing import List, Dict
from backend.games.base import BaseGame, Player

logger = logging.getLogger(__name__)


class ZeroOneGame(BaseGame):
    """ゼロワンゲーム（301/501/701等）"""

    VALID_STARTING_SCORES = [301, 501, 701, 901, 1101, 1501]
    VALID_FINISH_TYPES = ['straight', 'double', 'master']

    def __init__(
        self,
        game_id: str,
        players: List[Player],
        starting_score: int = 501,
        finish_type: str = 'double'
    ):
        """
        Args:
            game_id: ゲームID
            players: プレイヤーリスト
            starting_score: 開始点数（301/501/701など）
            finish_type: 終了条件
                - 'straight': 任意のセグメントで終了可能
                - 'double': ダブルで終了（ダブルアウト）
                - 'master': ダブルまたはトリプルで終了（マスターアウト）
        """
        settings = {
            'starting_score': starting_score,
            'finish_type': finish_type
        }
        super().__init__(game_id, players, settings)

        # バリデーション
        if starting_score not in self.VALID_STARTING_SCORES:
            raise ValueError(f"無効な開始点数: {starting_score}. 有効な値: {self.VALID_STARTING_SCORES}")

        if finish_type not in self.VALID_FINISH_TYPES:
            raise ValueError(f"無効な終了条件: {finish_type}. 有効な値: {self.VALID_FINISH_TYPES}")

        self.starting_score = starting_score
        self.finish_type = finish_type

        # 各プレイヤーの現在スコアを初期化
        self.scores = {player.id: starting_score for player in players}

        # ラウンド管理
        self.round_count = 1
        self.current_round_throws: List[dict] = []
        self.max_throws_per_round = 3

        # ゲーム履歴
        self.history: List[dict] = []

    def handle_throw(self, throw_data: dict) -> Dict:
        """
        投擲を処理

        Args:
            throw_data: 投擲データ（segment_code, segment_name, score, multiplier等）

        Returns:
            処理結果
        """
        if self.state == 'finished':
            return {
                'type': 'error',
                'message': 'ゲームは既に終了しています'
            }

        if self.state == 'waiting':
            self.state = 'playing'

        current_player = self.get_current_player()
        current_score = self.scores[current_player.id]

        # プレイヤー交代ボタン（0x54）の処理
        if throw_data.get('segment_code') == 0x54:
            logger.info(f"プレイヤー交代: {current_player.name}")
            self.current_round_throws.clear()
            next_player = self.next_player()

            return {
                'type': 'player_changed',
                'current_player': current_player.to_dict(),
                'next_player': next_player.to_dict(),
                'game_state': self.get_state()
            }

        # 投擲を記録
        self.current_round_throws.append(throw_data)

        score = throw_data.get('score', 0)
        new_score = current_score - score

        # バスト判定
        if new_score < 0:
            logger.info(f"バースト! {current_player.name}: {current_score} - {score} = {new_score}")
            result = self._handle_bust(current_player, score)
            self._complete_round()
            return result

        # 勝利判定
        if new_score == 0:
            if self._is_valid_finish(throw_data):
                logger.info(f"勝利! {current_player.name}")
                return self._handle_win(current_player, score)
            else:
                logger.info(f"無効なフィニッシュ! {current_player.name} (finish_type: {self.finish_type})")
                result = self._handle_bust(current_player, score)
                self._complete_round()
                return result

        # スコア更新
        self.scores[current_player.id] = new_score
        logger.info(f"投擲: {current_player.name}, {throw_data['segment_name']} ({score}点), 残り: {new_score}")

        # 3投完了でラウンド終了
        if len(self.current_round_throws) >= self.max_throws_per_round:
            return self._complete_round()

        return {
            'type': 'throw_processed',
            'player': current_player.to_dict(),
            'score': score,
            'new_score': new_score,
            'throw': throw_data,
            'round_throws_count': len(self.current_round_throws),
            'game_state': self.get_state()
        }

    def _is_valid_finish(self, throw_data: dict) -> bool:
        """
        フィニッシュが有効かチェック

        Args:
            throw_data: 投擲データ

        Returns:
            有効な場合True
        """
        multiplier = throw_data.get('multiplier', 0)

        if self.finish_type == 'straight':
            return True
        elif self.finish_type == 'double':
            return multiplier == 2
        elif self.finish_type == 'master':
            return multiplier in [2, 3]

        return False

    def _handle_bust(self, player: Player, score: int) -> Dict:
        """
        バースト処理

        Args:
            player: プレイヤー
            score: 投擲した得点

        Returns:
            処理結果
        """
        # スコアを元に戻す（ラウンド開始時のスコア）
        # 履歴からラウンド開始時のスコアを復元
        round_start_score = self.scores[player.id]
        for throw in self.current_round_throws[:-1]:  # 最後の投擲を除く
            round_start_score += throw.get('score', 0)

        self.scores[player.id] = round_start_score

        self.history.append({
            'round': self.round_count,
            'player_id': player.id,
            'player_name': player.name,
            'result': 'bust',
            'throws': self.current_round_throws.copy()
        })

        self.current_round_throws.clear()

        return {
            'type': 'bust',
            'player': player.to_dict(),
            'score_restored': round_start_score,
            'game_state': self.get_state()
        }

    def _handle_win(self, player: Player, score: int) -> Dict:
        """
        勝利処理

        Args:
            player: プレイヤー
            score: 最終投擲の得点

        Returns:
            処理結果
        """
        self.state = 'finished'
        self.winner = player
        self.scores[player.id] = 0

        self.history.append({
            'round': self.round_count,
            'player_id': player.id,
            'player_name': player.name,
            'result': 'win',
            'throws': self.current_round_throws.copy()
        })

        logger.info(f"ゲーム終了！勝者: {player.name}")

        return {
            'type': 'game_finished',
            'winner': player.to_dict(),
            'rounds': self.round_count,
            'game_state': self.get_state()
        }

    def _complete_round(self) -> Dict:
        """ラウンド完了処理"""
        current_player = self.get_current_player()

        # 履歴に記録
        round_score = sum(throw.get('score', 0) for throw in self.current_round_throws)
        self.history.append({
            'round': self.round_count,
            'player_id': current_player.id,
            'player_name': current_player.name,
            'result': 'completed',
            'throws': self.current_round_throws.copy(),
            'round_score': round_score
        })

        self.current_round_throws.clear()
        next_player = self.next_player()

        # 全プレイヤーが1回投げ終わったらラウンドカウント増加
        if self.current_player_index == 0:
            self.round_count += 1

        return {
            'type': 'round_completed',
            'player': current_player.to_dict(),
            'next_player': next_player.to_dict(),
            'round': self.round_count,
            'game_state': self.get_state()
        }

    def get_state(self) -> dict:
        """ゲーム状態を取得"""
        base_state = super().get_state()
        base_state.update({
            'starting_score': self.starting_score,
            'finish_type': self.finish_type,
            'scores': self.scores,
            'round_count': self.round_count,
            'current_round_throws': self.current_round_throws,
            'history': self.history
        })
        return base_state
