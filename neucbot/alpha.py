import os
from neucbot import ensdf

ALPHA_LIST_DIR = "./AlphaLists"


def _alphas_from_file_path(file_path):
    file = open(file_path)

    # Parse alphalist files:
    # 1. Only parse lines that have 2+ tab-separated tokens
    # 2. Ignore any lines starting with "#"
    # 3. Return list of lists (where each sublist is a list of floats)
    alphas = [
        [float(token) for token in line.split()]  # Parse each token as float
        for line in file.readlines()  # for each line in file
        if line[0] != "#"
        and len(line.split()) >= 2  # except for lines matching these conditions
    ]

    file.close()

    return alphas


class AlphaList:
    def __init__(self, element, isotope):
        self.element = element
        self.isotope = isotope
        self.file_path = f"{ALPHA_LIST_DIR}/{self.element}{self.isotope}Alphas.dat"
        self.fetch_attempts = 3

    @classmethod
    def from_filepath(cls, file_path):
        return _alphas_from_file_path(file_path)

    def load_or_fetch(self):
        while not os.path.isfile(self.file_path):
            if self.fetch_attempts < 0:
                raise RuntimeError(f"Unable to write alpha file to {self.file_path}")
            self.write()
            self.fetch_attempts -= 1

        return self.load()

    def load(self):
        return _alphas_from_file_path(self.file_path)

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
