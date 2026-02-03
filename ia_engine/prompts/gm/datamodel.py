from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, model_validator

ALLOWED_PATCH_KEYS = {"c", "g", "e"}

class GMOutput(BaseModel):
    reply: str = Field(..., min_length=1)
    patch_story: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_patch_story(self) -> "GMOutput":
        keys = set(self.patch_story.keys())
        extra = keys - ALLOWED_PATCH_KEYS
        if extra:
            raise ValueError(f"patch_story contiene keys no permitidas: {sorted(extra)}")

        # Validación suave de estructura (sin ser ultra estrictos al inicio)
        c = self.patch_story.get("c")
        if c is not None and not isinstance(c, dict):
            raise ValueError("patch_story.c debe ser un dict")
        g = self.patch_story.get("g")
        if g is not None and not isinstance(g, dict):
            raise ValueError("patch_story.g debe ser un dict")
        e = self.patch_story.get("e")
        if e is not None and not isinstance(e, dict):
            raise ValueError("patch_story.e debe ser un dict")

        return self
