from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from character_engine.models.stats import StatsModel
from character_engine.models.inventory import InventoryModel
from character_engine.models.state import StateModel
from character_engine.models.story import StoryModel


class CharacterModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stats: StatsModel
    inventory: InventoryModel
    state: StateModel
    story: StoryModel
