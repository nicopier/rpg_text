from __future__ import annotations

class CharacterEngineError(Exception):
    """Base error for character engine."""

class CharacterNotFound(CharacterEngineError):
    pass

class ItemNotFound(CharacterEngineError):
    pass

class SlotNotFound(CharacterEngineError):
    pass

class InvalidEquipSlot(CharacterEngineError):
    pass
