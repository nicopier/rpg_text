from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from character_engine.errors import CharacterNotFound
from character_engine.models.character import CharacterModel
from character_engine.models.stats import StatsModel
from character_engine.models.inventory import InventoryModel
from character_engine.models.state import StateModel
from character_engine.models.story import StoryModel
from character_engine.stores._env import get_characters_root


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write_json(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


class CharacterStore:
    """
    Carga/guarda un personaje en disco.

    Archivos por personaje:
      - stats.json
      - inventory.json
      - state.json
      - story.json   (NUEVO)
    """

    def __init__(self, *, project_root: Path) -> None:
        self.project_root = project_root
        self.characters_root = get_characters_root(project_root)
        self.characters_root.mkdir(parents=True, exist_ok=True)

    def character_dir(self, name: str) -> Path:
        return self.characters_root / name

    def load(self, name: str) -> CharacterModel:
        cdir = self.character_dir(name)
        if not cdir.exists():
            raise CharacterNotFound(f"No existe el personaje '{name}' ({cdir})")

        stats_path = cdir / "stats.json"
        inv_path = cdir / "inventory.json"
        state_path = cdir / "state.json"
        story_path = cdir / "story.json"

        if not (stats_path.exists() and inv_path.exists() and state_path.exists()):
            raise CharacterNotFound(f"Personaje '{name}' incompleto: faltan JSON base en {cdir}")

        stats = StatsModel.model_validate(_read_json(stats_path))
        inventory = InventoryModel.model_validate(_read_json(inv_path))
        state = StateModel.model_validate(_read_json(state_path))

        # story.json puede no existir para personajes viejos -> default
        if story_path.exists():
            story = StoryModel.model_validate(_read_json(story_path))
        else:
            story = StoryModel.default()
            # opcional: lo creamos en disco para “migrar” automáticamente
            _atomic_write_json(story_path, story.model_dump())

        return CharacterModel(stats=stats, inventory=inventory, state=state, story=story)

    def save(self, name: str, character: CharacterModel) -> None:
        cdir = self.character_dir(name)
        cdir.mkdir(parents=True, exist_ok=True)

        _atomic_write_json(cdir / "stats.json", character.stats.model_dump())
        _atomic_write_json(cdir / "inventory.json", character.inventory.model_dump())
        _atomic_write_json(cdir / "state.json", character.state.model_dump())
        _atomic_write_json(cdir / "story.json", character.story.model_dump())
