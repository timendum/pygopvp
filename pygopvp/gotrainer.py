"""Leaders' pokemons"""
from typing import List

from .gamemaster import TRAINERS
from .model import Move, Pokemon
from .utils import League


def read_export(trainer_name: str, league: League) -> List[Pokemon]:
    """Load pokemons from leaders given league"""
    pnames = TRAINERS[trainer_name.upper()][league]
    pokemons = []
    for pname in pnames:
        pokemon = Pokemon.find_max(Pokemon.convert_name(pname), league.cp)
        if league.name == "Master":
            pokemon.level = 42
        moves = pokemon.best_dpt_moves()
        pokemon.fast = Move(moves[0])
        pokemon.charged = [Move(m) for m in moves[1:]]
        pokemons.append(pokemon)
    return pokemons
