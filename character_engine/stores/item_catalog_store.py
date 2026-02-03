from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from character_engine.models.item import ItemTemplateModel

class ItemCatalogStore:
    """Carga el catálogo global (items.json) y permite buscar."""

    def __init__(self, *, catalog_path: Path) -> None:
        self.catalog_path = catalog_path

    def load_all(self) -> List[ItemTemplateModel]:
        raw = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        items = raw.get("items", [])
        return [ItemTemplateModel.model_validate(x) for x in items]

    def find_by_name(self, name: str) -> List[ItemTemplateModel]:
        needle = name.strip().lower()
        return [it for it in self.load_all() if it.name.strip().lower() == needle]

    def find_one_by_name(self, name: str) -> ItemTemplateModel | None:
        matches = self.find_by_name(name)
        return matches[0] if matches else None

    def filter_by_slot(self, slot: str) -> List[ItemTemplateModel]:
        needle = slot.strip()
        return [it for it in self.load_all() if it.slot == needle]
