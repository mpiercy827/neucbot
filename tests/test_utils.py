import pytest

from neucbot import utils


class TestUtils:
    def test_format_float_zero(self):
        assert utils.format_float(0) == "0.0"
        assert utils.format_float(0.0) == "0.0"
        assert utils.format_float(0.0e0) == "0.0"

    def test_format_float_nonzero(self):
        assert utils.format_float(0.123456789) == "1.234568e-01"
        assert utils.format_float(1.987654321e10) == "1.987654e+10"

    def test_format_float_allows_precision(self):
        assert utils.format_float(0.123456789, 3) == "1.235e-01"
        assert utils.format_float(12345678991, 9) == "1.234567899e+10"
