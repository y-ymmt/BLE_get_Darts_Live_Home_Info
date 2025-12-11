"""データ分析機能"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter

from .models import DartThrow
from .storage import DartDatabase

logger = logging.getLogger(__name__)


class DartAnalyzer:
    """ダーツデータの分析クラス"""

    def __init__(self, database: DartDatabase):
        """
        Args:
            database: データベースインスタンス
        """
        self.db = database

    def get_statistics(
        self,
        device_address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """
        基本統計情報を取得

        Args:
            device_address: デバイスアドレスでフィルタ
            start_time: 開始時刻でフィルタ
            end_time: 終了時刻でフィルタ

        Returns:
            統計情報の辞書
        """
        throws = self.db.get_throws(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        if not throws:
            return {
                'total_throws': 0,
                'total_score': 0,
                'average_score': 0.0,
                'max_score': 0,
                'min_score': 0,
            }

        scores = [t.score for t in throws if t.score is not None]

        return {
            'total_throws': len(throws),
            'total_score': sum(scores),
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
        }

    def get_segment_distribution(
        self,
        device_address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        top_n: int = 10
    ) -> List[Tuple[str, int]]:
        """
        セグメント別の投擲分布を取得

        Args:
            device_address: デバイスアドレスでフィルタ
            start_time: 開始時刻でフィルタ
            end_time: 終了時刻でフィルタ
            top_n: 上位何件を取得するか

        Returns:
            (セグメント名, 投擲回数) のリスト
        """
        throws = self.db.get_throws(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        segment_counter = Counter(t.segment_name for t in throws)
        return segment_counter.most_common(top_n)

    def get_score_distribution(
        self,
        device_address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[int, int]:
        """
        得点別の分布を取得

        Args:
            device_address: デバイスアドレスでフィルタ
            start_time: 開始時刻でフィルタ
            end_time: 終了時刻でフィルタ

        Returns:
            {得点: 回数} の辞書
        """
        throws = self.db.get_throws(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        score_counter = Counter(t.score for t in throws if t.score is not None)
        return dict(sorted(score_counter.items()))

    def get_accuracy_by_target(
        self,
        target_number: int,
        device_address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """
        特定の数字への精度を分析

        Args:
            target_number: 対象の数字 (1-20, 25)
            device_address: デバイスアドレスでフィルタ
            start_time: 開始時刻でフィルタ
            end_time: 終了時刻でフィルタ

        Returns:
            精度情報の辞書
        """
        throws = self.db.get_throws(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        target_throws = [t for t in throws if t.base_number == target_number]
        total_throws = len(throws)

        if total_throws == 0:
            return {
                'target_number': target_number,
                'hit_count': 0,
                'total_throws': 0,
                'accuracy': 0.0,
                'single_count': 0,
                'double_count': 0,
                'triple_count': 0,
            }

        multiplier_counter = Counter(t.multiplier for t in target_throws)

        return {
            'target_number': target_number,
            'hit_count': len(target_throws),
            'total_throws': total_throws,
            'accuracy': len(target_throws) / total_throws * 100,
            'single_count': multiplier_counter.get(1, 0),
            'double_count': multiplier_counter.get(2, 0),
            'triple_count': multiplier_counter.get(3, 0),
        }

    def get_daily_summary(
        self,
        date: Optional[datetime] = None,
        device_address: Optional[str] = None
    ) -> Dict:
        """
        日別のサマリーを取得

        Args:
            date: 対象日 (Noneの場合は今日)
            device_address: デバイスアドレスでフィルタ

        Returns:
            日別サマリーの辞書
        """
        if date is None:
            date = datetime.now()

        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)

        stats = self.get_statistics(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time
        )

        top_segments = self.get_segment_distribution(
            device_address=device_address,
            start_time=start_time,
            end_time=end_time,
            top_n=5
        )

        return {
            'date': date.strftime('%Y-%m-%d'),
            'statistics': stats,
            'top_segments': top_segments,
        }

    def get_recent_throws_summary(
        self,
        limit: int = 10,
        device_address: Optional[str] = None
    ) -> List[Dict]:
        """
        直近の投擲データのサマリーを取得

        Args:
            limit: 取得件数
            device_address: デバイスアドレスでフィルタ

        Returns:
            投擲データのリスト
        """
        throws = self.db.get_throws(limit=limit, device_address=device_address)

        return [
            {
                'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'segment': t.segment_name,
                'score': t.score,
            }
            for t in throws
        ]

    def export_report(
        self,
        device_address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> str:
        """
        レポートをテキスト形式でエクスポート

        Args:
            device_address: デバイスアドレスでフィルタ
            start_time: 開始時刻でフィルタ
            end_time: 終了時刻でフィルタ

        Returns:
            レポートテキスト
        """
        stats = self.get_statistics(device_address, start_time, end_time)
        top_segments = self.get_segment_distribution(device_address, start_time, end_time, top_n=10)

        report_lines = [
            "=" * 50,
            "DARTSLIVE HOME データレポート",
            "=" * 50,
            "",
            "【基本統計】",
            f"  総投擲数: {stats['total_throws']}回",
            f"  合計得点: {stats['total_score']}点",
            f"  平均得点: {stats['average_score']:.2f}点",
            f"  最高得点: {stats['max_score']}点",
            f"  最低得点: {stats['min_score']}点",
            "",
            "【よく狙ったセグメント (Top 10)】",
        ]

        for i, (segment, count) in enumerate(top_segments, 1):
            report_lines.append(f"  {i:2d}. {segment}: {count}回")

        report_lines.append("")
        report_lines.append("=" * 50)

        return "\n".join(report_lines)
