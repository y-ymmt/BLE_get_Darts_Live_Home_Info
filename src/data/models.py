"""データモデル定義"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DartThrow:
    """ダーツの投擲データ"""

    id: Optional[int] = None  # データベースID
    timestamp: Optional[datetime] = None  # 投擲時刻
    segment_code: int = 0  # セグメントコード (生データ)
    segment_name: str = ""  # セグメント名 (例: "ダブル20", "トリプル1")
    base_number: Optional[int] = None  # 基本数字 (1-20, 25)
    multiplier: Optional[int] = None  # 倍率 (1: シングル, 2: ダブル, 3: トリプル)
    score: Optional[int] = None  # 得点
    device_address: str = ""  # デバイスのMACアドレス
    device_name: str = ""  # デバイス名

    def __post_init__(self):
        """初期化後の処理"""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'segment_code': self.segment_code,
            'segment_name': self.segment_name,
            'base_number': self.base_number,
            'multiplier': self.multiplier,
            'score': self.score,
            'device_address': self.device_address,
            'device_name': self.device_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DartThrow':
        """辞書からインスタンスを生成"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class GameSession:
    """ゲームセッション (将来の機能拡張用)"""

    id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    device_address: str = ""
    throw_count: int = 0
    total_score: int = 0

    def __post_init__(self):
        """初期化後の処理"""
        if self.start_time is None:
            self.start_time = datetime.now()

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'device_address': self.device_address,
            'throw_count': self.throw_count,
            'total_score': self.total_score,
        }
