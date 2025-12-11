"""統計API"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime

from src.data.storage import DartDatabase
from src.data.analyzer import DartAnalyzer
from src.core.config import AppConfig

logger = logging.getLogger(__name__)

stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')

# データベースとアナライザー初期化
config = AppConfig()
db = DartDatabase(config.db_path)
analyzer = DartAnalyzer(db)


@stats_bp.route('', methods=['GET'])
def get_statistics():
    """
    基本統計情報を取得

    Query Parameters:
        device_address (str): デバイスアドレスでフィルタ
        start_time (str): 開始時刻でフィルタ (ISO形式)
        end_time (str): 終了時刻でフィルタ (ISO形式)
    """
    try:
        device_address = request.args.get('device_address')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
        end_time = datetime.fromisoformat(end_time_str) if end_time_str else None

        stats = analyzer.get_statistics(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        return jsonify({
            'success': True,
            'statistics': stats
        })

    except Exception as e:
        logger.error(f"統計情報取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stats_bp.route('/segments', methods=['GET'])
def get_segment_distribution():
    """
    セグメント分布を取得

    Query Parameters:
        top_n (int): 上位何件を取得するか（デフォルト: 10）
        device_address (str): デバイスアドレスでフィルタ
        start_time (str): 開始時刻でフィルタ
        end_time (str): 終了時刻でフィルタ
    """
    try:
        top_n = request.args.get('top_n', 10, type=int)
        device_address = request.args.get('device_address')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
        end_time = datetime.fromisoformat(end_time_str) if end_time_str else None

        distribution = analyzer.get_segment_distribution(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time,
            top_n=top_n
        )

        # タプルのリストを辞書のリストに変換
        distribution_data = [
            {'segment_name': segment, 'count': count}
            for segment, count in distribution
        ]

        return jsonify({
            'success': True,
            'distribution': distribution_data
        })

    except Exception as e:
        logger.error(f"セグメント分布取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stats_bp.route('/scores', methods=['GET'])
def get_score_distribution():
    """得点分布を取得"""
    try:
        device_address = request.args.get('device_address')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
        end_time = datetime.fromisoformat(end_time_str) if end_time_str else None

        distribution = analyzer.get_score_distribution(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        # 辞書を配列形式に変換
        distribution_data = [
            {'score': score, 'count': count}
            for score, count in distribution.items()
        ]

        return jsonify({
            'success': True,
            'distribution': distribution_data
        })

    except Exception as e:
        logger.error(f"得点分布取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stats_bp.route('/daily', methods=['GET'])
def get_daily_summary():
    """日別サマリーを取得"""
    try:
        date_str = request.args.get('date')
        device_address = request.args.get('device_address')

        date = datetime.fromisoformat(date_str) if date_str else None

        summary = analyzer.get_daily_summary(
            date=date,
            device_address=device_address
        )

        return jsonify({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        logger.error(f"日別サマリー取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stats_bp.route('/recent', methods=['GET'])
def get_recent_throws():
    """直近の投擲サマリーを取得"""
    try:
        limit = request.args.get('limit', 10, type=int)
        device_address = request.args.get('device_address')

        recent_throws = analyzer.get_recent_throws_summary(
            limit=limit,
            device_address=device_address
        )

        return jsonify({
            'success': True,
            'throws': recent_throws
        })

    except Exception as e:
        logger.error(f"直近投擲取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
