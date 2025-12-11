"""ゲームAPI"""

import logging
from flask import Blueprint, jsonify, request
from flask_socketio import emit

from backend.games.state import GameStateManager

logger = logging.getLogger(__name__)

games_bp = Blueprint('games', __name__, url_prefix='/api/games')

# ゲーム状態マネージャー初期化
game_manager = GameStateManager()


@games_bp.route('', methods=['POST'])
def create_game():
    """
    新しいゲームを作成

    Request Body:
        {
            "game_type": "zero_one",
            "player_names": ["Player 1", "Player 2"],
            "settings": {
                "starting_score": 501,
                "finish_type": "double"
            }
        }
    """
    try:
        data = request.get_json()

        game_type = data.get('game_type', 'zero_one')
        player_names = data.get('player_names', [])
        settings = data.get('settings', {})

        # バリデーション
        if not player_names:
            return jsonify({
                'success': False,
                'error': 'プレイヤー名が指定されていません'
            }), 400

        if len(player_names) < 1:
            return jsonify({
                'success': False,
                'error': 'プレイヤーは1人以上必要です'
            }), 400

        # ゲーム作成
        game_id = game_manager.create_game(game_type, player_names, settings)
        game = game_manager.get_game(game_id)

        return jsonify({
            'success': True,
            'game_id': game_id,
            'game_state': game.get_state()
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"ゲーム作成エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@games_bp.route('/<game_id>', methods=['GET'])
def get_game_state(game_id):
    """ゲーム状態を取得"""
    try:
        game = game_manager.get_game(game_id)

        if not game:
            return jsonify({
                'success': False,
                'error': 'ゲームが見つかりません'
            }), 404

        return jsonify({
            'success': True,
            'game_state': game.get_state()
        })

    except Exception as e:
        logger.error(f"ゲーム状態取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@games_bp.route('/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    """ゲームを削除"""
    try:
        success = game_manager.delete_game(game_id)

        if not success:
            return jsonify({
                'success': False,
                'error': 'ゲームが見つかりません'
            }), 404

        return jsonify({
            'success': True,
            'message': 'ゲームを削除しました'
        })

    except Exception as e:
        logger.error(f"ゲーム削除エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@games_bp.route('', methods=['GET'])
def list_games():
    """アクティブなゲーム一覧を取得"""
    try:
        games = game_manager.list_games()

        return jsonify({
            'success': True,
            'games': games,
            'count': len(games)
        })

    except Exception as e:
        logger.error(f"ゲーム一覧取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@games_bp.route('/<game_id>/throw', methods=['POST'])
def process_throw(game_id):
    """
    ゲームに投擲を適用

    Request Body:
        throw_data (投擲データ)
    """
    try:
        throw_data = request.get_json()

        result = game_manager.handle_throw_for_game(game_id, throw_data)

        if result is None:
            return jsonify({
                'success': False,
                'error': 'ゲームが見つかりません'
            }), 404

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"投擲処理エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
