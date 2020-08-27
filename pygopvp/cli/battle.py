from ..battle import Battle
from ..csvreader import read_export
from ..model import Pokemon
from .utils import add_moves


def main(a_name, a_cp, b_name, b_cp, b_moves, shields):
    # A (mine)
    pokemons = read_export()
    # Filter incomplete pokemon
    pokemons = [pokemon for pokemon in pokemons if pokemon.fast and pokemon.charged]
    pokemons = [pokemon for pokemon in pokemons if pokemon.name == a_name]
    pokemons = [pokemon for pokemon in pokemons if a_cp == pokemon.cp]
    if not pokemons:
        print("Pokemon not found")
        return
    pokemon = pokemons[0]
    opponent = Pokemon.find_by_cp(b_name, b_cp)
    add_moves(opponent, b_moves)
    battle = Battle([pokemon, opponent], shields, battlelog=True)
    battle.resolve()
    print("\n".join(battle.bl.logs))
