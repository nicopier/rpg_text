from __future__ import annotations

from dataclasses import dataclass
from typing import List

from combat_engine.models import CombatState, CombatEntity, ActionId


@dataclass(frozen=True)
class ActionOption:
    action_id: ActionId
    label: str
    requires_target: bool = False


def available_action_options(entity: CombatEntity) -> List[ActionOption]:
    opts: List[ActionOption] = []

    # ATTACK si tiene arma o igual permitimos puño
    opts.append(ActionOption(action_id="ATTACK", label="⚔️ Atacar", requires_target=True))
    if entity.has_shield:
        opts.append(ActionOption(action_id="DEFEND", label="🛡️ Defender"))

    opts.append(ActionOption(action_id="PASS", label="⏭️ Pasar"))
    return opts


def valid_attack_targets(state: CombatState, *, attacker_id: str) -> List[str]:
    attacker = state.entities.get(attacker_id)
    if not attacker:
        return []
    enemy_team = "enemies" if attacker.team == "players" else "players"
    return state.alive_ids(team=enemy_team)
