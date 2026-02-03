from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from character_engine.stores.character_store import CharacterStore

from combat_engine.compiler import compile_from_character_model, compile_from_sheet_dict
from combat_engine.models import ActionIntent, CombatState
from combat_engine.stores.npc_catalog_store import NPCCatalogStore


@dataclass
class CombatSession:
    chat_id: int
    player_character_id: str
    state: CombatState
    # selección pendiente (UI)
    pending: Dict[str, Any] = field(default_factory=dict)


class InMemoryCombatSessions:
    def __init__(self, *, project_root: Path) -> None:
        self.project_root = project_root
        self._sessions: Dict[int, CombatSession] = {}
        self.char_store = CharacterStore(project_root=project_root)
        self.npc_store = NPCCatalogStore(project_root=project_root)

    def get(self, chat_id: int) -> Optional[CombatSession]:
        return self._sessions.get(chat_id)

    def start_demo(self, *, chat_id: int, player_character_id: str) -> CombatSession:
        player = self.char_store.load(player_character_id)
        p_entity = compile_from_character_model(player, character_id=player_character_id, team="players", pos=(1, 1))

        catalog = self.npc_store.load_all()
        # Por defecto: goblin_1 y kobold_1 si existen. Si no, usa los primeros 2.
        keys = []
        for k in ("goblin_1", "kobold_1"):
            if k in catalog:
                keys.append(k)
        if len(keys) < 2:
            keys = list(catalog.keys())[:2]

        enemies = []
        for i, k in enumerate(keys):
            sheet = dict(catalog[k])
            sheet["id"] = sheet.get("id") or k
            enemies.append(compile_from_sheet_dict(sheet, team="enemies", pos=(3 + i, 1)))

        state = CombatState(turn_number=1, entities={p_entity.id: p_entity, **{e.id: e for e in enemies}})
        sess = CombatSession(chat_id=chat_id, player_character_id=player_character_id, state=state)
        self._sessions[chat_id] = sess
        return sess

    def set_pending(self, chat_id: int, **kwargs: Any) -> None:
        sess = self._sessions.get(chat_id)
        if not sess:
            return
        sess.pending.update(kwargs)

    def consume_pending_intent(self, chat_id: int) -> Optional[ActionIntent]:
        sess = self._sessions.get(chat_id)
        if not sess:
            return None
        p = sess.pending
        action_id = p.get("action_id")
        if not action_id:
            return None
        actor_id = sess.player_character_id
        intent = ActionIntent(
            actor_id=actor_id,
            action_id=action_id,
            target_id=p.get("target_id"),
        )
        sess.pending = {}
        return intent
    
    