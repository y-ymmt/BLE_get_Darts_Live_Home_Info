"""セグメントマッパーのテスト"""

import pytest
from src.data.mapper import SegmentMapper


class TestSegmentMapper:
    """SegmentMapperクラスのテスト"""

    def test_get_segment_info_valid_code(self):
        """有効なセグメントコードで情報を取得"""
        mapper = SegmentMapper()
        base_number, multiplier, segment_name = mapper.get_segment_info(0x00)

        assert base_number is not None
        assert multiplier is not None
        assert segment_name != ""
        assert "不明" not in segment_name

    def test_get_segment_info_invalid_code(self):
        """無効なセグメントコードで情報を取得"""
        mapper = SegmentMapper()
        base_number, multiplier, segment_name = mapper.get_segment_info(0xFF)

        assert base_number is None
        assert multiplier is None
        assert "不明" in segment_name

    def test_get_score_valid_code(self):
        """有効なセグメントコードで得点を計算"""
        mapper = SegmentMapper()
        # シングル20の場合 (コード0x00と仮定)
        score = mapper.get_score(0x00)

        assert score is not None
        assert score > 0

    def test_get_score_invalid_code(self):
        """無効なセグメントコードで得点を計算"""
        mapper = SegmentMapper()
        score = mapper.get_score(0xFF)

        assert score is None

    def test_update_mapping(self):
        """マッピングを更新"""
        mapper = SegmentMapper()
        test_code = 0xFF

        # マッピングを更新
        mapper.update_mapping(test_code, 20, 3, "テストトリプル20")

        # 更新されたマッピングを確認
        base_number, multiplier, segment_name = mapper.get_segment_info(test_code)
        assert base_number == 20
        assert multiplier == 3
        assert segment_name == "テストトリプル20"

    def test_export_import_mapping(self):
        """マッピングのエクスポートとインポート"""
        mapper1 = SegmentMapper()

        # マッピングをエクスポート
        exported = mapper1.export_mapping()
        assert isinstance(exported, dict)
        assert len(exported) > 0

        # 新しいマッパーにインポート
        mapper2 = SegmentMapper()
        mapper2.import_mapping(exported)

        # 同じマッピングが得られることを確認
        for code_str in exported.keys():
            code = int(code_str, 16)
            info1 = mapper1.get_segment_info(code)
            info2 = mapper2.get_segment_info(code)
            assert info1 == info2
