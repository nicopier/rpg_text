from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict

class TimeModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: int = Field(ge=1, default=1)
    hour: int = Field(ge=0, le=23, default=0)

class StateModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: str = "start_zone"
    hp_current: int = Field(ge=0, default=10)
    mana_current: int = Field(ge=0, default=0)
    time: TimeModel = Field(default_factory=TimeModel)
