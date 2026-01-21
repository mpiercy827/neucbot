import pytest

from neucbot import elements, material


class TestComposition:
    def test_from_file_isotopes_specified(self):
        comp = material.Composition.from_file("./tests/test_material/WithIsotopes.dat")

        assert len(comp.materials) == 3
        assert comp.fractions == {
            "C": 0.5,
            "O": 0.25,
            "H": 0.25,
        }

    def test_from_file_no_isotopes_specified(self):
        comp = material.Composition.from_file("./tests/test_material/NoIsotopes.dat")

        assert len(comp.materials) == 7
        assert comp.fractions == {
            "C": 0.5,
            "O": 0.25,
            "H": 0.25,
        }

    def test_normalize(self):
        comp = material.Composition()

        comp.add(material.Isotope(elements.Element("C"), 12, 0.4))
        comp.add(material.Isotope(elements.Element("H"), 12, 0.2))
        comp.add(material.Isotope(elements.Element("O"), 12, 0.2))

        comp.normalize()

        assert comp.fractions.get("C") == 0.5
        assert comp.fractions.get("H") == 0.25
        assert comp.fractions.get("O") == 0.25

    def test_stopping_power_single_element_material(self):
        comp = material.Composition.from_file("./tests/test_material/CarbonOnly.dat")
        assert len(comp.materials) == 1
        assert comp.fractions == {"C": 1.0}

        # Since this material is 100% carbon 12, stopping power is just computed
        # as the stopping power of carbon at this energy level
        assert comp.stopping_power(11.0) == 486.0835

    def test_stopping_power_multi_element_material(self):
        comp = material.Composition.from_file("./tests/test_material/WithIsotopes.dat")

        assert len(comp.materials) == 3
        assert comp.fractions == {
            "C": 0.5,
            "O": 0.25,
            "H": 0.25,
        }

        # 50% stopping power of C = 0.5 * 486.0835
        # 25% stopping power of H = 0.25 * 1371.204
        # 25% stopping power of O = 0.25 * 462.8758
        assert comp.stopping_power(11.0) == 701.5617


class TestStoppingPowerList:
    def test_load_file(self):
        stop_list = material.StoppingPowerList("C")
        stop_list.load_file()

        assert len(stop_list.stopping_powers.items()) == 79
        assert stop_list.stopping_powers[0.01] == 511.72

    def test_find_energy(self):
        stop_list = material.StoppingPowerList("C")
        stop_list.load_file()

        # Energy less than lowest energy in the list
        assert stop_list.find_energy(0.001) == 511.72

        # Energies in between two entries in the list
        assert stop_list.find_energy(0.525) == 1923.768
        assert stop_list.find_energy(4.25) == 942.3363

        # Energy higher than the highest in the list
        assert stop_list.find_energy(11.0) == 486.0835
