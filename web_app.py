"""Webアプリケーションのエントリーポイント"""

import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import start_web_server

if __name__ == '__main__':
    start_web_server(host='0.0.0.0', port=5000, debug=True)
