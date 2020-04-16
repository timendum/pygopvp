import random
from math import floor, pow as fpow
from typing import Callable, List, Optional, Tuple

from .gamemaster import BUFFS, MOVES, POKEMONS, SETTINGS
from .utils import Type, json_cache, simple_repr, LEAGUES


class MoveBuff:
    """A buff inside a move"""

    def __init__(self, buff_data):
        self.a_att = buff_data.get("attackerAttackStatStageChange", 0)
        self.a_def = buff_data.get("attackerDefenseStatStageChange", 0)
        self.b_att = buff_data.get("targetAttackStatStageChange", 0)
        self.b_deff = buff_data.get("targetDefenseStatStageChange", 0)
        self.chance = buff_data["buffActivationChance"]
        self.__next_roll = random.random()

    def roll(self):
        """Simulate a chance, starts random then it depens only of the chance.

        It should be stable, quickly convergint to chance"""
        activated = bool(self.__next_roll >= 1 - self.chance)
        self.__next_roll += self.chance
        if self.__next_roll >= 1:
            self.__next_roll -= 1
        return activated


class Move:
    """A pokemon Move"""

    def __init__(self, name):
        move_data = MOVES[name]
        self.moveId = move_data["uniqueId"]
        self.energyDelta = move_data.get("energyDelta", 0)
        self.type = Type(move_data.get("type"))
        self.power = move_data.get("power", 0)
        self.waitTurns = move_data.get("durationTurns", 0)
        if "buffs" in move_data:
            self.buffs = MoveBuff(move_data["buffs"])
        else:
            self.buffs = None

    @property
    def is_fast(self):
        return self.energyDelta >= 0

    @property
    def is_charged(self):
        return not self.is_fast

    def __repr__(self) -> str:
        return "Move({!r})".format(self.moveId)

    def __str__(self) -> str:
        name = self.moveId
        if "_FAST" in name:
            i = name.find("_FAST")
            name = name[0:i]
        name = name.replace("_", " ")
        name = name.title()
        return name

    def __eq__(self, other) -> bool:
        if not isinstance(other, Move):
            return False
        return self.moveId == other.moveId

    def __hash__(self) -> int:
        return hash(self.moveId)

    @staticmethod
    def fast_from_name(name: str) -> "Move":
        """Return a fast move from a name"""
        name = name.replace("-", " ")
        name = name.replace(" ", "_")
        name = name.upper() + "_FAST"
        if name.startswith("HIDDEN_POWER"):
            move = Move.charged_from_name("HIDDEN_POWER_FAST")
            move.type = Type("POKEMON_TYPE_" + name.split("_")[2])
            return move
        return Move(name)

    @staticmethod
    def charged_from_name(name: str) -> "Move":
        """Return a charged move from a name"""
        name = name.replace("-", " ")
        name = name.replace(" ", "_")
        name = name.upper()
        if name == "VISE_GRIP":
            name = "VICE_GRIP"
        elif name == "FUTURE_SIGHT":
            name = "FUTURESIGHT"
        return Move(name)

    def stab_multiplier(self, types: List[Type]):
        """Return the Same Type Attack Bonus multiplier base on pokemon `types`"""
        if self.type in types:
            return SETTINGS["sameTypeAttackBonusMultiplier"]
        return 1

    @staticmethod
    def best_dpt_moves(fast_names: List[str], charged_name: List[str], bonusType=()) -> List[str]:
        """Find the best fast, charged, second charged move name, from a list of move names."""
        TURNS = 1013  # prime number, every charged move should have remaing turns
        best_dpt = 0
        best = ["", ""]
        fasts = [Move(name) for name in fast_names]
        chargeds = [Move(name) for name in charged_name]
        for fast in fasts:
            for charged in chargeds:
                dpt = fast.power * TURNS * fast.stab_multiplier(bonusType) / (fast.waitTurns + 1)
                dpt += (
                    charged.power
                    * charged.stab_multiplier(bonusType)
                    * (fast.energyDelta * TURNS / (fast.waitTurns + 1))
                    / (-charged.energyDelta)
                )
                if dpt > best_dpt:
                    best_dpt = dpt
                    best = [fast.moveId, charged.moveId]
        # 2nd charged
        best_dpt = 0
        best.append("")
        for fast in fasts:
            if fast.moveId != best[0]:
                continue
            for charged in chargeds:
                if fast.moveId == best[0] and charged.moveId == best[1]:
                    continue
                dpt = fast.power * TURNS / (fast.waitTurns + 1)
                dpt += (
                    charged.power
                    * (fast.energyDelta * TURNS / (fast.waitTurns + 1))
                    / (-charged.energyDelta)
                )
                if dpt > best_dpt:
                    best_dpt = dpt
                    best[2] = charged.moveId
        return best


