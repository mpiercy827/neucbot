from bisect import bisect

from neucbot import elements

N_A = 6.0221409e23


class Isotope:
    def __init__(self, element, mass_number, fraction):
        self.element = element
        self.mass_number = int(mass_number)
        self.fraction = float(fraction)

    def material_term(self):
        return (N_A * self.fraction) / self.mass_number


class StoppingPowerList:
    def __init__(self, element_symbol):
        self.element_symbol = element_symbol
        self.stopping_powers = {}

    def load_file(self):
        file_path = f"./Data/StoppingPowers/{self.element_symbol.lower()}.dat"
        file = open(file_path)

        for data in [
            line.split() for line in file.readlines() if not line.startswith("#")
        ]:
            energy = float(data[0])
            units = str(data[1])
            stopping_power = float(data[2]) + float(data[3])

            if units == "keV":
                energy /= 1000

            self.stopping_powers[energy] = stopping_power

    # Use binary search to find energy in log(N) time
    def find_energy(self, energy):
        energy_intervals = list(self.stopping_powers.keys())
        min_energy = energy_intervals[0]
        max_energy = energy_intervals[-1]

        if energy < min_energy:
            return self.stopping_powers[min_energy]
        elif energy > max_energy:
            return self.stopping_powers[max_energy]

        interval_index = bisect(energy_intervals, energy) - 1
        interval_start = energy_intervals[interval_index]

        return self.stopping_powers[interval_start]


class Composition:
    @classmethod
    def from_file(cls, file_path):
        file = open(file_path)

        composition = cls()

        for material in [
            line.split() for line in file.readlines() if not line.startswith("#")
        ]:
            if len(material) < 3:
                continue

            element = elements.Element(material[0])
            mass_number = int(material[1])
            fraction = float(material[2])

            # If a single mass number isn't specified, use all isotopes
            # along with their natural abundances
            if mass_number == 0:
                for isotope in element.isotopes():
                    composition.add(
                        Isotope(
                            element,
                            isotope,
                            fraction * element.abundance(isotope) / 100.0,
                        )
                    )

            # Otherwise, if a single mass number is provided,
            # use the fraction provided
            else:
                composition.add(
                    Isotope(
                        element,
                        mass_number,
                        fraction / 100.0,
                    )
                )

        composition.normalize()

        return composition

    def __init__(self):
        self.materials = []
        self.fractions = {}

    def normalize(self):
        norm = 0

        for material in self.materials:
            norm += material.fraction

        for material in self.materials:
            material.fraction /= norm

            # Computes the fraction of this element in the overall material,
            # grouping isotopes with the same Z
            symbol = material.element.symbol
            self.fractions[symbol] = self.fractions.get(symbol, 0) + material.fraction

    def empty(self):
        return len(self.materials) == 0

    def add(self, material):
        self.materials.append(material)

    # Expects an alpha energy in units of MeV
    # Need to read/load elements from Data/StoppingPowers/*.dat
    # Use binary search to speed up search
    def stopping_power(self, e_alpha):
        total_stopping_power = 0

        for element, fraction in self.fractions.items():
            stop_power_list = StoppingPowerList(element)
            stop_power_list.load_file()
            element_stop_power = stop_power_list.find_energy(e_alpha)

            total_stopping_power += element_stop_power * fraction

        return total_stopping_power
