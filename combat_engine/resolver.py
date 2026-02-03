from __future__ import annotations

from dataclasses import replace
from typing import List

from combat_engine.models import ActionIntent, CombatState, Event
from combat_engine.rules import compute_attack_roll, compute_damage


def resolve_turn(state: CombatState, *, intents: List[ActionIntent]) -> CombatState:
    """Resuelve un turno completo (MVP determinista).

    Orden de resolución (MVP): en el orden recibido.
    Más adelante: initiative por destreza, estados, etc.
    """
    new_state = CombatState(turn_number=state.turn_number, entities=dict(state.entities), events=[])

    for intent in intents:
        actor = new_state.entities.get(intent.actor_id)
        if not actor or actor.hp_current <= 0:
            continue

        if intent.action_id == "PASS":
            new_state.events.append(Event(type="pass", payload={"actor": actor.id}))
            continue

        if intent.action_id == "DEFEND":
            # MVP: defend = +2 AC hasta fin de turno (no persistimos; lo dejamos en eventos)
            new_state.events.append(Event(type="defend", payload={"actor": actor.id, "ac_bonus": 2}))
            continue

        if intent.action_id == "MOVE":
            if intent.new_pos is None:
                continue
            new_state.entities[actor.id] = replace(actor, pos=intent.new_pos)
            new_state.events.append(Event(type="move", payload={"actor": actor.id, "to": list(intent.new_pos)}))
            continue

        if intent.action_id == "ATTACK":
            if not intent.target_id:
                continue
            target = new_state.entities.get(intent.target_id)
            if not target or target.hp_current <= 0:
                continue

            weapon = actor.weapon
            if not weapon:
                # Sin arma: golpe mínimo
                weapon_quality = 0
                base_damage = 1
                stat_key = "fuerza"
            else:
                weapon_quality = int(weapon.quality)
                base_damage = int(weapon.base_damage)
                stat_key = weapon.stat_key

            stat_val = getattr(actor.stats, stat_key)
            attack_roll = compute_attack_roll(stat=stat_val, quality=weapon_quality)
            hit = attack_roll >= int(target.ac)

            damage = 0
            new_hp = target.hp_current
            if hit:
                damage = compute_damage(base_damage=base_damage, stat=stat_val, quality=weapon_quality)
                new_hp = max(0, target.hp_current - damage)
                new_state.entities[target.id] = replace(target, hp_current=new_hp)

            new_state.events.append(
                Event(
                    type="attack",
                    payload={
                        "actor": actor.id,
                        "target": target.id,
                        "attack_roll": attack_roll,
                        "target_ac": target.ac,
                        "result": "hit" if hit else "miss",
                        "damage": damage,
                        "target_hp_after": new_hp,
                    },
                )
            )

            if hit and new_hp <= 0:
                new_state.events.append(Event(type="death", payload={"who": target.id, "by": actor.id}))

    new_state.turn_number = state.turn_number + 1
    return new_state
