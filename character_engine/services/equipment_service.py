from __future__ import annotations

from character_engine.errors import SlotNotFound, InvalidEquipSlot
from character_engine.models.character import CharacterModel
from character_engine.models.item import ItemModel

_ALLOWED_SLOTS = {
    "casco",
    "pecho",
    "botas",
    "arma_derecha",
    "arma_izquierda",
    "anillo_derecho",
    "anillo_izquierdo",
}

class EquipmentService:
    """Equip/unequip con swap automático (si el slot estaba ocupado)."""

    def _assert_slot(self, slot: str) -> None:
        if slot not in _ALLOWED_SLOTS:
            raise SlotNotFound(f"Slot inválido: {slot}")

    def can_equip_in_slot(self, item: ItemModel, slot: str) -> bool:
        # Permitimos equipar si:
        # - coincide exactamente con el slot, o
        # - el item es "cualquier_mano" y el slot es arma derecha/izquierda
        if item.slot == slot:
            return True
        if item.slot == "cualquier_mano" and slot in ("arma_derecha", "arma_izquierda"):
            return True
        return False

    def equip(self, character: CharacterModel, *, item: ItemModel, slot: str) -> ItemModel | None:
        self._assert_slot(slot)
        if not self.can_equip_in_slot(item, slot):
            raise InvalidEquipSlot(f"El item '{item.name}' (slot={item.slot}) no puede equiparse en {slot}")

        equipped = character.stats.equipped

        # swap automático
        previous: ItemModel | None = getattr(equipped, slot)
        setattr(equipped, slot, item)
        return previous

    def unequip(self, character: CharacterModel, *, slot: str) -> ItemModel | None:
        self._assert_slot(slot)
        equipped = character.stats.equipped
        previous: ItemModel | None = getattr(equipped, slot)
        setattr(equipped, slot, None)
        return previous
