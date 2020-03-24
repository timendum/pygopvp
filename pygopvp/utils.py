from collections import namedtuple
from enum import Enum
from typing import List, Dict, Any
import json
import os
import atexit

League = namedtuple("League", ["name", "cp", "lower"])

LEAGUES = [League("Great", 1500, 1000), League("Ultra", 2500, 2000), League("Master", 10000, 2500)]

DATA_DIR = "data"


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


def compatible_leagues(cp: int) -> List[League]:
    """Give a pokemon CP"""
    leagues = [league for league in LEAGUES if league.cp >= cp]
    if len(leagues) > 1:
        leagues = sorted(leagues, key=lambda league: league.cp)
    return leagues


class simple_repr:
    """This decorator replace the repr of a function with the function name"""

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return self.func.__name__


__CACHE_DATA = {}  # type: Dict[str, Any]
__DIRTY = {}


def start_cache():
    """Current cache will be written and a new cache will start with content from file."""
    cache_file = os.path.join(DATA_DIR, "_cache.json")
    __CACHE_DATA.clear()
    if os.path.isfile(cache_file):
        with open(cache_file, "r", encoding="utf8") as fp:
            __CACHE_DATA.update(json.load(fp))


def json_cache(func, *args, **kwargs) -> Any:
    """Read content from cache or invoke `func` with `*args` and `**kwargs`"""
    key = "{}.{}:{!r}-{!r}".format(func.__module__, func.__name__, args, kwargs)
    if key in __CACHE_DATA:
        return __CACHE_DATA[key]
    result = func(*args, **kwargs)
    __CACHE_DATA[key] = result
    __DIRTY["value"] = True
    return result


def write_cache():
    """Save cache to disk, if needed"""
    cache_file = os.path.join(DATA_DIR, "_cache.json")
    if "value" not in __DIRTY:
        return
    with open(cache_file, "w", encoding="utf8") as fp:
        json.dump(__CACHE_DATA, fp)
    del __DIRTY["value"]


start_cache()
atexit.register(write_cache)