class BasePokemon:
    """A pokemon template"""

    def __init__(self, name):
        pokemon_data = POKEMONS[name]
        self.name = name
        self.types = [Type(pokemon_data.get("type"))]
        self.baseStamina = pokemon_data["stats"]["baseStamina"]
        self.baseAttack = pokemon_data["stats"]["baseAttack"]
        self.baseDefense = pokemon_data["stats"]["baseDefense"]
        self.rarity = pokemon_data.get("rarity", "").replace("POKEMON_RARITY_", "") or None
        self.isTransferable = pokemon_data.get("isTransferable", False)
        self.fast_moves = pokemon_data["quickMoves"]
        self.charged_moves = pokemon_data["cinematicMoves"]
        if "type2" in pokemon_data:
            self.types.append(Type(pokemon_data.get("type2")))

    def __repr__(self) -> str:
        return "BasePokemon({!r})".format(self.name)

    def title(self):
        return self.name.replace("_", " ").replace(" ALOLA", " (Alolan)").title()

    def best_dpt_moves(self) -> List[str]:
        """Find the best move names for this pokemon"""
        return Move.best_dpt_moves(self.fast_moves, self.charged_moves, self.types)

    @staticmethod
    def convert_name(name: str) -> str:
        name = name.replace("-", "_")
        name = name.replace(" ", "_")
        name = name.replace(".", "")  # Mr. Mimer
        name = name.upper()
        name = name.replace("_ALOLAN", "_ALOLA")
        name = name.replace("MEWTWO_ARMORED", "MEWTWO_A")
        return name


