from math import floor
from typing import Iterable, List

from .gamemaster import BUFFS, EFFECTIVE, SETTINGS
from .model import Move, Pokemon


class BL:
    """Holds and generate battle log"""

    def __init__(self, battle: "Battle"):
        self.logs: List[str] = []
        self.battle = battle

    def _p_name(self, a):
        return self.battle.pokemons[a].title()

    def _p_str(self, a):
        pkmn = self.battle.pokemons[a]
        return "{!s}(HP: {}, energy: {})".format(pkmn.name.title(), pkmn.hp, pkmn.energy)

    def shield(self, a: int, move: Move):
        self.logs.append(
            "{:>2} {} uses {} but shield is used: deals 1 damange and loses {} energy".format(
                self.battle.turn, self._p_name(a), move, -move.energyDelta
            )
        )

    def damage(self, a: int, move: Move, dmg: int):
        self.logs.append(
            "{:>2} {} uses {}: deals {} damage and gains {} energy".format(
                self.battle.turn, self._p_str(a), move, dmg, move.energyDelta
            )
        )

    def start(self):
        self.logs.append(
            "Start: {!r} vs {!r}".format(self.battle.pokemons[0], self.battle.pokemons[1])
        )

    def end_turn(self):
        self.logs.append(
            "{:>2} End of turn: {} vs {}".format(self.battle.turn, self._p_str(0), self._p_str(1))
        )

    def buff(self, a: int, stat: str, amount: int):
        texts = [None, "rose", "rose sharply", "fell sharply", "fell"]
        self.logs.append(
            "{:>2} {} {} {}".format(self.battle.turn, self._p_str(a), stat, texts[amount])
        )


class DummyBL:
    """To fake BL when not needed"""

    def __call__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        if name == "log":
            return ()
        return self


class FakeMove(Move):
    def __init__(self, name="Fake"):
        self.moveId = name
        self.energyDelta = 0
        self.type = None
        self.power = 0
        self.durationTurns = 1
        self.buffs = None


WAIT_TURN = FakeMove("Wait")


class Battle:
    MAX_ENERGY = int(SETTINGS["maxEnergy"])
    TURN_DURATION = int(SETTINGS["turnDurationSeconds"] * 1000)
    CHARGING_DURATION = 9500

    def __init__(self, pokemons: Iterable[Pokemon], shields=(1, 1), battlelog=False):
        self.pokemons = [pokemon.copy() for pokemon in pokemons]
        if isinstance(shields, int):
            shields = [shields, shields]
        self.startSchields = list(shields)
        self.reset()
        self.waitTurns = [0, 0]
        if battlelog:
            self.bl = BL(self)
            self.bl.start()
        else:
            self.bl = DummyBL()  # type: ignore

    def reset(self) -> None:
        self.turn = 0
        self.mseconds = 0
        self.shields = self.startSchields
        for pokemon in self.pokemons:
            pokemon.reset()

    def __repr__(self):
        return "Battle({!r}, shields={}".format(self.pokemons, self.startSchields)

    def __str__(self):
        return "{!s} vs {!s}".format(self.pokemons[0], self.pokemons[1])

    def remaining_shields(self, b: int):
        return self.shields[b]

    def consume_shield(self, b: int):
        self.shields[b] -= 1

    def calculateDamage(self, a, move: Move) -> int:
        b = a ^ 1
        if move.is_fast:
            attackMultiplier = SETTINGS["fastAttackBonusMultiplier"]
        else:
            attackMultiplier = SETTINGS["chargeAttackBonusMultiplier"]
        damage = (
            floor(
                move.power
                * move.stab_multiplier(self.pokemons[a].types)
                * (self.pokemons[a].attack / self.pokemons[b].defense)
                * self.typeMultiplier(b, move)
                * 0.5
                * attackMultiplier
            )
            + 1
        )
        return damage

    @staticmethod
    def calculateBaseMoveDamage(move: Move, attacker: Pokemon):
        if move.is_fast:
            attackMultiplier = SETTINGS["fastAttackBonusMultiplier"]
        else:
            attackMultiplier = SETTINGS["chargeAttackBonusMultiplier"]
        if move.type in attacker.types:
            attackMultiplier *= SETTINGS["sameTypeAttackBonusMultiplier"]
        damage = move.power * attackMultiplier + 1
        return damage

    def typeMultiplier(self, b: int, move: Move) -> float:
        multiplier = 1
        for ptype in self.pokemons[b].types:
            multiplier *= EFFECTIVE[move.type][ptype]
        return multiplier

    def can_continue(self):
        if not all(self.pokemons) or len(self.pokemons) != 2:
            return False
        if self.pokemons[0].hp <= 0 or self.pokemons[1].hp <= 0:
            return False
        # TODO: timer
        return True

    @property
    def seconds(self):
        return self.mseconds / 1000

    def perform_move(self, a: int, move: Move) -> None:
        if move == WAIT_TURN:
            return
        b = a ^ 1
        attacker = self.pokemons[a]
        defender = self.pokemons[b]
        damage = self.calculateDamage(a, move)
        attacker.energy += move.energyDelta
        attacker.energy = min(attacker.energy, self.MAX_ENERGY)
        self.waitTurns[a] = move.waitTurns
        if move.is_fast:
            defender.hp -= min(damage, defender.hp)
            self.bl.damage(a, move, damage)
            return
        # charged
        self.mseconds += self.CHARGING_DURATION
        if self.remaining_shields(b) > 0:
            self.consume_shield(b)
            defender.hp -= 1
            self.bl.shield(a, move)
            self.apply_buffs(a, move)
            return
        defender.hp -= min(damage, defender.hp)
        self.bl.damage(a, move, damage)
        self.apply_buffs(a, move)

    @staticmethod
    def __calc_buff(start: int, delta: int) -> int:
        value = start + delta
        value = max(BUFFS["minimumStatStage"], value)
        value = min(BUFFS["maximumStatStage"], value)
        return value

    def apply_buffs(self, a: int, move: Move) -> None:
        if not move.buffs:
            return
        buff = move.buffs
        if buff.a_att or buff.a_def:
            attacker = self.pokemons[a]
            if buff.a_att:
                attacker.attBuffI = self.__calc_buff(attacker.attBuffI, buff.a_att)
                self.bl.buff(a, "attack", buff.a_att)
            if buff.a_def:
                attacker.defBuffI = self.__calc_buff(attacker.defBuffI, buff.a_def)
                self.bl.buff(a, "defense", buff.a_def)
        if buff.b_att or buff.b_deff:
            b = a ^ 1
            defender = self.pokemons[b]
            if buff.b_att:
                defender.attBuffI = self.__calc_buff(defender.attBuffI, buff.b_att)
                self.bl.buff(b, "attack", buff.b_att)
            if buff.a_def:
                defender.defBuffI = self.__calc_buff(defender.defBuffI, buff.b_def)
                self.bl.buff(b, "defense", buff.b_def)

    def perform_turn(self) -> None:
        if self.pokemons[1].attack > self.pokemons[0].attack:
            a = 1
        else:
            a = 0
        # a = attack priority
        b = a ^ 1
        self.turn += 1
        if self.waitTurns[a] >= 1:
            self.waitTurns[a] -= 1
            movea = WAIT_TURN  # type: Move
        else:
            movea = decide_move(self, a)
        if self.waitTurns[b] >= 1:
            moveb = WAIT_TURN  # type: Move
            self.waitTurns[b] -= 1
        else:
            moveb = decide_move(self, b)
        b_moved = False
        if moveb.is_charged and movea.is_fast:
            self.perform_move(b, moveb)
            b_moved = True
            if not self.can_continue():
                return
        self.perform_move(a, movea)
        if movea.is_charged:
            if not self.can_continue():
                return
        if not b_moved:
            self.perform_move(b, moveb)
        # check for charged and waitTurns
        if movea.is_charged and moveb.is_fast:
            self.waitTurns[b] = 0
        elif moveb.is_charged and movea.is_fast:
            self.waitTurns[a] = 0

    def resolve(self) -> None:
        self.mseconds += 1000
        while True:
            self.perform_turn()
            self.mseconds += self.TURN_DURATION
            if not self.can_continue():
                self.mseconds += self.TURN_DURATION
                break
        self.bl.end_turn()

    def rate(self, i: int) -> int:
        """Rate a pokemon in a battle, same as pvpoke"""
        pokea = self.pokemons[i]
        pokeb = self.pokemons[i ^ 1]
        return floor(
            (500 * ((pokeb.startHp - pokeb.hp) / pokeb.startHp))
            + (500 * (pokea.hp / pokea.startHp))
        )


