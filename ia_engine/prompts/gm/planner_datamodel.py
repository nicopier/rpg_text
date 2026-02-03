from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

Beat = Literal["advance", "clarify", "reveal", "complicate", "close_event"]
Intent = Literal["explore", "dialog", "ask_rumors", "quest", "combat", "meta", "other"]

class GMPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    beat: Beat = Field(..., description="Qué tipo de movimiento toca ahora.")
    intent: Intent = Field(..., description="Intención dominante del turno.")
    do: List[str] = Field(default_factory=list, description="Acciones narrativas a ejecutar (consecuencia, pista, etc.)")
    avoid: List[str] = Field(default_factory=list, description="Cosas a evitar (ej: repetir la misma pregunta).")
    next_question: Optional[str] = Field(default=None, description="Tipo de pregunta/cierre para el jugador.")
    event_close: bool = Field(default=False, description="Si se cerró un mini-evento y conviene escribir memoria.")
    active_npc_key: Optional[str] = Field(default=None, description="NPC activo si aplica.")
    location_key: Optional[str] = Field(default=None, description="Location actual si aplica.")
