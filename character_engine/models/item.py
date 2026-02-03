from __future__ import annotations

from typing import Optional, Literal, Dict
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

# Slots del juego (los tuyos)
SlotName = Literal[
    "casco",
    "pecho",
    "botas",
    "arma_derecha",
    "arma_izquierda",
    "anillo_derecho",
    "anillo_izquierdo",
    "cualquier_mano",
]

class StatModifiersModel(BaseModel):
    """Modificadores que aporta un item cuando está equipado."""
    fuerza: int = 0
    destreza: int = 0
    inteligencia: int = 0
    puntos_vida: int = 0   # base
    estres: int = 0        # base

class ItemTemplateModel(BaseModel):
    """Plantilla del catálogo (items.json). No tiene id."""
    model_config = ConfigDict(extra="forbid")

    name: str
    slot: SlotName
    weight: float
    quality: int = Field(ge=0)
    damage: Optional[str] = None
    stat_modifiers: StatModifiersModel = Field(default_factory=StatModifiersModel)
    description: Optional[str] = None

class ItemModel(BaseModel):
    """Instancia (inventario o equipado). Tiene id único."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    name: str
    slot: SlotName
    weight: float
    quality: int = Field(ge=0)
    damage: Optional[str] = None
    stat_modifiers: StatModifiersModel = Field(default_factory=StatModifiersModel)
    description: Optional[str] = None

    @classmethod
    def from_template(cls, tpl: ItemTemplateModel) -> "ItemModel":
        # Clona un template del catálogo y genera id
        return cls(
            name=tpl.name,
            slot=tpl.slot,
            weight=tpl.weight,
            quality=tpl.quality,
            damage=tpl.damage,
            stat_modifiers=tpl.stat_modifiers,
            description=tpl.description,
        )
