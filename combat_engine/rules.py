from __future__ import annotations

"""Reglas deterministas del combate.

Estas reglas son *la verdad*: el LLM no calcula números.

Reglas acordadas:
  - AC = 10 + destreza + ac_adicional
  - AttackRoll = 10 + stat_principal + quality
  - Hit si AttackRoll >= AC
  - HP_max = (10 + level*5) + puntos_vida_final

Daño (MVP, determinista):
  - damage = base_damage + stat_principal + quality
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ComputedNumbers:
    hp_max: int
    ac: int


def base_hp_for_level(level: int) -> int:
    return 10 + int(level) * 5


def compute_hp_max(*, level: int, puntos_vida: int) -> int:
    return max(1, base_hp_for_level(level) + int(puntos_vida))


def compute_ac(*, destreza: int, ac_bonus: int) -> int:
    return 10 + int(destreza) + int(ac_bonus)


def compute_attack_roll(*, stat: int, quality: int) -> int:
    return 10 + int(stat) + int(quality)


def compute_damage(*, base_damage: int, stat: int, quality: int) -> int:
    return max(0, int(base_damage) + int(stat) + int(quality))
