"""投擲データAPI"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime

from src.data.storage import DartDatabase
from src.core.config import AppConfig

logger = logging.getLogger(__name__)

throws_bp = Blueprint('throws', __name__, url_prefix='/api/throws')

# データベース初期化
config = AppConfig()
db = DartDatabase(config.db_path)


@throws_bp.route('', methods=['GET'])
def get_throws():
    """
    投擲データ一覧を取得

    Query Parameters:
        limit (int): 取得件数（デフォルト: 100）
        device_address (str): デバイスアドレスでフィルタ
        start_time (str): 開始時刻でフィルタ (ISO形式)
        end_time (str): 終了時刻でフィルタ (ISO形式)
    """
    try:
        # クエリパラメータ取得
        limit = request.args.get('limit', 100, type=int)
        device_address = request.args.get('device_address')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        # 日時パース
        start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
        end_time = datetime.fromisoformat(end_time_str) if end_time_str else None

        # データベースから取得
        throws = db.get_throws(
            limit=limit,
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        # 辞書形式に変換
        throws_data = [throw.to_dict() for throw in throws]

        return jsonify({
            'success': True,
            'count': len(throws_data),
            'throws': throws_data
        })

    except Exception as e:
        logger.error(f"投擲データ取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@throws_bp.route('/count', methods=['GET'])
def get_throw_count():
    """投擲数を取得"""
    try:
        device_address = request.args.get('device_address')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
        end_time = datetime.fromisoformat(end_time_str) if end_time_str else None

        count = db.get_throw_count(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        return jsonify({
            'success': True,
            'count': count
        })

    except Exception as e:
        logger.error(f"投擲数取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
