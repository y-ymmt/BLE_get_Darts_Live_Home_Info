"""データストレージ機能 (SQLite)"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager

from .models import DartThrow, GameSession

logger = logging.getLogger(__name__)


class DartDatabase:
    """ダーツデータを管理するデータベースクラス"""

    def __init__(self, db_path: str = "data/dartslive.db"):
        """
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    @contextmanager
    def _get_connection(self):
        """データベース接続のコンテキストマネージャー"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"データベースエラー: {e}")
            raise
        finally:
            conn.close()

    def _initialize_database(self) -> None:
        """データベースとテーブルを初期化"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # dart_throwsテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dart_throws (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    segment_code INTEGER NOT NULL,
                    segment_name TEXT NOT NULL,
                    base_number INTEGER,
                    multiplier INTEGER,
                    score INTEGER,
                    device_address TEXT NOT NULL,
                    device_name TEXT
                )
            """)

            # インデックス作成
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON dart_throws(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_device
                ON dart_throws(device_address)
            """)

            # game_sessionsテーブル (将来の機能拡張用)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    device_address TEXT NOT NULL,
                    throw_count INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0
                )
            """)

            logger.info(f"データベースを初期化しました: {self.db_path}")

    def save_throw(self, throw: DartThrow) -> int:
        """
        投擲データを保存

        Args:
            throw: 投擲データ

        Returns:
            保存されたレコードのID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dart_throws (
                    timestamp, segment_code, segment_name,
                    base_number, multiplier, score,
                    device_address, device_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                throw.timestamp.isoformat(),
                throw.segment_code,
                throw.segment_name,
                throw.base_number,
                throw.multiplier,
                throw.score,
                throw.device_address,
                throw.device_name
            ))

            throw_id = cursor.lastrowid
            logger.debug(f"投擲データを保存: ID={throw_id}, {throw.segment_name}")
            return throw_id

    def get_throws(
        self,
        limit: Optional[int] = None,
        device_address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[DartThrow]:
        """
        投擲データを取得

        Args:
            limit: 取得件数の上限
            device_address: デバイスアドレスでフィルタ
            start_time: 開始時刻でフィルタ
            end_time: 終了時刻でフィルタ

        Returns:
            投擲データのリスト
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM dart_throws WHERE 1=1"
            params = []

            if device_address:
                query += " AND device_address = ?"
                params.append(device_address)

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            query += " ORDER BY timestamp DESC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            throws = []
            for row in rows:
                throw = DartThrow(
                    id=row['id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    segment_code=row['segment_code'],
                    segment_name=row['segment_name'],
                    base_number=row['base_number'],
                    multiplier=row['multiplier'],
                    score=row['score'],
                    device_address=row['device_address'],
                    device_name=row['device_name']
                )
                throws.append(throw)

            return throws

    def get_throw_count(
        self,
        device_address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """
        投擲数を取得

        Args:
            device_address: デバイスアドレスでフィルタ
            start_time: 開始時刻でフィルタ
            end_time: 終了時刻でフィルタ

        Returns:
            投擲数
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT COUNT(*) as count FROM dart_throws WHERE 1=1"
            params = []

            if device_address:
                query += " AND device_address = ?"
                params.append(device_address)

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    def delete_old_throws(self, days: int = 30) -> int:
        """
        古い投擲データを削除

        Args:
            days: 何日前より古いデータを削除するか

        Returns:
            削除した件数
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cutoff_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=days)

            cursor.execute("""
                DELETE FROM dart_throws
                WHERE timestamp < ?
            """, (cutoff_date.isoformat(),))

            deleted_count = cursor.rowcount
            logger.info(f"{deleted_count}件の古いデータを削除しました")
            return deleted_count
