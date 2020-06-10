"""Reads from  PvPoke ranking files"""
from typing import Iterable, List, Tuple

from ..battle import Battle
from ..csvreader import read_export
from ..model import Pokemon
from ..utils import compatible_leagues
from .utils import filter_pokemons, find_pokemon, load_opponents


def battle_all(
    pokemon: Pokemon, opponents: Iterable[Pokemon], shields: int
) -> Tuple[int, List[Tuple[Pokemon, int]]]:
    win = 0
    ranks = []
    for i, opponent in enumerate(opponents):
        battle = Battle([pokemon, opponent], shields)
        try:
            battle.resolve()
        except Exception as e:
            print(e)
            print(battle.pokemons)
        if battle.pokemons[1].hp <= 0:
            win += 1
        ranks.append(battle.rate(0))
    return win, sorted(zip(opponents, ranks), key=lambda i: i[1], reverse=True)


def main(name: str, cp: int, dataname: str, shields: int, limit: int, nopponents: int) -> None:
    cvs_pokemons = read_export()
    pokemons = find_pokemon(cvs_pokemons, name, cp)
    if not pokemons:
        print("Pokemon not found")
        return
    pokemon = pokemons[0]
    if not pokemon.fast or not pokemon.charged:
        print("Pokemon without moves")
        return
    league = compatible_leagues(pokemon.cp)[0]
    try:
        opponents = load_opponents(league, dataname, nopponents)
    except Exception as e:
        print(str(e))
        return
    wins, poppos = battle_all(pokemon, opponents, shields)
    lopps = len(opponents)
    poppos = list(poppos)
    print("Wins {:.0%} ({} over {})".format(wins / lopps, wins, lopps))
    for i in range(limit):
        print("{:d}. {!s} = {}".format(i + 1, poppos[i][0].title(), poppos[i][1]))
    print("...")
    for i in range(limit + 1, 0, -1):
        print(
            "{:d}. {!s} = {}".format(
                lopps - i + 1, poppos[lopps - i][0].title(), poppos[lopps - i][1]
            )
        )
