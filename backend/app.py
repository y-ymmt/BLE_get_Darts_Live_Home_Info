"""Flaskアプリケーションのメインファイル"""

import logging
from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os

from backend.ble_manager import BLEManager
from src.core.logger import setup_logger

# ロガー設定（環境変数LOG_LEVELで制御可能、デフォルトはINFO）
log_level = os.environ.get('LOG_LEVEL', 'INFO')
setup_logger(log_level)
logger = logging.getLogger(__name__)
logger.info(f"ログレベル: {log_level}")

# Flaskアプリ作成
app = Flask(__name__, static_folder='../frontend/dist')
# 本番環境では環境変数SECRET_KEYを設定してください
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-dartslive-key')
CORS(app)

# SocketIO初期化
# 本番環境では環境変数CORS_ORIGINSを設定してください（例: "https://yourdomain.com"）
allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode='threading')

# BLEマネージャー初期化
ble_manager = BLEManager()


def init_event_handlers():
    """イベントハンドラーを初期化"""

    def on_throw(throw_data):
        """投擲データをWebSocketで配信"""
        logger.debug(f"投擲データをWebSocketで配信: {throw_data.get('segment_name')}")
        socketio.emit('throw', throw_data)

    def on_player_change(data):
        """プレイヤー交代をWebSocketで配信"""
        logger.info("プレイヤー交代イベントを配信")
        socketio.emit('player_change', data)

    def on_ble_connected(data):
        """BLE接続成功をWebSocketで配信"""
        logger.info(f"BLE接続成功: {data.get('device_name')}")
        socketio.emit('ble_connected', data)

    def on_ble_error(data):
        """BLEエラーをWebSocketで配信"""
        logger.error(f"BLEエラー: {data.get('message')}")
        socketio.emit('ble_error', data)

    # EventBusに購読登録
    ble_manager.event_bus.subscribe('throw', on_throw)
    ble_manager.event_bus.subscribe('player_change', on_player_change)
    ble_manager.event_bus.subscribe('ble_connected', on_ble_connected)
    ble_manager.event_bus.subscribe('ble_error', on_ble_error)

    logger.info("イベントハンドラーを初期化しました")


# イベントハンドラー初期化
init_event_handlers()


# WebSocketイベント
@socketio.on('connect')
def handle_connect():
    """クライアント接続時"""
    logger.info(f"クライアントが接続しました")
    # BLE接続状態を送信
    emit('ble_status', ble_manager.get_status())


@socketio.on('disconnect')
def handle_disconnect():
    """クライアント切断時"""
    logger.info(f"クライアントが切断しました")


@socketio.on('request_status')
def handle_request_status():
    """ステータスリクエスト"""
    emit('ble_status', ble_manager.get_status())


# APIブループリント登録
from backend.api.throws import throws_bp
from backend.api.stats import stats_bp
from backend.api.games import games_bp

app.register_blueprint(throws_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(games_bp)

# REST APIルート
@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({'status': 'ok'})


@app.route('/api/ble/status', methods=['GET'])
def ble_status():
    """BLE接続状態"""
    return jsonify(ble_manager.get_status())


# フロントエンドの配信（本番用）
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Reactアプリケーションを配信"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


def start_web_server(host='0.0.0.0', port=5000, debug=False):
    """Webサーバーを起動"""
    logger.info("=" * 60)
    logger.info("DARTSLIVE HOME Webアプリケーション起動中...")
    logger.info("=" * 60)

    # BLE接続をバックグラウンドで開始
    logger.info("BLE接続をバックグラウンドで開始...")
    ble_manager.start_background()

    # Webサーバー起動
    logger.info(f"Webサーバーを起動: http://{host}:{port}")
    # BLE接続との競合を避けるため、デバッグモードでもリローダーは無効化
    # 本番環境ではallow_unsafe_werkzeugを無効化（debugフラグに連動）
    socketio.run(app, host=host, port=port, debug=debug, use_reloader=False, allow_unsafe_werkzeug=debug)


if __name__ == '__main__':
    start_web_server(debug=True)
