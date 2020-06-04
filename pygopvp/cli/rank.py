"""Reads from  PvPoke ranking files"""
from typing import Iterable, List, Tuple

from ..battle import Battle
from ..csvreader import read_export
from .utils import filter_pokemons, load_opponents
from ..model import Pokemon
from ..utils import League


def order_pokemons(
    opponents: Iterable[Pokemon], pokemons: Iterable[Pokemon], shields: int
) -> List[Tuple[Pokemon, int, float]]:
    bests = []
    ranks = []
    wins = []
    for pokemon in pokemons:
        rank = 0
        win = 0
        for i, opponent in enumerate(opponents):
            battle = Battle([pokemon, opponent], shields)
            try:
                battle.resolve()
            except Exception as e:
                print(e)
                print(battle.pokemons)
            rank += battle.rate(0)
            if battle.pokemons[1].hp <= 0:
                win += 1
        bests.append(pokemon)
        ranks.append(rank)
        wins.append(win / (i + 1))
    return sorted(zip(bests, ranks, wins), key=lambda i: i[1], reverse=True)


def main(league: League, dataname: str, shields, limit: int, nopponents: int) -> None:
    try:
        opponents = load_opponents(league, dataname, nopponents)
    except Exception as e:
        print(str(e))
        return
    pokemons = read_export()
    pokemons = filter_pokemons(pokemons, league)
    bests = order_pokemons(opponents, pokemons, shields)[:limit]
    for i, best in enumerate(bests):
        print("{:d}. {!s} = {} {:.2%}".format(i + 1, best[0], best[1], best[2]))
