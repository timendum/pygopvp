from typing import Iterable, List

from ..customreader import generate_from_custom as customs
from ..gotrainer import genate_from_leader as leaders
from ..model import BasePokemon, Move, Pokemon
from ..rankings import generate_from_rankings as rankings
from ..utils import LEAGUES, League


def league(name: str) -> League:
    try:
        # league cp
        cp = int(name)
        for lg in LEAGUES:
            if lg.cp == cp:
                return lg
    except ValueError:
        pass
    # league name
    tname = name.title()
    for lg in LEAGUES:
        # full name
        if lg.name == tname:
            return lg
        # first char
        if lg.name[0] == tname:
            return lg
    raise ValueError("Invalid league value: " + name)


def pokename(name: str) -> str:
    try:
        return BasePokemon.convert_name(name)
    except KeyError:
        raise ValueError("Pokemon not valid: " + name)


def filter_pokemons(pokemons: Iterable[Pokemon], league: League) -> List[Pokemon]:
    result = [pokemon for pokemon in pokemons if pokemon.fast and pokemon.charged]
    result = [pokemon for pokemon in result if pokemon.cp <= league.cp]
    result = [pokemon for pokemon in result if pokemon.cp >= league.lower]
    print("You have {} valid pokemons".format(len(result)))
    return result


def add_moves(pokemon: Pokemon, moves: Iterable[Move]) -> None:
    best_moves = BasePokemon(pokemon.name).best_dpt_moves(legacy=True)
    if [move for move in moves if move.is_fast]:
        pokemon.fast = [move for move in moves if move.is_fast][0]
    else:
        pokemon.fast = Move(best_moves[0])
    pokemon.charged = [move for move in moves if move.is_charged]
    if not pokemon.charged:
        pokemon.charged = [Move(move) for move in best_moves[1:]]


def print_table(headers: Iterable[str], rows: Iterable[Iterable[str]]) -> None:
    """Prints a formatted table, headers and every row must have same size."""
    max_sizes = []
    for i, h in enumerate(headers):
        max_sizes.append(len(h))
    srows = []
    for row in rows:
        srow = []
        for i, c in enumerate(row):
            srow.append(str(c))
            max_sizes[i] = max(max_sizes[i], len(srow[-1]))
        srows.append(srow)
    if not max_sizes:
        return
    print("| ", end="")
    for i, h in enumerate(headers):
        print("{{:>{}}} | ".format(max_sizes[i]).format(h), end="")
    print(" ")
    print("-" * (sum(max_sizes) + len(max_sizes) * 3 + 1))
    for row in srows:
        print("| ", end="")
        for j, c in enumerate(row):
            print("{{:>{}}} | ".format(max_sizes[j]).format(c), end="")
        print("")
    print(" ")


def load_opponents(league: League, dataname: str, nopponents: int) -> List[Pokemon]:
    # AI Trainers (Spark, Candela, Blance)
    try:
        opponents = leaders(dataname.upper(), league)
        return opponents
    except KeyError:
        pass
    # PvPoke rankings
    try:
        opponents = rankings(league.cp, section=dataname, top=nopponents)
        return opponents
    except Exception:
        pass
    # Custom csv
    try:
        opponents = customs(league.cp, section=dataname, top=nopponents)
        return opponents
    except Exception:
        pass
    raise ValueError("Unable to load Opponents from " + dataname)
