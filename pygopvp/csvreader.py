import csv
import glob
import os

from .model import Move, Pokemon


class CustomDialect(csv.Dialect):
    """Describe the properties of Calcy-IV generated CSV files."""

    delimiter = ","
    skipinitialspace = False
    lineterminator = "\n"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL


def find_export(folder="data"):
    files = glob.glob(os.path.join(folder, "history_*.csv"))
    files = sorted(files, reverse=True)
    if files:
        return files[0]
    else:
        raise FileNotFoundError("No history_*.csv file found in {}".format(folder))


def read_export(csvfile=None):
    csvfile = csvfile or find_export()
    pokemons = []
    with open(csvfile, newline="", encoding="utf8") as csvfile:
        calcy_reader = csv.DictReader(csvfile, dialect=CustomDialect())
        for row in calcy_reader:
            if row["Ancestor?"] == "1":
                continue
            pokemons.append(
                Pokemon.from_name(
                    row["Name"],
                    float(row["Level"]),
                    [
                        int(float(row["ØATT IV"])),
                        int(float(row["ØDEF IV"])),
                        int(float(row["ØHP IV"])),
                    ],
                )
            )
            if row["Fast move"].strip(" -"):
                pokemons[-1].fast = Move.fast_from_name(row["Fast move"])
            if row["Special move"].strip(" -"):
                pokemons[-1].charged = [Move.charged_from_name(row["Special move"])]
                if row["Special move 2"].strip(" -"):
                    pokemons[-1].charged.append(Move.charged_from_name(row["Special move 2"]))
            if pokemons[-1].cp != int(row["CP"]):
                print(row)
    return pokemons
