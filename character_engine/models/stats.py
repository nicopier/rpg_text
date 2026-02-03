from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from character_engine.models.item import ItemModel

class StatsBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: int = Field(ge=1, default=1)
    fuerza: int = 1
    destreza: int = 1
    inteligencia: int = 1
    puntos_vida: int = 1   # BASE
    estres: int = 0        # BASE

class EquippedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    casco: Optional[ItemModel] = None
    pecho: Optional[ItemModel] = None
    botas: Optional[ItemModel] = None
    arma_derecha: Optional[ItemModel] = None
    arma_izquierda: Optional[ItemModel] = None
    anillo_derecho: Optional[ItemModel] = None
    anillo_izquierdo: Optional[ItemModel] = None

class StatsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stats: StatsBaseModel
    equipped: EquippedModel
