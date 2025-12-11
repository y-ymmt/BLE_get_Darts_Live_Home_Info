"""データストレージのテスト"""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.data.models import DartThrow
from src.data.storage import DartDatabase


@pytest.fixture
def temp_db():
    """テスト用の一時データベースを作成"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    db = DartDatabase(db_path)
    yield db

    # クリーンアップ
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_throw():
    """サンプルの投擲データを作成"""
    return DartThrow(
        timestamp=datetime.now(),
        segment_code=0x14,
        segment_name="ダブル20",
        base_number=20,
        multiplier=2,
        score=40,
        device_address="AA:BB:CC:DD:EE:FF",
        device_name="DARTSLIVE HOME"
    )


class TestDartDatabase:
    """DartDatabaseクラスのテスト"""

    def test_save_throw(self, temp_db, sample_throw):
        """投擲データを保存"""
        throw_id = temp_db.save_throw(sample_throw)

        assert throw_id > 0
        assert isinstance(throw_id, int)

    def test_get_throws(self, temp_db, sample_throw):
        """投擲データを取得"""
        # データを保存
        temp_db.save_throw(sample_throw)

        # 取得
        throws = temp_db.get_throws(limit=10)

        assert len(throws) == 1
        assert throws[0].segment_name == "ダブル20"
        assert throws[0].score == 40

    def test_get_throws_with_limit(self, temp_db, sample_throw):
        """リミット付きで投擲データを取得"""
        # 複数のデータを保存
        for i in range(5):
            throw = DartThrow(
                timestamp=datetime.now(),
                segment_code=i,
                segment_name=f"テスト{i}",
                base_number=20,
                multiplier=1,
                score=20,
                device_address="AA:BB:CC:DD:EE:FF",
                device_name="Test"
            )
            temp_db.save_throw(throw)

        # リミット付きで取得
        throws = temp_db.get_throws(limit=3)

        assert len(throws) == 3

    def test_get_throws_filter_by_device(self, temp_db):
        """デバイスアドレスでフィルタして取得"""
        # 異なるデバイスからのデータを保存
        throw1 = DartThrow(
            timestamp=datetime.now(),
            segment_code=0x01,
            segment_name="テスト1",
            score=20,
            device_address="AA:AA:AA:AA:AA:AA",
            device_name="Device1"
        )
        throw2 = DartThrow(
            timestamp=datetime.now(),
            segment_code=0x02,
            segment_name="テスト2",
            score=30,
            device_address="BB:BB:BB:BB:BB:BB",
            device_name="Device2"
        )

        temp_db.save_throw(throw1)
        temp_db.save_throw(throw2)

        # デバイス1のデータのみ取得
        throws = temp_db.get_throws(device_address="AA:AA:AA:AA:AA:AA")

        assert len(throws) == 1
        assert throws[0].device_address == "AA:AA:AA:AA:AA:AA"

    def test_get_throws_filter_by_time(self, temp_db):
        """時刻でフィルタして取得"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # 昨日のデータ
        throw_old = DartThrow(
            timestamp=yesterday,
            segment_code=0x01,
            segment_name="古いデータ",
            score=20,
            device_address="AA:AA:AA:AA:AA:AA",
            device_name="Test"
        )

        # 今日のデータ
        throw_new = DartThrow(
            timestamp=now,
            segment_code=0x02,
            segment_name="新しいデータ",
            score=30,
            device_address="AA:AA:AA:AA:AA:AA",
            device_name="Test"
        )

        temp_db.save_throw(throw_old)
        temp_db.save_throw(throw_new)

        # 今日のデータのみ取得
        throws = temp_db.get_throws(
            start_time=now.replace(hour=0, minute=0, second=0, microsecond=0)
        )

        assert len(throws) == 1
        assert throws[0].segment_name == "新しいデータ"

    def test_get_throw_count(self, temp_db, sample_throw):
        """投擲数を取得"""
        # データを保存
        for i in range(3):
            temp_db.save_throw(sample_throw)

        # カウントを取得
        count = temp_db.get_throw_count()

        assert count == 3

    def test_delete_old_throws(self, temp_db):
        """古いデータを削除"""
        now = datetime.now()
        old_date = now - timedelta(days=31)

        # 古いデータを保存
        throw_old = DartThrow(
            timestamp=old_date,
            segment_code=0x01,
            segment_name="古いデータ",
            score=20,
            device_address="AA:AA:AA:AA:AA:AA",
            device_name="Test"
        )

        # 新しいデータを保存
        throw_new = DartThrow(
            timestamp=now,
            segment_code=0x02,
            segment_name="新しいデータ",
            score=30,
            device_address="AA:AA:AA:AA:AA:AA",
            device_name="Test"
        )

        temp_db.save_throw(throw_old)
        temp_db.save_throw(throw_new)

        # 30日より古いデータを削除
        deleted_count = temp_db.delete_old_throws(days=30)

        assert deleted_count == 1

        # 残っているデータを確認
        remaining = temp_db.get_throws()
        assert len(remaining) == 1
        assert remaining[0].segment_name == "新しいデータ"
