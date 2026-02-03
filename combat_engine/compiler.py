from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from character_engine.domain.character_sheet import CharacterSheet
from character_engine.models.character import CharacterModel

from combat_engine.models import CombatEntity, FinalStats, WeaponProfile, Team
from combat_engine.rules import compute_ac, compute_hp_max


def _sum_ac_bonus(equipped: Dict[str, Any]) -> int:
    total = 0
    for it in equipped.values():
        if not it:
            continue
        total += int(it.get("ac_bonus", 0) or 0) if isinstance(it, dict) else int(getattr(it, "ac_bonus", 0) or 0)
    return int(total)


def _pick_weapon_profile(equipped: Dict[str, Any]) -> Optional[WeaponProfile]:
    weapon = equipped.get("arma_derecha")
    if not weapon:
        return None

    # Soportamos dict (npc sheet) o ItemModel (player)
    if isinstance(weapon, dict):
        wid = str(weapon.get("id") or "weapon")
        name = str(weapon.get("name") or wid)
        quality = int(weapon.get("quality", 0) or 0)
        base_damage = int(weapon.get("base_damage", 1) or 1)
        tags = set(weapon.get("tags") or [])
        reach = int(weapon.get("reach_bonus", 0) or 0)
    else:
        wid = str(getattr(weapon, "id", "weapon"))
        name = str(getattr(weapon, "name", wid))
        quality = int(getattr(weapon, "quality", 0) or 0)
        base_damage = int(getattr(weapon, "base_damage", 1) or 1)
        tags = set(getattr(weapon, "tags", []) or [])
        reach = int(getattr(weapon, "reach_bonus", 0) or 0)

    # stat_key según tags
    # - ranged o finesse => destreza
    # - sino fuerza
    stat_key = "destreza" if ("ranged" in tags or "finesse" in tags) else "fuerza"
    rng = 1 + reach
    return WeaponProfile(
        id=wid,
        name=name,
        quality=quality,
        base_damage=base_damage,
        stat_key=stat_key,
        range=rng,
    )


def _has_shield(equipped: Dict[str, Any]) -> bool:
    it = equipped.get("arma_izquierda")
    if not it:
        return False
    kind = it.get("kind") if isinstance(it, dict) else getattr(it, "kind", None)
    tags = set(it.get("tags") or []) if isinstance(it, dict) else set(getattr(it, "tags", []) or [])
    return kind == "shield" or ("shield" in tags)


def compile_from_character_model(
    character: CharacterModel,
    *,
    team: Team,
    character_id: str,
    pos: Tuple[int, int] = (0, 0),
) -> CombatEntity:
    sheet = CharacterSheet(character)
    eff = sheet.effective

    # AC y HP según reglas acordadas
    equipped = sheet.equipped_items
    ac_bonus = _sum_ac_bonus(equipped)
    ac = compute_ac(destreza=int(eff["destreza"]), ac_bonus=ac_bonus)
    hp_max = compute_hp_max(level=int(eff["level"]), puntos_vida=int(eff["puntos_vida"]))
    hp_current = min(int(sheet.hp_current), hp_max) if sheet.hp_current > 0 else hp_max

    stats = FinalStats(
        level=int(eff["level"]),
        fuerza=int(eff["fuerza"]),
        destreza=int(eff["destreza"]),
        inteligencia=int(eff["inteligencia"]),
        puntos_vida=int(eff["puntos_vida"]),
        estres=int(eff["estres"]),
    )

    weapon = _pick_weapon_profile(equipped)

    return CombatEntity(
        id=str(character_id),
        team=team,
        race=getattr(character, "race", None),
        stats=stats,
        hp_max=hp_max,
        hp_current=hp_current,
        ac=ac,
        pos=pos,
        weapon=weapon,
        has_shield=_has_shield(equipped),
    )


def compile_from_sheet_dict(
    sheet: Dict[str, Any],
    *,
    team: Team,
    pos: Tuple[int, int] = (0, 0),
) -> CombatEntity:
    stats_raw = sheet.get("stats") or {}
    equipped = sheet.get("equipped") or {}

    # effective stats = base + mods
    base = {
        "level": int(stats_raw.get("level", 1) or 1),
        "fuerza": int(stats_raw.get("fuerza", 0) or 0),
        "destreza": int(stats_raw.get("destreza", 0) or 0),
        "inteligencia": int(stats_raw.get("inteligencia", 0) or 0),
        "puntos_vida": int(stats_raw.get("puntos_vida", 0) or 0),
        "estres": int(stats_raw.get("estres", 0) or 0),
    }

    mods = {"fuerza": 0, "destreza": 0, "inteligencia": 0, "puntos_vida": 0, "estres": 0}
    for it in equipped.values():
        if not it:
            continue
        sm = it.get("stat_modifiers") or {}
        for k in mods:
            mods[k] += int(sm.get(k, 0) or 0)

    eff = {
        **base,
        "fuerza": base["fuerza"] + mods["fuerza"],
        "destreza": base["destreza"] + mods["destreza"],
        "inteligencia": base["inteligencia"] + mods["inteligencia"],
        "puntos_vida": base["puntos_vida"] + mods["puntos_vida"],
        "estres": base["estres"] + mods["estres"],
    }

    ac_bonus = _sum_ac_bonus(equipped)
    ac = compute_ac(destreza=eff["destreza"], ac_bonus=ac_bonus)
    hp_max = compute_hp_max(level=eff["level"], puntos_vida=eff["puntos_vida"])

    stats = FinalStats(
        level=eff["level"],
        fuerza=eff["fuerza"],
        destreza=eff["destreza"],
        inteligencia=eff["inteligencia"],
        puntos_vida=eff["puntos_vida"],
        estres=eff["estres"],
    )

    return CombatEntity(
        id=str(sheet.get("id") or "npc"),
        team=team,
        race=str(sheet.get("race") or "npc"),
        stats=stats,
        hp_max=hp_max,
        hp_current=hp_max,
        ac=ac,
        pos=pos,
        weapon=_pick_weapon_profile(equipped),
        has_shield=_has_shield(equipped),
    )


def load_npc_catalog(path: Path) -> Dict[str, Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("bad_boys.json debe ser un objeto JSON {key: sheet}")
    return data
