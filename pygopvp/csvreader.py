"""Load export from Calcy-IV"""
import csv
import glob
import os
from typing import List, Optional

from .model import Move, Pokemon

DATA_DIR = "data"


class CustomDialect(csv.Dialect):
    """Describe the properties of Calcy-IV generated CSV files."""

    delimiter = ","
    skipinitialspace = False
    lineterminator = "\n"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL


def find_export(folder=None) -> str:
    """Find most recent history_*.csv file"""
    folder = folder or DATA_DIR
    files = glob.glob(os.path.join(folder, "history_*.csv"))
    files = sorted(files, reverse=True)
    if files:
        return files[0]
    else:
        raise FileNotFoundError("No history_*.csv file found in {}".format(folder))


def read_export(csvfile=None) -> List[Pokemon]:
    """Load Calcy-IV and generate Pokemons"""
    csvfile = csvfile or find_export()
    pokemons = []
    with open(csvfile, newline="", encoding="utf8") as csvfile:
        calcy_reader = csv.DictReader(csvfile, dialect=CustomDialect())
        for row in calcy_reader:
            if row["Ancestor?"] == "1":
                continue
            try:
                pokemon = Pokemon(
                    Pokemon.convert_name(row["Name"]),
                    float(row["Level"]),
                    [
                        int(float(row["ØATT IV"])),
                        int(float(row["ØDEF IV"])),
                        int(float(row["ØHP IV"])),
                    ],
                )  # type: Optional[Pokemon]
            except KeyError:
                print("Pokemon not in gamemaster: " + row["Name"])
                continue
            if not pokemon or pokemon.cp != int(row["CP"]):
                pokemon = Pokemon.find_by_cp_level(
                    Pokemon.convert_name(row["Name"]), int(row["CP"]), float(row["Level"])
                )
            if not pokemon or pokemon.cp != int(row["CP"]):
                print(
                    "Not found any combination for {}, CP: level:{}".format(
                        row["Name"], row["CP"], row["Level"],
                    )
                )
                continue
            pokemons.append(pokemon)
            if row["Fast move"].strip(" -"):
                pokemon.fast = Move.fast_from_name(row["Fast move"])
            if row["Special move"].strip(" -"):
                pokemon.charged = [Move.charged_from_name(row["Special move"])]
                if row["Special move 2"].strip(" -"):
                    pokemon.charged.append(Move.charged_from_name(row["Special move 2"]))
    return pokemons