def _enablet_charged(attacker: Pokemon) -> List[Move]:
    enabled_charged = []  # type: List[Move]
    for charged in attacker.charged:
        if not charged:
            continue
        if attacker.energy >= -charged.energyDelta:
            enabled_charged.append(charged)
    return enabled_charged


def decide_move(battle: Battle, a: int, consume_shield=True) -> Move:
    b = a ^ 1
    attacker = battle.pokemons[a]
    defender = battle.pokemons[b]
    # no available charged
    enabled_charged = _enablet_charged(attacker)
    if not enabled_charged:
        return attacker.fast
    # is a fast move enought to ko?
    if battle.calculateDamage(a, attacker.fast) >= defender.hp:
        return attacker.fast
    # at least 1 available charged
    chargeds = sorted(attacker.charged, key=lambda charged: charged.energyDelta)
    # if poke has only 1 charged, use it
    if len(chargeds) == 1:
        return enabled_charged[0]
    if consume_shield:
        # we want to consume defender shields asap
        if battle.shields[b] > 0:
            return enabled_charged[0]
    best_charged = find_best_charged(battle, a)
    if attacker.charged[best_charged] in enabled_charged:
        return attacker.charged[best_charged]
    # check if attacker is going ko soon
    if battle.calculateDamage(b, defender.fast) * 2 >= attacker.hp:
        return enabled_charged[0]
    # TODO not best charged if attacker can ko before his ko
    return attacker.fast


def find_best_charged(battle: Battle, a: int) -> int:
    """Find the index of the best charged move for attacker by:

    1. Damage per energy
    2. Energy use
    3. With buff"""
    attacker = battle.pokemons[a]
    chargeds = attacker.charged
    # calculate damage per energy
    dpes = [battle.calculateDamage(a, chargeds[i]) / chargeds[i].energyDelta for i in (0, 1)]
    dpes = [-dpe for dpe in dpes]  # adjust sign
    if dpes[0] >= dpes[1]:
        return 0
    if dpes[1] > dpes[0]:
        return 1
    # use the one with less energy
    energyes = [-charged.energyDelta for charged in chargeds]
    if energyes[0] >= energyes[1]:
        return 0
    if energyes[1] > energyes[0]:
        return 1
    # same energy, check for buff
    with_buff = [i for i, charged in enumerate(chargeds) if charged.buffs]
    if len(with_buff) == 1:
        return with_buff[0]
    return 0
