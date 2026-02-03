from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class NPCCatalogStore:
    """Lee un JSON de templates NPC.

    Espera un archivo estilo:
      characters/bad_boys.json
    con formato:
      {"goblin_1": {...}, "kobold_1": {...}}
    o similar.
    """

    def __init__(self, *, project_root: Path, filename: str = "characters/bad_boys.json") -> None:
        self.path = project_root / filename

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        if not self.path.exists():
            raise FileNotFoundError(f"No existe {self.path}")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("bad_boys.json debe ser un objeto JSON {key: sheet}")
        return data

    def get(self, key: str) -> Dict[str, Any]:
        return self.load_all()[key]
