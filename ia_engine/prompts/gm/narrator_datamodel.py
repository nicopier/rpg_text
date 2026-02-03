from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict

class GMReply(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply: str = Field(..., min_length=1)
