"""データモデルのテスト"""

import pytest
from datetime import datetime

from src.data.models import DartThrow, GameSession


class TestDartThrow:
    """DartThrowモデルのテスト"""

    def test_create_dart_throw(self):
        """DartThrowインスタンスを作成"""
        throw = DartThrow(
            segment_code=0x14,
            segment_name="ダブル20",
            base_number=20,
            multiplier=2,
            score=40,
            device_address="AA:BB:CC:DD:EE:FF",
            device_name="DARTSLIVE HOME"
        )

        assert throw.segment_code == 0x14
        assert throw.segment_name == "ダブル20"
        assert throw.base_number == 20
        assert throw.multiplier == 2
        assert throw.score == 40
        assert throw.device_address == "AA:BB:CC:DD:EE:FF"
        assert throw.device_name == "DARTSLIVE HOME"
        assert isinstance(throw.timestamp, datetime)

    def test_dart_throw_auto_timestamp(self):
        """タイムスタンプが自動設定される"""
        throw = DartThrow(
            segment_code=0x01,
            segment_name="シングル1",
            score=1,
            device_address="AA:BB:CC:DD:EE:FF"
        )

        assert throw.timestamp is not None
        assert isinstance(throw.timestamp, datetime)

    def test_to_dict(self):
        """辞書形式に変換"""
        throw = DartThrow(
            segment_code=0x14,
            segment_name="ダブル20",
            base_number=20,
            multiplier=2,
            score=40,
            device_address="AA:BB:CC:DD:EE:FF",
            device_name="DARTSLIVE HOME"
        )

        throw_dict = throw.to_dict()

        assert isinstance(throw_dict, dict)
        assert throw_dict['segment_code'] == 0x14
        assert throw_dict['segment_name'] == "ダブル20"
        assert throw_dict['score'] == 40
        assert 'timestamp' in throw_dict

    def test_from_dict(self):
        """辞書からインスタンスを生成"""
        data = {
            'id': 1,
            'timestamp': datetime.now().isoformat(),
            'segment_code': 0x14,
            'segment_name': "ダブル20",
            'base_number': 20,
            'multiplier': 2,
            'score': 40,
            'device_address': "AA:BB:CC:DD:EE:FF",
            'device_name': "DARTSLIVE HOME"
        }

        throw = DartThrow.from_dict(data)

        assert throw.id == 1
        assert isinstance(throw.timestamp, datetime)
        assert throw.segment_code == 0x14
        assert throw.score == 40


class TestGameSession:
    """GameSessionモデルのテスト"""

    def test_create_game_session(self):
        """GameSessionインスタンスを作成"""
        session = GameSession(
            device_address="AA:BB:CC:DD:EE:FF",
            throw_count=10,
            total_score=350
        )

        assert session.device_address == "AA:BB:CC:DD:EE:FF"
        assert session.throw_count == 10
        assert session.total_score == 350
        assert isinstance(session.start_time, datetime)
        assert session.end_time is None

    def test_game_session_auto_start_time(self):
        """開始時刻が自動設定される"""
        session = GameSession(device_address="AA:BB:CC:DD:EE:FF")

        assert session.start_time is not None
        assert isinstance(session.start_time, datetime)

    def test_to_dict(self):
        """辞書形式に変換"""
        session = GameSession(
            device_address="AA:BB:CC:DD:EE:FF",
            throw_count=5,
            total_score=150
        )

        session_dict = session.to_dict()

        assert isinstance(session_dict, dict)
        assert session_dict['device_address'] == "AA:BB:CC:DD:EE:FF"
        assert session_dict['throw_count'] == 5
        assert session_dict['total_score'] == 150
        assert 'start_time' in session_dict
