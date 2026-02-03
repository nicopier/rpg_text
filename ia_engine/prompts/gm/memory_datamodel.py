from __future__ import annotations

from typing import Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class GMMemoryWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    should_write: bool = Field(default=False)
    patch_story: Dict[str, Any] = Field(default_factory=dict)
