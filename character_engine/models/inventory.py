from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, ConfigDict

from character_engine.models.item import ItemModel

class InventoryModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: List[ItemModel] = Field(default_factory=list)
