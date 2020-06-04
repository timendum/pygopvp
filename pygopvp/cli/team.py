from typing import Iterable, List, Set, Tuple

from ..battle import Battle
from ..csvreader import read_export
from ..model import Pokemon
from .utils import filter_pokemons, load_opponents


def order_pokemons(
    opponents: Iterable[Pokemon], pokemons: Iterable[Pokemon], shields: int
) -> List[Tuple[Pokemon, Set[str]]]:
    bests = []
    wins = []  # type: List[Set[str]]
    for pokemon in pokemons:
        win = []
        for opponent in opponents:
            battle = Battle([pokemon, opponent], shields)
            try:
                battle.resolve()
            except Exception as e:
                print(e)
                print(battle.pokemons)
            if battle.pokemons[1].hp <= 0:
                win.append(opponent.name)
        bests.append(pokemon)
        wins.append(set(win))
    return sorted(zip(bests, wins), key=lambda i: len(i[1]), reverse=True)


def order_coverage(
    pokemons: Iterable[Pokemon], wins: List[Set[str]]
) -> List[Tuple[Tuple[Pokemon, Pokemon, Pokemon], Set[str]]]:
    pokemons = list(pokemons)
    ratings = []
    for i, a in enumerate(pokemons[0:-2]):
        for j, b in enumerate(pokemons[0:-1]):
            if j <= i:
                continue
            for k, c in enumerate(pokemons):
                if k <= j:
                    continue
                ratings.append(((a, b, c), wins[i].union(wins[j]).union(wins[k])))
    return sorted(ratings, key=lambda r: len(r[1]), reverse=True)


def main(league, dataname: str, shields: int, limit: int, nopponents: int) -> None:
    try:
        opponents = load_opponents(league, dataname, nopponents)
    except Exception as e:
        print(str(e))
        return
    pokemons = read_export()
    pokemons = filter_pokemons(pokemons, league)
    bests = order_pokemons(opponents, pokemons, shields)[:limit]
    print("\nBest pokemons:")
    for i, best in enumerate(bests):
        print("{:d}. {!s} = {}".format(i + 1, best[0], best[1]))
    suggestions = order_coverage([e[0] for e in bests], [e[1] for e in bests])[:10]
    print("\nSuggestions:")
    for i, suggestion in enumerate(suggestions):
        print(
            "{:d}. {!s} = {}".format(
                i + 1, ", ".join([str(p) for p in suggestion[0]]), suggestion[1]
            )
        )
