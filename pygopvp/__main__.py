import argparse

from pygopvp.cli.battle import main as battle_func
from pygopvp.cli.counter import main as counter_func
from pygopvp.cli.moves import main as moves_func
from pygopvp.cli.rank import main as rank_func
from pygopvp.cli.team import main as team_func
from pygopvp.cli.utils import league, pokename
from pygopvp.cli.vsall import main as vsall_func
from pygopvp.gamemaster import _update_dev, _update_miners
from pygopvp.model import Move


def team_main(args):
    return team_func(args.league, args.opponents, args.shields, args.num, args.nopponents)


def vsall_main(args):
    return vsall_func(args.name, args.cp, args.opponents, args.shields, args.num, args.nopponents)


def counter_main(args):
    moves = []
    if args.fast:
        moves.append(args.fast)
    if args.charged:
        moves.extend(args.charged)
    return counter_func(args.opponent, args.cp, args.shields, args.num, moves)


def rank_main(args):
    return rank_func(args.league, args.opponents, args.shields, args.num, args.nopponents)


def moves_main(args):
    return moves_func(args.name, args.cp, args.opponents, args.shields, args.nopponents)


def battle_main(args):
    moves = []
    if args.fast:
        moves.append(args.fast)
    if args.charged:
        moves.extend(args.charged)
    return battle_func(args.name, args.cp, args.opponent, args.ocp, moves, args.shields)


def gamemaster_update(args):
    if args.source.lower() in ("dev",):
        _update_dev()
        print("Gamemaster updated from pokemongo-dev-contrib")
    else:
        _update_miners()
        print("Gamemaster updated from PokeMiners")


def shields(s: str):
    try:
        return int(s)
    except ValueError:
        return [int(sp) for sp in s.split(",")]


def main():
    parser = argparse.ArgumentParser("pygopvp")
    subparsers = parser.add_subparsers(help="Modules:")
    # team_advisor
    parser_team = subparsers.add_parser("team", help="Find the best team for a list of opponents")
    parser_team.set_defaults(func=team_main)
    parser_team.add_argument("league", default="great", type=league)
    parser_team.add_argument("opponents", default="overall", type=str)
    parser_team.add_argument("--shields", "-s", default=1, type=shields)
    parser_team.add_argument(
        "-nopponents", "-o", default=30, type=int, help="Max number of opponents"
    )
    parser_team.add_argument("--num", "-n", default=10, type=int, help="Number of results")
    # counter_advisor
    parser_counter = subparsers.add_parser(
        "counter", help="Find the best counter against an opponent"
    )
    parser_counter.set_defaults(func=counter_main)
    parser_counter.add_argument("opponent", type=pokename)
    parser_counter.add_argument("cp", type=int)
    parser_counter.add_argument("--fast", "-f", type=Move.fast_from_name)
    parser_counter.add_argument("--charged", "-c", nargs="*", type=Move.charged_from_name)
    parser_counter.add_argument("-shields", "-s", default=1, type=shields)
    parser_counter.add_argument("--num", "-n", default=10, type=int, help="Number of results")
    # rank
    parser_rank = subparsers.add_parser("rank", help="Rank your pokemons")
    parser_rank.set_defaults(func=rank_main)
    parser_rank.add_argument("league", default="great", type=league)
    parser_rank.add_argument("opponents", default="overall", type=str, nargs="?")
    parser_rank.add_argument("--shields", "-s", default=1, type=shields)
    parser_rank.add_argument(
        "-nopponents", "-o", default=30, type=int, help="Max number of opponents"
    )
    parser_rank.add_argument("-num", "-n", default=10, type=int, help="Number of results")
    # moves
    parser_moves = subparsers.add_parser("moves", help="Suggest best moveset for your pokemon")
    parser_moves.set_defaults(func=moves_main)
    parser_moves.add_argument("name", type=pokename, help="Your pokemon name")
    parser_moves.add_argument("cp", type=int, help="Your pokemon CP")
    parser_moves.add_argument("opponents", default="overall", type=str, nargs="?")
    parser_moves.add_argument("--shields", "-s", default=1, type=shields, help="How many shields")
    parser_moves.add_argument(
        "-nopponents", "-o", default=30, type=int, help="Max number of opponents"
    )
    # battle
    parser_battle = subparsers.add_parser("battle", help="Simulate a battle")
    parser_battle.set_defaults(func=battle_main)
    parser_battle.add_argument("name", type=pokename, help="Your pokemon name")
    parser_battle.add_argument("cp", type=int, help="Your pokemon CP")
    parser_battle.add_argument("opponent", type=pokename)
    parser_battle.add_argument("ocp", type=int, help="Opponent CP")
    parser_battle.add_argument("--fast", "-f", type=Move.fast_from_name)
    parser_battle.add_argument("--charged", "-c", nargs="*", type=Move.charged_from_name)
    parser_battle.add_argument("--shields", "-s", default=1, type=shields, help="How many shields")
    # vsall
    parser_vsall = subparsers.add_parser("vsall", help="Rank a single pokemon vs others")
    parser_vsall.set_defaults(func=vsall_main)
    parser_vsall.add_argument("name", type=pokename, help="Your pokemon name")
    parser_vsall.add_argument("cp", type=int, help="Your pokemon CP")
    parser_vsall.add_argument("opponents", default="overall", type=str, nargs="?")
    parser_vsall.add_argument("--shields", "-s", default=1, type=shields, help="How many shields")
    parser_vsall.add_argument("-num", "-n", default=5, type=int, help="Number of results")
    parser_vsall.add_argument(
        "-nopponents", "-o", default=10000, type=int, help="Max number of opponents"
    )
    # gamemaster update
    parser_gmupdate = subparsers.add_parser("gamemaster", help="Update gamemaster")
    parser_gmupdate.set_defaults(func=gamemaster_update)
    parser_gmupdate.add_argument(
        "--source", "-s", default="pokeminers", help="Source name", choices=["pokeminers", "dev"]
    )
    # parse
    args = parser.parse_args()
    if "func" in args:
        args.func(args)
    else:
        parser.print_help()


main()
