import random
from math import floor, pow
from typing import List

from .gamemaster import BUFFS, MOVES, POKEMONS
from .utils import Type


class MoveBuff:
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
        if self.__next_roll >= 1 - self.chance:
            activated = True
        else:
            activated = False
        self.__next_roll += self.chance
        if self.__next_roll >= 1:
            self.__next_roll -= 1
        return activated


class Move:
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

    def __repr__(self):
        return "Move({!r})".format(self.moveId)

    def __str__(self):
        name = self.moveId
        if "_FAST" in name:
            i = name.find("_FAST")
            name = name[0:i]
        name = name.replace("_", " ")
        name = name.title()
        return name

    @staticmethod
    def fast_from_name(name: str) -> "Move":
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
        name = name.replace("-", " ")
        name = name.replace(" ", "_")
        name = name.upper()
        if name == "VISE_GRIP":
            name = "VICE_GRIP"
        return Move(name)


class BasePokemon:
    def __init__(self, name):
        pokemon_data = POKEMONS[name]
        self.pokemonId = pokemon_data["pokemonId"]
        self.types = [Type(pokemon_data.get("type"))]
        self.baseStamina = pokemon_data["stats"]["baseStamina"]
        self.baseAttack = pokemon_data["stats"]["baseAttack"]
        self.baseDefense = pokemon_data["stats"]["baseDefense"]
        if "type2" in pokemon_data:
            self.types.append(Type(pokemon_data.get("type2")))

    def __repr__(self):
        return "BasePokemon({!r})".format(self.pokemonId)


class Pokemon(BasePokemon):
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

    def __init__(self, name, level: float, IVs: List[int], attaks=[None, None]):
        super().__init__(name)
        self.level = level
        self.attackIV = IVs[0]
        self.defenseIV = IVs[1]
        self.staminaIV = IVs[2]
        self.fast = attaks[0]  # type: Move
        self.charged = attaks[1:]  # type: List[Move]
        self.reset()

    def __repr__(self):
        return "Pokemon({!r}, {!r}, {!r}, {!r})".format(
            self.pokemonId,
            self.level,
            [self.attackIV, self.defenseIV, self.staminaIV],
            [self.fast] + self.charged,
        )

    def __str__(self):
        return "{!s}(hp: {}, att:{}, def: {}, energy: {})".format(
            self.pokemonId.title(), self.hp, self.attack, self.defense, self.energy
        )

    def reset(self):
        self.hp = self.startHp
        self.energy = 0
        self.attBuffI = (len(BUFFS["attackBuffMultiplier"]) - 1) >> 1
        self.defBuffI = (len(BUFFS["defenseBuffMultiplier"]) - 1) >> 1

    @property
    def cpm(self):
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
                    * pow((self.baseDefense + self.defenseIV), 0.5)
                    * pow((self.baseStamina + self.staminaIV), 0.5)
                    * pow(self.cpm, 2)
                )
                / 10
            ),
            10,
        )

    def generate_dummy(self, tagertHP=0) -> "Pokemon":
        dummyp = Pokemon(
            self.pokemonId,
            self.level,
            [self.defenseIV, self.attackIV, self.staminaIV],  # defense and attack inverted
            [Move("YAWN_FAST"), Move("FRUSTRATION")],
        )
        dummyp.types = []
        if tagertHP:
            dummyp.staminaIV = tagertHP - dummyp.startHp
        return dummyp

    @staticmethod
    def from_name(name: str, level: float, IVs: List[int], attaks=[None, None]) -> "Pokemon":
        name = name.replace("-", "_")
        name = name.replace(" ", "_")
        name = name.upper()
        name = name.replace("_ALOLAN", "_ALOLA")
        return Pokemon(name, level, IVs, attaks)
