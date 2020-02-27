import json
import os
import pathlib
from typing import Dict, List, Union
from urllib.request import urlretrieve

from .utils import Type

DATA_DIR = "data"
FILEPATH = os.path.join(DATA_DIR, "GAME_MASTER.json")


def _update():
    pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    urlretrieve(
        url=(
            "https://raw.githubusercontent.com/pokemongo-dev-contrib/pokemongo-game-master/"
            + "master/versions/latest/GAME_MASTER.json"
        ),
        filename=FILEPATH,
    )


POKEMONS = {}
MOVES = {}
EFFECTIVE = {}
SETTINGS = {}  # type: Dict[str, float]
BUFFS = {}  # type: Dict[str, Union[int, List[float]]]


def __data_to_effective(effective_data):
    matches = {}
    for t, v in zip(Type, effective_data["attackScalar"]):
        matches[t] = v
    return matches


def __load():
    if not os.path.isfile(FILEPATH):
        _update()
    with open(FILEPATH, "rt") as fjson:
        data = json.load(fjson)
    smeargle_moves = {}
    for item in data["itemTemplates"]:
        if "pokemonSettings" in item:
            pokemon_data = item["pokemonSettings"]
            # POKEMON
            key = pokemon_data.get("form", pokemon_data["pokemonId"])
            POKEMONS[key] = pokemon_data
        elif "combatMove" in item:
            move_data = item["combatMove"]
            key = move_data["uniqueId"]
            MOVES[key] = move_data
        elif "typeEffective" in item:
            effective_data = item["typeEffective"]
            key = effective_data["attackType"]
            EFFECTIVE[Type(key)] = __data_to_effective(effective_data)
        elif item["templateId"] == "COMBAT_SETTINGS":
            SETTINGS.update(item["combatSettings"])
        elif item["templateId"] == "COMBAT_STAT_STAGE_SETTINGS":
            BUFFS.update(item["combatStatStageSettings"])
        elif item["templateId"] == "SMEARGLE_MOVES_SETTINGS":
            smeargle_moves.update(item["smeargleMovesSettings"])
    POKEMONS["SMEARGLE"].update(smeargle_moves)


__load()
