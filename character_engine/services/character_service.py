from __future__ import annotations

from pathlib import Path

from character_engine.errors import ItemNotFound
from character_engine.models.item import ItemModel
from character_engine.stores.character_store import CharacterStore
from character_engine.stores.item_catalog_store import ItemCatalogStore
from character_engine.services.inventory_service import InventoryService
from character_engine.services.equipment_service import EquipmentService

class CharacterService:
    """Servicios alto nivel, pensados para que Telegram llame directo."""

    def __init__(self, *, project_root: Path, catalog_path: Path) -> None:
        self.store = CharacterStore(project_root=project_root)
        self.catalog = ItemCatalogStore(catalog_path=catalog_path)
        self.inventory = InventoryService()
        self.equipment = EquipmentService()

    # -------- items / inventario --------
    def spawn_item_to_inventory(self, character_name: str, template_name: str) -> ItemModel:
        char = self.store.load(character_name)
        tpl = self.catalog.find_one_by_name(template_name)
        if tpl is None:
            raise ItemNotFound(f"No existe template '{template_name}' en catálogo")

        instance = ItemModel.from_template(tpl)
        self.inventory.add_item(char, instance)
        self.store.save(character_name, char)
        return instance

    def delete_item_from_inventory(self, character_name: str, item_id: str) -> None:
        char = self.store.load(character_name)
        self.inventory.remove_item(char, item_id)
        self.store.save(character_name, char)

    # -------- equipamiento --------
    def equip_item(self, character_name: str, item_id: str, slot: str) -> None:
        char = self.store.load(character_name)

        item = self.inventory.remove_item(char, item_id)  # si no está, explota
        previous = self.equipment.equip(char, item=item, slot=slot)

        if previous is not None:
            # swap: lo viejo vuelve al inventario
            self.inventory.add_item(char, previous)

        self.store.save(character_name, char)

    def unequip_item(self, character_name: str, slot: str) -> None:
        char = self.store.load(character_name)

        previous = self.equipment.unequip(char, slot=slot)
        if previous is not None:
            self.inventory.add_item(char, previous)

        self.store.save(character_name, char)
