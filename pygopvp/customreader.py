"""Export like PvPoke custom multi-battle"""
import csv
import os
from typing import List

from .model import Move, Pokemon

DATA_DIR = "data"


class CustomDialect(csv.Dialect):
    """Describe the properties of Calcy-IV generated CSV files."""

    delimiter = ","
    skipinitialspace = False
    lineterminator = "\n"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL


def __filepath(cp, section: str) -> str:
    return os.path.join(DATA_DIR, "{}-{}.txt".format(section, cp))


def generate_from_custom(cp, section="custom", top=30) -> List[Pokemon]:
    """Load custom opponents csv and generate Pokemons"""
    filepath = __filepath(cp, section)
    with open(filepath, newline="", encoding="utf8") as csvfile:
        csv_reader = csv.reader(csvfile, dialect=CustomDialect())
        rows = [row for row in csv_reader]
    pokemons = []
    for row in rows:
        if len(row) > 4:
            try:
                pokemon = Pokemon(
                    Pokemon.convert_name(row[0]),
                    float(row[4]),
                    [int(float(row[5])), int(float(row[6])), int(float(row[7]))],
                )
            except KeyError:
                print("Pokemon not in gamemaster: " + row[0])
                continue
        else:
            pokemon = Pokemon.find_max(Pokemon.convert_name(row[0]), cp)
        pokemon.fast = Move.fast_from_name(row[1])
        pokemon.charged = [Move.charged_from_name(row[2])]
        if row[3] != "none":
            pokemon.charged.append(Move.charged_from_name(row[3]))
        pokemons.append(pokemon)
        if len(pokemons) >= top:
            break
    return pokemons
