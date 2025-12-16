import os
from neucbot import ensdf

ALPHA_LIST_DIR = "./AlphaLists"


class AlphaList:
    def __init__(self, element, isotope):
        self.element = element
        self.isotope = isotope
        self.file_path = f"{ALPHA_LIST_DIR}/{self.element}{self.isotope}Alphas.dat"

    def write(self):
        if os.path.exists(self.file_path):
            print(f"Alpha list file already exists at {self.file_path}")
        else:
            client = ensdf.Client(self.element, self.isotope)
            decay_file_text = client.read_or_fetch_decay_file()
            energyMaps = ensdf.Parser.parse(decay_file_text)
            file = open(self.file_path, "w")

            for energy, probability in energyMaps["alphas"].items():
                file.write(f"{str(energy/1000)}\t{probability}\n")

            file.close()

        return True
