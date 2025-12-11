"""セグメントコードのマッピング機能"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SegmentMapper:
    """セグメントコードをダーツボードのセグメント情報にマッピング"""

    def __init__(self):
        """
        セグメントマッピングテーブルを初期化

        注: 実際のマッピングは実機で確認する必要があります
        ここでは一般的なダーツボードのレイアウトに基づいた推定値を使用
        """
        # セグメントコード -> (基本数字, 倍率) のマッピング
        # 倍率: 1=シングル, 2=ダブル, 3=トリプル, 25=ブル(シングル), 50=ブル(ダブル/ブルズアイ)
        self._mapping = self._create_default_mapping()

    def _create_default_mapping(self) -> dict:
        """
        デフォルトのマッピングテーブルを作成

        注: このマッピングは実機（DARTSLIVE HOME）でテストして確認済みです。

        Returns:
            セグメントコード -> (基本数字, 倍率, セグメント名) の辞書
        """
        mapping = {}

        # ダーツボードの数字配置 (時計回り)
        board_numbers = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]

        # ダブルエリア (外側) - 0x14から開始 (実機確認済み)
        code = 0x14
        for num in board_numbers:
            mapping[code] = (num, 2, f"ダブル{num}")
            code += 1

        # トリプルエリア (中間) - 0x28から開始 (実機確認済み)
        code = 0x28
        for num in board_numbers:
            mapping[code] = (num, 3, f"トリプル{num}")
            code += 1

        # ブル - 0x3cと0x3d (実機確認済み)
        mapping[0x3c] = (25, 1, "アウターブル")
        mapping[0x3d] = (25, 2, "インナーブル")

        # シングルエリア (内側) - 0x54が20、0x3e-0x51が1-19 (実機確認済み)
        # シングル20
        mapping[0x54] = (20, 1, "シングル20")

        # シングル1-19 (時計回り順: 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5)
        single_numbers = [1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
        code = 0x3e
        for num in single_numbers:
            mapping[code] = (num, 1, f"シングル{num}")
            code += 1

        return mapping

    def get_segment_info(self, segment_code: int) -> Tuple[Optional[int], Optional[int], str]:
        """
        セグメントコードから詳細情報を取得

        Args:
            segment_code: セグメントコード

        Returns:
            (基本数字, 倍率, セグメント名) のタプル
            マッピングが見つからない場合は (None, None, "不明")
        """
        if segment_code in self._mapping:
            return self._mapping[segment_code]
        else:
            logger.warning(f"未知のセグメントコード: 0x{segment_code:02x}")
            return (None, None, f"不明(0x{segment_code:02x})")

    def get_score(self, segment_code: int) -> Optional[int]:
        """
        セグメントコードから得点を計算

        Args:
            segment_code: セグメントコード

        Returns:
            得点、計算できない場合はNone
        """
        base_number, multiplier, _ = self.get_segment_info(segment_code)

        if base_number is None or multiplier is None:
            return None

        return base_number * multiplier

    def update_mapping(self, segment_code: int, base_number: int,
                      multiplier: int, segment_name: str) -> None:
        """
        マッピングを更新 (実機確認後のキャリブレーション用)

        Args:
            segment_code: セグメントコード
            base_number: 基本数字
            multiplier: 倍率
            segment_name: セグメント名
        """
        self._mapping[segment_code] = (base_number, multiplier, segment_name)
        logger.info(f"マッピングを更新: 0x{segment_code:02x} -> {segment_name}")

    def export_mapping(self) -> dict:
        """
        マッピングテーブルをエクスポート

        Returns:
            マッピングテーブルの辞書
        """
        return {
            f"0x{code:02x}": {
                'base_number': base_number,
                'multiplier': multiplier,
                'segment_name': segment_name
            }
            for code, (base_number, multiplier, segment_name) in self._mapping.items()
        }

    def import_mapping(self, mapping_dict: dict) -> None:
        """
        マッピングテーブルをインポート

        Args:
            mapping_dict: インポートするマッピング辞書
        """
        for code_str, info in mapping_dict.items():
            code = int(code_str, 16) if code_str.startswith('0x') else int(code_str)
            self._mapping[code] = (
                info['base_number'],
                info['multiplier'],
                info['segment_name']
            )
        logger.info(f"{len(mapping_dict)}個のマッピングをインポートしました")
