import json
import os
import pathlib
from typing import Any, Dict, List
from urllib.request import urlretrieve

from .model import Pokemon, Move

DATA_DIR = "data"


def __filepath(cp, section: str) -> str:
    return os.path.join(DATA_DIR, "rankings-{}-{}.json".format(cp, section))


def _update(cp, section):
    pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    urlretrieve(
        url="https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/all/{}/rankings-{}.json".format(
            section, cp
        ),
        filename=__filepath(cp, section),
    )


def _load(cp: int, section="overall") -> List[Dict[str, Any]]:
    """Load (and download) file and return a list of {pokemonData}"""
    filepath = __filepath(cp, section)
    if not os.path.isfile(filepath):
        _update(cp, section)
    with open(filepath, "rt") as fjson:
        data = json.load(fjson)
    pokemons = []
    for row in data:
        pokemon = {
            "speciesId": row["speciesId"].upper(),
        }
        pokemon["fastMove"] = sorted(row["moves"]["fastMoves"], key=lambda m: m["uses"])[-1]
        pokemon["fastMove"] = pokemon["fastMove"]["moveId"]
        pokemon["chargedMoves"] = sorted(
            row["moves"]["chargedMoves"], key=lambda m: m["uses"], reverse=True
        )[:2]
        pokemon["chargedMoves"] = [move["moveId"] for move in pokemon["chargedMoves"]]
        pokemons.append(pokemon)
    return pokemons


def generate_from_rankings(cp: int, section="overall", top=10):
    """Load rankings and generate Pokemons"""
    dpokemons = _load(cp, section)[0:top]
    pokemons = []
    for dpokemon in dpokemons:
        pokemon = Pokemon.find_max(Pokemon.convert_name(dpokemon["speciesId"]), cp)
        pokemon.fast = Move.fast_from_name(dpokemon["fastMove"])
        pokemon.charged = [Move.charged_from_name(name) for name in dpokemon["chargedMoves"]]
        pokemons.append(pokemon)
    return pokemons
