"""データ分析のテスト"""

import pytest
import tempfile
from datetime import datetime
from pathlib import Path

from src.data.models import DartThrow
from src.data.storage import DartDatabase
from src.data.analyzer import DartAnalyzer


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
def analyzer_with_data(temp_db):
    """サンプルデータを含むアナライザーを作成"""
    # サンプルデータを保存
    throws = [
        DartThrow(
            timestamp=datetime.now(),
            segment_code=0x14,
            segment_name="ダブル20",
            base_number=20,
            multiplier=2,
            score=40,
            device_address="AA:BB:CC:DD:EE:FF",
            device_name="DARTSLIVE HOME"
        ),
        DartThrow(
            timestamp=datetime.now(),
            segment_code=0x14,
            segment_name="ダブル20",
            base_number=20,
            multiplier=2,
            score=40,
            device_address="AA:BB:CC:DD:EE:FF",
            device_name="DARTSLIVE HOME"
        ),
        DartThrow(
            timestamp=datetime.now(),
            segment_code=0x01,
            segment_name="シングル1",
            base_number=1,
            multiplier=1,
            score=1,
            device_address="AA:BB:CC:DD:EE:FF",
            device_name="DARTSLIVE HOME"
        ),
        DartThrow(
            timestamp=datetime.now(),
            segment_code=0x28,
            segment_name="トリプル20",
            base_number=20,
            multiplier=3,
            score=60,
            device_address="AA:BB:CC:DD:EE:FF",
            device_name="DARTSLIVE HOME"
        ),
    ]

    for throw in throws:
        temp_db.save_throw(throw)

    return DartAnalyzer(temp_db)


class TestDartAnalyzer:
    """DartAnalyzerクラスのテスト"""

    def test_get_statistics(self, analyzer_with_data):
        """基本統計情報を取得"""
        stats = analyzer_with_data.get_statistics()

        assert stats['total_throws'] == 4
        assert stats['total_score'] == 141  # 40 + 40 + 1 + 60
        assert stats['average_score'] == pytest.approx(35.25)
        assert stats['max_score'] == 60
        assert stats['min_score'] == 1

    def test_get_statistics_empty_db(self, temp_db):
        """空のデータベースで統計情報を取得"""
        analyzer = DartAnalyzer(temp_db)
        stats = analyzer.get_statistics()

        assert stats['total_throws'] == 0
        assert stats['total_score'] == 0
        assert stats['average_score'] == 0.0

    def test_get_segment_distribution(self, analyzer_with_data):
        """セグメント別の分布を取得"""
        distribution = analyzer_with_data.get_segment_distribution(top_n=5)

        assert len(distribution) > 0
        # ダブル20が最も多い (2回)
        assert distribution[0][0] == "ダブル20"
        assert distribution[0][1] == 2

    def test_get_score_distribution(self, analyzer_with_data):
        """得点別の分布を取得"""
        score_dist = analyzer_with_data.get_score_distribution()

        assert isinstance(score_dist, dict)
        assert score_dist[40] == 2  # 40点が2回
        assert score_dist[1] == 1   # 1点が1回
        assert score_dist[60] == 1  # 60点が1回

    def test_get_accuracy_by_target(self, analyzer_with_data):
        """特定の数字への精度を分析"""
        accuracy = analyzer_with_data.get_accuracy_by_target(20)

        assert accuracy['target_number'] == 20
        assert accuracy['hit_count'] == 3  # ダブル20×2 + トリプル20×1
        assert accuracy['total_throws'] == 4
        assert accuracy['accuracy'] == pytest.approx(75.0)
        assert accuracy['double_count'] == 2
        assert accuracy['triple_count'] == 1

    def test_get_accuracy_by_target_no_hits(self, analyzer_with_data):
        """ヒットなしの場合の精度分析"""
        accuracy = analyzer_with_data.get_accuracy_by_target(19)

        assert accuracy['hit_count'] == 0
        assert accuracy['accuracy'] == 0.0

    def test_get_recent_throws_summary(self, analyzer_with_data):
        """直近の投擲サマリーを取得"""
        recent = analyzer_with_data.get_recent_throws_summary(limit=3)

        assert len(recent) == 3
        assert all('timestamp' in throw for throw in recent)
        assert all('segment' in throw for throw in recent)
        assert all('score' in throw for throw in recent)

    def test_export_report(self, analyzer_with_data):
        """レポートをエクスポート"""
        report = analyzer_with_data.export_report()

        assert isinstance(report, str)
        assert "DARTSLIVE HOME データレポート" in report
        assert "総投擲数: 4回" in report
        assert "合計得点: 141点" in report
        assert "ダブル20" in report