class Pokemon(BasePokemon):
    """A pokemon for battle"""

    CPMS = [
        0.094,
        0.135137432,
        0.16639787,
        0.192650919,
        0.21573247,
        0.236572661,
        0.25572005,
        0.273530381,
        0.29024988,
        0.306057377,
        0.3210876,
        0.335445036,
        0.34921268,
        0.362457751,
        0.37523559,
        0.387592406,
        0.39956728,
        0.411193551,
        0.42250001,
        0.432926419,
        0.44310755,
        0.453059958,
        0.46279839,
        0.472336083,
        0.48168495,
        0.4908558,
        0.49985844,
        0.508701765,
        0.51739395,
        0.525942511,
        0.53435433,
        0.542635767,
        0.55079269,
        0.558830576,
        0.56675452,
        0.574569153,
        0.58227891,
        0.589887917,
        0.59740001,
        0.604818814,
        0.61215729,
        0.619399365,
        0.62656713,
        0.633644533,
        0.64065295,
        0.647576426,
        0.65443563,
        0.661214806,
        0.667934,
        0.674577537,
        0.68116492,
        0.687680648,
        0.69414365,
        0.700538673,
        0.70688421,
        0.713164996,
        0.71939909,
        0.725571552,
        0.7317,
        0.734741009,
        0.73776948,
        0.740785574,
        0.74378943,
        0.746781211,
        0.74976104,
        0.752729087,
        0.75568551,
        0.758630378,
        0.76156384,
        0.764486065,
        0.76739717,
        0.770297266,
        0.7731865,
        0.776064962,
        0.77893275,
        0.781790055,
        0.78463697,
        0.787473578,
        0.79030001,
    ]

    def __init__(self, name, level: float, IVs: List[int], attaks=(None, None)):
        super().__init__(name)
        self.level = level
        self.attackIV = IVs[0]
        self.defenseIV = IVs[1]
        self.staminaIV = IVs[2]
        self.fast = attaks[0]  # type: Move
        self.charged = attaks[1:]  # type: List[Move]
        self.reset()

    def __repr__(self) -> str:
        return "Pokemon({!r}, {!r}, {!r}, {!r})".format(
            self.name,
            self.level,
            [self.attackIV, self.defenseIV, self.staminaIV],
            [self.fast] + self.charged,
        )

    def __str__(self) -> str:
        moves = []
        if self.fast:
            moves.append(self.fast)
        if self.charged:
            moves.extend([charged for charged in self.charged if charged])
        s_moves = ""
        if moves:
            s_moves = "; moves: " + ", ".join([str(m) for m in moves])
        return "{!s}(CP: {}{})".format(self.title(), self.cp, s_moves)

    def reset(self) -> None:
        """Reset a pokemon: HP, energy and reset buffs"""
        self.hp = self.startHp
        self.energy = 0
        self.attBuffI = (len(BUFFS["attackBuffMultiplier"]) - 1) >> 1
        self.defBuffI = (len(BUFFS["defenseBuffMultiplier"]) - 1) >> 1

    @property
    def cpm(self) -> float:
        return self.CPMS[int((self.level - 1) * 2)]

    @property
    def attack(self):
        return (
            self.cpm
            * (self.baseAttack + self.attackIV)
            * BUFFS["attackBuffMultiplier"][self.attBuffI]
        )

    @property
    def defense(self):
        return (
            self.cpm
            * (self.baseDefense + self.defenseIV)
            * BUFFS["defenseBuffMultiplier"][self.defBuffI]
        )

    @property
    def startHp(self):
        return floor(self.cpm * (self.baseStamina + self.staminaIV))

    @property
    def cp(self):
        return max(
            floor(
                (
                    (self.baseAttack + self.attackIV)
                    * fpow((self.baseDefense + self.defenseIV), 0.5)
                    * fpow((self.baseStamina + self.staminaIV), 0.5)
                    * fpow(self.cpm, 2)
                )
                / 10
            ),
            10,
        )

    def copy(self) -> "Pokemon":
        """"Return a copy of this pokemon"""
        return Pokemon(
            self.name,
            self.level,
            [self.attackIV, self.defenseIV, self.staminaIV],
            [self.fast] + self.charged,
        )

    @staticmethod
    def __find_best(
        name: str, targetCP: int, validator: Callable[["Pokemon", "Pokemon"], bool], lowerIV
    ) -> Tuple[float, List[int]]:
        if targetCP == LEAGUES[-1].cp:
            return (40.0, [15, 15, 15])
        best = Pokemon(name, 1, [0, 0, 0])
        staminaIV = 15
        while staminaIV >= lowerIV:
            defenseIV = 15
            while defenseIV >= lowerIV:
                attackIV = 15
                while attackIV >= lowerIV:
                    targetCPM = fpow(
                        targetCP
                        * 10
                        / (
                            (best.baseAttack + attackIV)
                            * fpow((best.baseDefense + defenseIV), 0.5)
                            * fpow((best.baseStamina + staminaIV), 0.5)
                        ),
                        0.5,
                    )
                    try:
                        level = (
                            next(i for i, cpm in enumerate(Pokemon.CPMS) if cpm >= targetCPM) / 2
                            - 1
                        )
                    except StopIteration:
                        level = 40.0
                    while level <= 40:
                        pokemon = Pokemon(name, level, [attackIV, defenseIV, staminaIV])
                        if pokemon.cp > targetCP:
                            break
                        if validator(pokemon, best):
                            best = pokemon
                        level += 0.5
                    attackIV -= 1
                defenseIV -= 1
            staminaIV -= 1
        return (best.level, [best.attackIV, best.defenseIV, best.staminaIV])

    @staticmethod
    def find_max(name: str, targetCP: int, lowerIV=0) -> "Pokemon":
        """Find the best (overall) level/IVs for a pokemon, given a maximum CP"""

        @simple_repr
        def mult_v(pokemon: Pokemon, best: Pokemon) -> bool:
            return (pokemon.startHp * pokemon.attack * pokemon.defense) > (
                best.startHp * best.attack * best.defense
            ) or (
                (pokemon.startHp * pokemon.attack * pokemon.defense)
                == (best.startHp * best.attack * best.defense)
                and pokemon.attack > best.attack
            )

        values = json_cache(Pokemon.__find_best, name, targetCP, mult_v, lowerIV)
        return Pokemon(name, values[0], values[1])

    @staticmethod
    def find_by_cp(name: str, targetCP: int, lowerIV=0) -> Optional["Pokemon"]:
        """Find the best (overall) level/IVs for a pokemon, given a target CP"""

        @simple_repr
        def cp_validator(pokemon: Pokemon, best: Pokemon) -> bool:
            return (pokemon.startHp * pokemon.attack * pokemon.defense) > (
                best.startHp * best.attack * best.defense
            ) and pokemon.cp == targetCP

        values = json_cache(Pokemon.__find_best, name, targetCP, cp_validator, lowerIV)
        candidate = Pokemon(name, values[0], values[1])
        if candidate.cp == targetCP:
            return candidate
        return None

    @staticmethod
    def find_by_cp_level(name: str, targetCP: int, level: float, lowerIV=0) -> Optional["Pokemon"]:
        """Find the best (overall) level/IVs for a pokemon, given a target CP and level"""

        @simple_repr
        def cp_l_v(pokemon: Pokemon, best: Pokemon) -> bool:
            return (
                (pokemon.startHp * pokemon.attack * pokemon.defense)
                > (best.startHp * best.attack * best.defense)
                and pokemon.cp == targetCP
                and pokemon.level == level
            )

        values = json_cache(Pokemon.__find_best, name, targetCP, cp_l_v, lowerIV)
        candidate = Pokemon(name, values[0], values[1])
        if candidate.cp == targetCP:
            return candidate
        return None
