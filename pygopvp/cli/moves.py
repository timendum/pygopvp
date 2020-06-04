from typing import Any, List, Tuple, Iterable

from ..battle import Battle
from ..csvreader import read_export
from ..model import Move, Pokemon
from ..rankings import generate_from_rankings
from ..utils import compatible_leagues
from .utils import print_table


def generate_movesets(pokemon: Pokemon) -> List[List[Move]]:
    movesets = []
    for fast in pokemon.fast_moves + pokemon.legacy_fast:
        for charged in pokemon.charged_moves + pokemon.legacy_charged:
            movesets.append([Move(fast), Move(charged)])
    return movesets


def evaluate_movesets(
    pokemon: Pokemon, movesets: List[List[Move]], opponents: Iterable[Pokemon], shields: int
) -> List[Tuple[Any, int]]:
    ratings = []
    for moveset in movesets:
        rating = 0
        for opponent in opponents:
            battle = Battle([pokemon, opponent], shields=shields)
            battle.pokemons[0].fast = moveset[0]
            battle.pokemons[0].charged = [moveset[1]]
            battle.resolve()
            rating += battle.rate(0)
        ratings.append(rating)
    return sorted(zip(movesets, ratings), key=lambda i: i[1], reverse=True)


def order_by_time(movesets: List[List[Move]]):
    times = []
    for fast, charged in movesets:
        times.append(-charged.energyDelta / fast.energyDelta * (fast.waitTurns + 1))
    return sorted(zip(movesets, times), key=lambda i: i[1])


def main(name: str, cp: int, dataname: str, shields: int, nopponents: int) -> None:
    cvs_pokemons = read_export()
    pokemons = [pokemon for pokemon in cvs_pokemons if pokemon.name == name]
    pokemons = [pokemon for pokemon in pokemons if cp == pokemon.cp]
    if not pokemons:
        print("Pokemon not found")
        return
    pokemon = pokemons[0]
    if not pokemon.fast or not pokemon.charged:
        print("Pokemon without moves")
        return
    league = compatible_leagues(pokemon.cp)[0]
    movesets = generate_movesets(pokemon)
    for ms in movesets:
        if ms[0] == pokemon.fast and ms[1] == pokemon.charged[0]:
            break
    else:
        movesets.append([pokemon.fast, pokemon.charged[0]])
    if len(pokemon.charged) > 1:
        for ms in movesets:
            if ms[0] == pokemon.fast and ms[1] == pokemon.charged[1]:
                break
        else:
            movesets.append([pokemon.fast, pokemon.charged[1]])
    print("Ranks:")
    opponents = generate_from_rankings(league.cp, dataname, top=nopponents)
    bests = evaluate_movesets(pokemon, movesets, opponents, shields)
    top = bests[0][1]
    for i, moveset in enumerate(bests):
        fast = moveset[0][0]
        charged = moveset[0][1]
        flegacy = "*" if fast.moveId in pokemon.legacy_fast else ""
        clegacy = "*" if charged.moveId in pokemon.legacy_charged else ""
        print(
            "{:d}. {!s}{} + {!s}{} = {:.0%}".format(
                i + 1, fast, flegacy, charged, clegacy, (moveset[1] / top)
            ),
            end="",
        )
        if fast == pokemon.fast and charged in pokemon.charged:
            print("  (current)")
        else:
            print("")
    print("\nFast move details:")
    fasts = set([Move(move) for move in pokemon.fast_moves + pokemon.legacy_fast])
    fasts.add(pokemon.fast)
    rows = []
    for move in fasts:
        damage = Battle.calculateBaseMoveDamage(move, pokemon)
        turns = move.waitTurns + 1
        rows.append(
            [
                move,
                move.type,
                damage,
                move.energyDelta,
                turns,
                "{:.2f}".format(damage / turns),
                "{:.2f}".format(move.energyDelta / turns),
                "*" if move.moveId in pokemon.legacy_fast else "",
            ]
        )
    rows = sorted(rows, key=lambda row: row[6], reverse=True)  # Sort by DPE
    print_table(["Name", "Type", "D", "E", "T", "DPT", "EPT", "Legacy"], rows)
    print("\nCharges move details:")
    chargeds = set([Move(move) for move in pokemon.charged_moves + pokemon.legacy_charged])
    chargeds.update(pokemon.charged)
    rows = []
    for move in chargeds:
        damage = Battle.calculateBaseMoveDamage(move, pokemon)
        rows.append(
            [
                move,
                move.type,
                damage,
                -move.energyDelta,
                "{:.2f}".format(damage / -move.energyDelta),
                "*" if move.moveId in pokemon.legacy_charged else "",
            ]
        )
    rows = sorted(rows, key=lambda row: row[4], reverse=True)  # Sort by DPE
    print_table(["Name", "Type", "D", "E", "DPE", "Legacy"], rows)
    print("\nQuickest movesets (turns for charged):")
    times = order_by_time(movesets)
    for i, moveset in enumerate(times):
        fast = moveset[0][0]
        charged = moveset[0][1]
        flegacy = "*" if fast.moveId in pokemon.legacy_fast else ""
        clegacy = "*" if charged.moveId in pokemon.legacy_charged else ""
        print(
            "{:d}. {!s}{} + {!s}{} = {:.2f}".format(
                i + 1, fast, flegacy, charged, clegacy, (moveset[1])
            ),
            end="",
        )
        if fast == pokemon.fast and charged in pokemon.charged:
            print("  (current)")
        else:
            print("")
