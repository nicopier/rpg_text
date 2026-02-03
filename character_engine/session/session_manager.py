from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from character_engine.models.character import CharacterModel
from character_engine.stores.character_store import CharacterStore
from character_engine.services.story_service import StoryService


@dataclass
class CharacterSession:
    """
    Sesión runtime: vive mientras Telegram interactúa.
    - Carga una vez
    - Operás en memoria
    - Guardás tras cada acción (commit)
    """
    project_root: Path
    character_name: str
    store: CharacterStore
    story_service: StoryService
    character: CharacterModel

    @classmethod
    def load(cls, *, project_root: Path, character_name: str) -> "CharacterSession":
        store = CharacterStore(project_root=project_root)
        character = store.load(character_name)
        story_service = StoryService(tail_cap=4, facts_cap=12)
        return cls(
            project_root=project_root,
            character_name=character_name,
            store=store,
            story_service=story_service,
            character=character,
        )

    def commit(self) -> None:
        self.store.save(self.character_name, self.character)

    # -------- helpers de alto nivel para storyline --------
    def set_ctx(self, *, l: Optional[str]=None, a: Optional[str]=None, s: Optional[str]=None, x: Optional[str]=None, p: Optional[str]=None) -> None:
        self.story_service.set_context(self.character.story, l=l, a=a, s=s, x=x, p=p)

    def begin_dialog(self, *, npc_id: str, npc_name: str, location_key: str, scene_id: str, step: str="0") -> None:
        self.story_service.set_context(self.character.story, l=location_key, a="d", s=scene_id, x=npc_id, p=step)
        self.story_service.upsert_encounter(self.character.story, encounter_id=npc_id, t="n", n=npc_name)

    def begin_combat(self, *, combat_id: str, combat_name: str, location_key: str, scene_id: str, step: str="0") -> None:
        self.story_service.set_context(self.character.story, l=location_key, a="c", s=scene_id, x=combat_id, p=step)
        self.story_service.upsert_encounter(self.character.story, encounter_id=combat_id, t="c", n=combat_name)

    def log_line(self, text: str) -> None:
        # agrega tail al encounter actual
        enc_id = self.character.story.c.x
        self.story_service.add_tail(self.character.story, encounter_id=enc_id, text=text)

    def apply_story_patch(self, patch: Dict[str, Any]) -> None:
        self.story_service.apply_llm_patch(self.character.story, patch)
