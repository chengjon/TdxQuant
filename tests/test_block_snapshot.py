import unittest

from tdxquant.block_snapshot import BlockSnapshotRequest, normalize_block_snapshot
from tdxquant.models import ErrorCode


class BlockSnapshotTests(unittest.TestCase):
    def test_preserves_order_and_deduplicates(self) -> None:
        result = normalize_block_snapshot(
            BlockSnapshotRequest(
                block_code="ZXG",
                sector_name="自选股",
                member_codes=["600519", "000001", "600519", "300750", "000001"],
            )
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, ErrorCode.OK)
        self.assertEqual(
            result.data["snapshot"],
            {
                "block_code": "ZXG",
                "symbols": ["600519.SH", "000001.SZ", "300750.SZ"],
                "symbol_count": 3,
                "source": "tongdaxin.custom_sector",
                "source_metadata": {
                    "sector_name": "自选股",
                    "raw_member_count": 5,
                    "duplicate_count": 2,
                },
            },
        )
        self.assertEqual(
            result.data["snapshot"]["source_metadata"],
            {
                "sector_name": "自选股",
                "raw_member_count": 5,
                "duplicate_count": 2,
            },
        )
        self.assertEqual(result.warnings, ["Deduplicated 2 repeated members in block ZXG"])

    def test_empty_block_success(self) -> None:
        result = normalize_block_snapshot(
            BlockSnapshotRequest(
                block_code="ZXG",
                sector_name="空板块",
                member_codes=[],
            )
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, ErrorCode.OK)
        self.assertEqual(
            result.data["snapshot"],
            {
                "block_code": "ZXG",
                "symbols": [],
                "symbol_count": 0,
                "source": "tongdaxin.custom_sector",
                "source_metadata": {
                    "sector_name": "空板块",
                    "raw_member_count": 0,
                    "duplicate_count": 0,
                },
            },
        )
        self.assertEqual(
            result.data["snapshot"]["source_metadata"],
            {
                "sector_name": "空板块",
                "raw_member_count": 0,
                "duplicate_count": 0,
            },
        )
        self.assertEqual(result.warnings, [])

    def test_invalid_member_failure(self) -> None:
        result = normalize_block_snapshot(
            BlockSnapshotRequest(
                block_code="ZXG",
                sector_name="坏数据",
                member_codes=["600519", "ABC123"],
            )
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("ABC123", result.message)

    def test_preserves_explicit_exchange_suffix_and_bj_symbols(self) -> None:
        result = normalize_block_snapshot(
            BlockSnapshotRequest(
                block_code="ZXG",
                sector_name="北交所板块",
                member_codes=["430001.BJ", "920001.BJ", "430001.BJ"],
            )
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["snapshot"]["symbols"],
            ["430001.BJ", "920001.BJ"],
        )
        self.assertEqual(result.data["snapshot"]["source_metadata"]["duplicate_count"], 1)
        self.assertEqual(result.warnings, ["Deduplicated 1 repeated members in block ZXG"])

    def test_infers_bj_symbol_for_supported_numeric_prefixes(self) -> None:
        result = normalize_block_snapshot(
            BlockSnapshotRequest(
                block_code="ZXG",
                sector_name="北交所板块",
                member_codes=["430001", "920001"],
            )
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data["snapshot"]["symbols"], ["430001.BJ", "920001.BJ"])

    def test_blank_block_code_failure(self) -> None:
        result = normalize_block_snapshot(
            BlockSnapshotRequest(
                block_code="  ",
                sector_name="自选股",
                member_codes=["600519"],
            )
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "block snapshot requires a non-blank block_code")


if __name__ == "__main__":
    unittest.main()
