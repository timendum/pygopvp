from typing import Iterable, List, Tuple

from ..battle import Battle
from ..csvreader import read_export
from ..model import Pokemon
from ..utils import compatible_leagues
from .utils import add_moves, filter_pokemons


def order_matches(
    opponent: Pokemon, pokemons: Iterable[Pokemon], shields: int
) -> List[Tuple[Pokemon, int]]:
    pokemons = iter(pokemons)
    bests = []
    ratings = []
    for pokemon in pokemons:
        battle = Battle([pokemon, opponent], shields)
        battle.resolve()
        bests.append(pokemon)
        ratings.append(battle.rate(0))
    return list(sorted(zip(bests, ratings), key=lambda i: i[1], reverse=True))


def main(opponent_name, opponent_cp, shields, limit, moves):
    opponent = Pokemon.find_by_cp(opponent_name, opponent_cp)
    add_moves(opponent, moves)
    print("Target pokemon: {!s}".format(opponent))
    pokemons = read_export()
    # Filter incomplete pokemon
    pokemons = [pokemon for pokemon in pokemons if pokemon.fast and pokemon.charged]
    league = compatible_leagues(opponent_cp)[0]
    pokemons = filter_pokemons(pokemons, league)
    bests = order_matches(opponent, pokemons, shields)[:limit]
    for i, (pokemon, rate) in enumerate(bests):
        print("{:d}. {!s} ({})".format(i + 1, pokemon, rate))
