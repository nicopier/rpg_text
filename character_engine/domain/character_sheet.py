from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List

from character_engine.models.character import CharacterModel
from character_engine.models.item import ItemModel
from character_engine.services.equipment_service import EquipmentService


# -------------------------
# D&D-ish helpers
# -------------------------

def ability_mod(score: int) -> int:
    # D&D clásico: (score - 10) // 2
    return (int(score) - 10) // 2


def parse_dice(d: str) -> Tuple[int, int]:
    s = (d or "").strip().lower()
    if "d" not in s:
        raise ValueError(f"Dado inválido: {d!r}")
    a, b = s.split("d", 1)
    n = int(a) if a else 1
    sides = int(b)
    if n <= 0 or sides <= 0:
        raise ValueError(f"Dado inválido: {d!r}")
    return n, sides


# -------------------------
# Runtime views (NO storage)
# -------------------------

@dataclass(frozen=True)
class AttackProfile:
    """
    Perfil de ataque listo para motor (sin RNG).
    El motor decide el hit/daño.
    """
    id: str
    name: str
    hand: str                  # "main" | "off" | "unarmed"
    damage_dice: str           # "1d6"
    damage_type: str           # default "physical"
    range: int                 # default 1
    stat_key: str              # "fuerza" | "destreza" | "inteligencia"
    to_hit_bonus: int = 0      # por calidad, buffs, etc.


class CharacterSheet:
    """
    Fachada runtime sobre CharacterModel.

    - NO duplica modelos.
    - NO inventa storage nuevo.
    - Interpreta stats + equipped + state.
    - Usa EquipmentService para equip/unequip (swap incluido).
    """

    def __init__(
        self,
        character: CharacterModel,
        *,
        equipment_service: Optional[EquipmentService] = None,
    ) -> None:
        self.character = character
        self.eq = equipment_service or EquipmentService()

    # -------------------------
    # BASE + EFFECTIVE STATS
    # -------------------------

    @property
    def base(self) -> Dict[str, int]:
        s = self.character.stats.stats
        return {
            "level": int(s.level),
            "fuerza": int(s.fuerza),
            "destreza": int(s.destreza),
            "inteligencia": int(s.inteligencia),
            "puntos_vida": int(s.puntos_vida),
            "estres": int(s.estres),
        }

    @property
    def equipped_items(self) -> Dict[str, Optional[ItemModel]]:
        e = self.character.stats.equipped
        # OJO: estos nombres vienen de tu EquippedModel
        return {
            "casco": e.casco,
            "pecho": e.pecho,
            "botas": e.botas,
            "arma_derecha": e.arma_derecha,
            "arma_izquierda": e.arma_izquierda,
            "anillo_derecho": e.anillo_derecho,
            "anillo_izquierdo": e.anillo_izquierdo,
        }

    @property
    def equipment_mods(self) -> Dict[str, int]:
        mods = {"fuerza": 0, "destreza": 0, "inteligencia": 0, "puntos_vida": 0, "estres": 0}
        for item in self.equipped_items.values():
            if not item:
                continue
            sm = item.stat_modifiers
            mods["fuerza"] += int(sm.fuerza)
            mods["destreza"] += int(sm.destreza)
            mods["inteligencia"] += int(sm.inteligencia)
            mods["puntos_vida"] += int(sm.puntos_vida)
            mods["estres"] += int(sm.estres)
        return mods

    @property
    def effective(self) -> Dict[str, int]:
        b = self.base
        m = self.equipment_mods
        return {
            "level": b["level"],
            "fuerza": b["fuerza"] + m["fuerza"],
            "destreza": b["destreza"] + m["destreza"],
            "inteligencia": b["inteligencia"] + m["inteligencia"],
            "puntos_vida": b["puntos_vida"] + m["puntos_vida"],
            "estres": b["estres"] + m["estres"],
        }

    # -------------------------
    # HP / STATE
    # -------------------------

    @property
    def hp_current(self) -> int:
        return int(self.character.state.hp_current)

    @hp_current.setter
    def hp_current(self, v: int) -> None:
        self.character.state.hp_current = max(0, int(v))

    @property
    def hp_max(self) -> int:
        """
        Regla HP (MVP determinista):
          base_hp = 10 + level * 5
          hp_max = base_hp + puntos_vida_efectivos
        """
        eff = self.effective
        level = int(eff["level"])
        pv = int(eff["puntos_vida"])
        base_hp = 10 + level * 5
        return max(1, base_hp + pv)

    # -------------------------
    # EQUIP / UNEQUIP / DROP
    # -------------------------

    def is_equipped(self, slot: str) -> bool:
        return self.equipped_items.get(slot) is not None

    def equip(self, *, item: ItemModel, slot: str) -> Optional[ItemModel]:
        """
        Devuelve el item anterior si había (swap).
        """
        return self.eq.equip(self.character, item=item, slot=slot)

    def unequip(self, *, slot: str) -> Optional[ItemModel]:
        return self.eq.unequip(self.character, slot=slot)

    def drop(self, *, slot: str) -> Optional[ItemModel]:
        """
        Para “desarmar / soltar”.
        En tu sistema, soltar = sacar de equipped.
        (Moverlo al suelo/inventario lo decide el motor luego.)
        """
        return self.unequip(slot=slot)

    # -------------------------
    # ATTACKS INTERPRETATION
    # -------------------------

    def _attack_from_weapon(self, weapon: ItemModel, *, hand: str) -> Optional[AttackProfile]:
        if not weapon.damage:
            return None  # escudos / armaduras no atacan

        # Defaults porque tu catálogo aún no tiene estos campos:
        damage_type = getattr(weapon, "damage_type", None) or "physical"
        rng = getattr(weapon, "range", None) or 1

        # Bonus simple por calidad (MVP):
        to_hit_bonus = int(weapon.quality or 0)

        # Elegir stat para el ataque:
        # MVP: si el arma da más destreza que fuerza -> usa destreza, sino fuerza.
        sm = weapon.stat_modifiers
        stat_key = "destreza" if int(sm.destreza) > int(sm.fuerza) else "fuerza"

        return AttackProfile(
            id=weapon.id,
            name=weapon.name,
            hand=hand,
            damage_dice=str(weapon.damage),
            damage_type=str(damage_type),
            range=int(rng),
            stat_key=stat_key,
            to_hit_bonus=to_hit_bonus,
        )

    @property
    def main_hand_weapon(self) -> Optional[ItemModel]:
        return self.equipped_items.get("arma_derecha")

    @property
    def off_hand_weapon(self) -> Optional[ItemModel]:
        return self.equipped_items.get("arma_izquierda")

    @property
    def main_hand_attack(self) -> AttackProfile:
        w = self.main_hand_weapon
        if w:
            atk = self._attack_from_weapon(w, hand="main")
            if atk:
                return atk

        # unarmed fallback
        return AttackProfile(
            id="unarmed",
            name="Golpe sin arma",
            hand="unarmed",
            damage_dice="1d2",
            damage_type="blunt",
            range=1,
            stat_key="fuerza",
            to_hit_bonus=0,
        )

    @property
    def off_hand_attack(self) -> Optional[AttackProfile]:
        w = self.off_hand_weapon
        if not w:
            return None
        return self._attack_from_weapon(w, hand="off")

    @property
    def available_attacks(self) -> List[AttackProfile]:
        out = [self.main_hand_attack]
        off = self.off_hand_attack
        if off:
            out.append(off)
        return out

    # -------------------------
    # D&D-ish mods exposed
    # -------------------------

    @property
    def initiative_mod(self) -> int:
        # D&D: Dex mod
        return ability_mod(self.effective["destreza"])
