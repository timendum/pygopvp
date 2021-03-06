import json
import os
import pathlib
from typing import Any, Dict, Iterable
from urllib.request import urlretrieve

from .utils import LEAGUES, League, Type

DATA_DIR = "data"
FILEPATH = os.path.join(DATA_DIR, "GAME_MASTER.json")


def _update_miners():
    pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    urlretrieve(
        url="https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json",
        filename=FILEPATH,
    )


POKEMONS = {}
MOVES = {}
EFFECTIVE = {}
SETTINGS: Dict[str, float] = {}
BUFFS: Dict[str, Any] = {}
TRAINERS: Dict[str, Dict[League, Iterable[str]]] = {}


def __data_to_effective(effective_data):
    matches = {}
    for t, v in zip(Type, effective_data["attackScalar"]):
        matches[t] = v
    return matches


def __load():
    if not os.path.isfile(FILEPATH):
        _update_miners()
    with open(FILEPATH, "rt") as fjson:
        data = json.load(fjson)
    smeargle_moves = {}
    for item in data:
        if "templateId" in item:
            templateId = item["templateId"]
            item = item["data"]
            item["templateId"] = templateId
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
        elif "combatNpcTrainer" in item:
            _, name, league_name = item["templateId"].split("_")
            league = [l for l in LEAGUES if l.name == league_name.title()][0]
            pokemons = [p for p in item["combatNpcTrainer"]["availablePokemon"]]
            if name not in TRAINERS:
                TRAINERS[name] = {l: () for l in LEAGUES}
            TRAINERS[name][league] = []
            for pokemon in pokemons:
                if "pokemonDisplay" in pokemon:
                    TRAINERS[name][league].append(pokemon["pokemonDisplay"]["form"])
                else:
                    TRAINERS[name][league].append(pokemon["pokemonType"])

    POKEMONS["SMEARGLE"].update(smeargle_moves)


if __name__ == "__main__":
    _update_miners()
    print("Gamemaster updated")

try:
    __load()
except json.decoder.JSONDecodeError:
    os.unlink(FILEPATH)
    __load()
