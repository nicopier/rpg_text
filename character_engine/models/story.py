from __future__ import annotations

from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field, ConfigDict

# Tipos compactos (1 letra)
Activity = Literal["e", "d", "c", "s", "t", "r"]  # exploration, dialog, combat, shop, travel, rest
EncounterType = Literal["n", "c", "l", "q", "v"]  # npc, combat, location, quest, event


class StoryContextModel(BaseModel):
    """
    Contexto actual (reanudar sesión):
      l = location_key (ej: "vh/plaza")
      a = activity ("d" dialog, "c" combat, etc)
      s = scene_id (ej: "p03")
      x = encounter_id (ej: "npc_herrero", "cb_mina_ratas_01")
      p = step (ej: "ch1", "turn2", "reward")
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    l: str = Field(default="start", description="location_key")
    a: Activity = Field(default="e", description="activity")
    s: str = Field(default="intro", description="scene_id")
    x: str = Field(default="none", description="encounter_id")
    p: str = Field(default="0", description="step")


class GlobalMemoryModel(BaseModel):
    """
    Memoria global del personaje (para prompt):
      s = summary (1-3 líneas)
      f = facts (lista corta)
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    s: str = Field(default="", description="global summary")
    f: List[str] = Field(default_factory=list, description="global facts/flags")


class EncounterModel(BaseModel):
    """
    Memoria por encuentro:
      t  = type (n/c/l/q/v)
      n  = name (humano)
      s  = summary (1-2 líneas)
      f  = facts cortas
      st = state mini reanudable (dict chiquito)
      tl = tail (últimos 3-5 textos, opcional)
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    t: EncounterType
    n: str
    s: str = ""
    f: List[str] = Field(default_factory=list)
    st: Dict[str, Any] = Field(default_factory=dict)
    tl: List[str] = Field(default_factory=list)


class StoryModel(BaseModel):
    """
    story.json compacto:
      v = schema version
      c = current context
      g = global memory
      e = encounters map (encounter_id -> EncounterModel)
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    v: int = 1
    c: StoryContextModel = Field(default_factory=StoryContextModel)
    g: GlobalMemoryModel = Field(default_factory=GlobalMemoryModel)
    e: Dict[str, EncounterModel] = Field(default_factory=dict)

    @classmethod
    def default(cls) -> "StoryModel":
        return cls()
