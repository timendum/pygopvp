from enum import Enum
from typing import List, Tuple

LEAGUES = {
    "Great": 1500,
    "Ultra": 2500,
    "Master": 100000,
}


class Type(Enum):
    """Pokemon and move types"""

    # Order depens on gamemaster order
    NORMAL = "POKEMON_TYPE_NORMAL"
    FIGHTING = "POKEMON_TYPE_FIGHTING"
    FLYING = "POKEMON_TYPE_FLYING"
    POISON = "POKEMON_TYPE_POISON"
    GROUND = "POKEMON_TYPE_GROUND"
    ROCK = "POKEMON_TYPE_ROCK"
    BUG = "POKEMON_TYPE_BUG"
    GHOST = "POKEMON_TYPE_GHOST"
    STEEL = "POKEMON_TYPE_STEEL"
    FIRE = "POKEMON_TYPE_FIRE"
    WATER = "POKEMON_TYPE_WATER"
    GRASS = "POKEMON_TYPE_GRASS"
    ELECTRIC = "POKEMON_TYPE_ELECTRIC"
    PSYCHIC = "POKEMON_TYPE_PSYCHIC"
    ICE = "POKEMON_TYPE_ICE"
    DRAGON = "POKEMON_TYPE_DRAGON"
    DARK = "POKEMON_TYPE_DARK"
    FAIRY = "POKEMON_TYPE_FAIRY"


def compatible_leagues(cp: int) -> List[Tuple[str, int]]:
    """Give a pokemon CP"""
    leagues = [(k, v) for k, v in LEAGUES.items() if v >= cp]
    if len(leagues) > 1:
        leagues = sorted(leagues, key=lambda k: leagues[1])
    return leagues
