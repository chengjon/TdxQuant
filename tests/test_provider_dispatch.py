"""Tests for multi-provider dispatch (DLL → pytdx → tdx-api)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from tdxquant.models import ErrorCode, Result


class TestProviderMode(unittest.TestCase):
    def setUp(self):
        from tdxquant.api.bridge import set_provider_mode
        set_provider_mode(None)

    def tearDown(self):
        from tdxquant.api.bridge import set_provider_mode
        set_provider_mode(None)

    def test_auto_mode_is_default(self):
        from tdxquant.api.bridge import get_provider_mode
        self.assertEqual(get_provider_mode(), "auto")

    def test_set_pytdx_mode(self):
        from tdxquant.api.bridge import set_provider_mode, get_provider_mode
        set_provider_mode("pytdx")
        self.assertEqual(get_provider_mode(), "pytdx")

    def test_set_tdxapi_mode(self):
        from tdxquant.api.bridge import set_provider_mode, get_provider_mode
        set_provider_mode("tdxapi")
        self.assertEqual(get_provider_mode(), "tdxapi")

    def test_set_dll_mode(self):
        from tdxquant.api.bridge import set_provider_mode, get_provider_mode
        set_provider_mode("dll")
        self.assertEqual(get_provider_mode(), "dll")

    def test_invalid_mode_raises(self):
        from tdxquant.api.bridge import set_provider_mode
        with self.assertRaises(ValueError):
            set_provider_mode("invalid")

    def test_reset_to_auto(self):
        from tdxquant.api.bridge import set_provider_mode, get_provider_mode
        set_provider_mode("pytdx")
        set_provider_mode(None)
        self.assertEqual(get_provider_mode(), "auto")


class TestPytdxModeDispatch(unittest.TestCase):
    def setUp(self):
        from tdxquant.api.bridge import set_provider_mode
        set_provider_mode("pytdx")

    def tearDown(self):
        from tdxquant.api.bridge import set_provider_mode
        set_provider_mode(None)

    @patch("tdxquant.api.bridge.run_pytdx_call")
    def test_kline_uses_pytdx(self, mock_pytdx):
        from tdxquant.api.bridge import run_tdx_data_kline
        mock_pytdx.return_value = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": {}})
        run_tdx_data_kline(["600000.SH"], "1d", "20250101", "20251231", 100, "qfq", [], False)
        mock_pytdx.assert_called_once()

    @patch("tdxquant.api.bridge.run_pytdx_call")
    def test_full_tick_uses_pytdx(self, mock_pytdx):
        from tdxquant.api.bridge import run_tdx_full_tick
        mock_pytdx.return_value = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": {}})
        run_tdx_full_tick("600000.SH", [])
        mock_pytdx.assert_called_once()

    @patch("tdxquant.api.bridge.run_pytdx_call")
    def test_stock_list_uses_pytdx(self, mock_pytdx):
        from tdxquant.api.bridge import run_tdx_stock_list
        mock_pytdx.return_value = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": []})
        run_tdx_stock_list(None, 0)
        mock_pytdx.assert_called_once()


class TestTdxapiModeDispatch(unittest.TestCase):
    def setUp(self):
        from tdxquant.api.bridge import set_provider_mode
        set_provider_mode("tdxapi")

    def tearDown(self):
        from tdxquant.api.bridge import set_provider_mode
        set_provider_mode(None)

    @patch("tdxquant.api.bridge.run_tdxapi_call")
    def test_full_tick_uses_tdxapi(self, mock_tdxapi):
        from tdxquant.api.bridge import run_tdx_full_tick
        mock_tdxapi.return_value = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": {}})
        run_tdx_full_tick("600000.SH", [])
        mock_tdxapi.assert_called_once()

    @patch("tdxquant.api.bridge.run_tdxapi_call")
    def test_kline_uses_tdxapi(self, mock_tdxapi):
        from tdxquant.api.bridge import run_tdx_data_kline
        mock_tdxapi.return_value = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": {}})
        run_tdx_data_kline(["600000.SH"], "1d", "20250101", "20251231", 100, "qfq", [], False)
        mock_tdxapi.assert_called_once()

    @patch("tdxquant.api.bridge.is_tdxapi_available", return_value=False)
    def test_tdxapi_unavailable_returns_error(self, _mock_avail):
        from tdxquant.api.bridge import run_tdx_full_tick
        result = run_tdx_full_tick("600000.SH", [])
        self.assertFalse(result.ok)
        self.assertIn("tdx-api provider unavailable", result.message)


class TestAutoModeFallback(unittest.TestCase):
    def setUp(self):
        from tdxquant.api.bridge import set_provider_mode
        set_provider_mode(None)

    def tearDown(self):
        from tdxquant.api.bridge import set_provider_mode
        set_provider_mode(None)

    @patch("tdxquant.api.bridge.IS_WINDOWS", False)
    @patch("tdxquant.api.bridge.is_pytdx_available", return_value=False)
    @patch("tdxquant.api.bridge.is_tdxapi_available", return_value=True)
    @patch("tdxquant.api.bridge.run_tdxapi_call")
    def test_falls_to_tdxapi_when_no_dll_no_pytdx(self, mock_tdxapi, _mock_avail, _mock_pytdx):
        from tdxquant.api.bridge import run_tdx_full_tick
        mock_tdxapi.return_value = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": {"code": "600000.SH"}})
        result = run_tdx_full_tick("600000.SH", [])
        self.assertTrue(result.ok)
        mock_tdxapi.assert_called_once()

    @patch("tdxquant.api.bridge.IS_WINDOWS", False)
    @patch("tdxquant.api.bridge.is_pytdx_available", return_value=False)
    @patch("tdxquant.api.bridge.is_tdxapi_available", return_value=False)
    def test_all_unavailable_returns_error(self, _mock_tdxapi, _mock_pytdx):
        from tdxquant.api.bridge import run_tdx_full_tick
        result = run_tdx_full_tick("600000.SH", [])
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.UNSUPPORTED_PLATFORM)

    @patch("tdxquant.api.bridge.IS_WINDOWS", False)
    @patch("tdxquant.api.bridge.is_pytdx_available", return_value=True)
    @patch("tdxquant.api.bridge.run_pytdx_call")
    def test_pytdx_used_on_linux(self, mock_pytdx, _mock_avail):
        from tdxquant.api.bridge import run_tdx_full_tick
        mock_pytdx.return_value = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": {}})
        result = run_tdx_full_tick("600000.SH", [])
        self.assertTrue(result.ok)
        mock_pytdx.assert_called_once()


class TestTdxapiProvider(unittest.TestCase):
    def test_price_from_li(self):
        from tdxquant.api.provider_tdxapi import _price_from_li
        self.assertEqual(_price_from_li(12500), 12.5)
        self.assertEqual(_price_from_li(0), 0.0)

    def test_strip_code_suffix(self):
        from tdxquant.api.provider_tdxapi import _strip_code_suffix
        self.assertEqual(_strip_code_suffix("600000.SH"), "600000")
        self.assertEqual(_strip_code_suffix("000001.SZ"), "000001")
        self.assertEqual(_strip_code_suffix("600000"), "600000")


class TestPytdxProviderHelpers(unittest.TestCase):
    def test_split_code_sh(self):
        from tdxquant.api.provider_pytdx import split_code
        self.assertEqual(split_code("600000.SH"), (1, "600000"))

    def test_split_code_sz(self):
        from tdxquant.api.provider_pytdx import split_code
        self.assertEqual(split_code("000001.SZ"), (0, "000001"))

    def test_split_code_by_prefix(self):
        from tdxquant.api.provider_pytdx import split_code
        self.assertEqual(split_code("688001.SH"), (1, "688001"))
        self.assertEqual(split_code("300001.SZ"), (0, "300001"))

    def test_split_code_invalid(self):
        from tdxquant.api.provider_pytdx import split_code
        with self.assertRaises(ValueError):
            split_code("INVALID")

    def test_join_code(self):
        from tdxquant.api.provider_pytdx import join_code
        self.assertEqual(join_code(1, "600000"), "600000.SH")
        self.assertEqual(join_code(0, "000001"), "000001.SZ")


if __name__ == "__main__":
    unittest.main()
