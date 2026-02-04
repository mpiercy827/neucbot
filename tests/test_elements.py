import pytest

from neucbot import elements


class TestElements:
    def test_isotopes(self):
        hydrogen = elements.Element("H")
        assert hydrogen.isotopes() == ["1", "2"]

        carbon = elements.Element("C")
        assert carbon.isotopes() == ["12", "13"]

        germanium = elements.Element("Ge")
        assert germanium.isotopes() == ["70", "72", "73", "74", "76"]

    def test_abundance(self):
        hydrogen = elements.Element("H")
        assert hydrogen.abundance("1") == pytest.approx(0.99985)
        assert hydrogen.abundance("2") == pytest.approx(0.00015)

        carbon = elements.Element("C")
        assert carbon.abundance("12") == pytest.approx(0.9890)
        assert carbon.abundance("13") == pytest.approx(0.0110)
