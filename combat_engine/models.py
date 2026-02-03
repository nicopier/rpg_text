from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal, Tuple


Team = Literal["players", "enemies"]
ActionId = Literal["ATTACK", "DEFEND", "MOVE", "PASS"]


@dataclass(frozen=True)
class FinalStats:
    level: int
    fuerza: int
    destreza: int
    inteligencia: int
    puntos_vida: int
    estres: int


@dataclass(frozen=True)
class WeaponProfile:
    id: str
    name: str
    quality: int
    base_damage: int
    # "fuerza" | "destreza" | "inteligencia"
    stat_key: str
    range: int = 1


@dataclass(frozen=True)
class CombatEntity:
    id: str
    team: Team
    race: Optional[str] = None

    stats: FinalStats = field(default_factory=lambda: FinalStats(1, 0, 0, 0, 0, 0))
    hp_max: int = 1
    hp_current: int = 1
    ac: int = 10

    # Simplificamos posiciones para MVP: (x,y) opcional.
    pos: Tuple[int, int] = (0, 0)

    weapon: Optional[WeaponProfile] = None
    has_shield: bool = False


@dataclass(frozen=True)
class ActionIntent:
    actor_id: str
    action_id: ActionId
    # Para ATTACK: target_id
    target_id: Optional[str] = None
    # Para MOVE: new_pos
    new_pos: Optional[Tuple[int, int]] = None
    # Extensible
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Event:
    type: str  # "attack" | "defend" | "move" | "death"...
    payload: Dict[str, Any]


@dataclass
class CombatState:
    turn_number: int = 1
    entities: Dict[str, CombatEntity] = field(default_factory=dict)
    events: List[Event] = field(default_factory=list)

    def alive_ids(self, *, team: Optional[Team] = None) -> List[str]:
        out: List[str] = []
        for eid, e in self.entities.items():
            if e.hp_current <= 0:
                continue
            if team and e.team != team:
                continue
            out.append(eid)
        return out
