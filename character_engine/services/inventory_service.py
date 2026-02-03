from __future__ import annotations

from character_engine.errors import ItemNotFound
from character_engine.models.character import CharacterModel
from character_engine.models.item import ItemModel

class InventoryService:
    def list_items(self, character: CharacterModel) -> list[ItemModel]:
        return list(character.inventory.items)

    def get_item(self, character: CharacterModel, item_id: str) -> ItemModel | None:
        for it in character.inventory.items:
            if it.id == item_id:
                return it
        return None

    def add_item(self, character: CharacterModel, item: ItemModel) -> None:
        character.inventory.items.append(item)

    def remove_item(self, character: CharacterModel, item_id: str) -> ItemModel:
        for idx, it in enumerate(character.inventory.items):
            if it.id == item_id:
                return character.inventory.items.pop(idx)
        raise ItemNotFound(f"No encontré item '{item_id}' en inventario")
