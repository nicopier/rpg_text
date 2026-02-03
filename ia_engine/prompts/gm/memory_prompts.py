from __future__ import annotations

import json
from typing import Any, Dict, List

MEMORY_SYSTEM = """
Sos el MEMORY WRITER del juego. No escribís narrativa.
Tu tarea es actualizar SOLO la memoria de largo plazo (story.json) cuando corresponde.

SALIDA OBLIGATORIA: devolvés SOLO JSON:
{
  "should_write": true|false,
  "patch_story": { "c": {...}, "g": {...}, "e": {...} }
}

REGLAS:
- Si plan.event_close es false => should_write=false y patch_story={} (vacío).
- Si plan.event_close es true => should_write=true y patch_story con:
  - c.l (location_key) y c.p (turn)
  - g.s (resumen global corto)
  - g.f (facts persistentes, 1-4)
  - e: solo encounters relevantes (NPC/quest) con nombre, resumen y facts.
- No guardes paja de ambiente repetida. Guardá hechos útiles.
""".strip()

def _j(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def build_memory_messages(
    *,
    plan: Dict[str, Any],
    story_current: Dict[str, Any],
    story_summary: str,
    state_min: Dict[str, Any],
    recent_chat: List[Dict[str, str]],
    player_message: str,
    gm_reply: str,
    turn_id: str,
) -> List[Dict[str, str]]:
    user_payload = {
        "plan": plan,
        "turn_id": turn_id,
        "story_current": story_current,
        "story_summary": story_summary,
        "state_min": state_min,
        "recent_chat": recent_chat,
        "player_message": player_message,
        "gm_reply": gm_reply,
    }
    return [
        {"role": "system", "content": MEMORY_SYSTEM},
        {"role": "user", "content": _j(user_payload)},
    ]
