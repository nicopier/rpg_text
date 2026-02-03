from __future__ import annotations

import json
from typing import Any, Dict, List

PLANNER_SYSTEM = """
Sos el PLANNER de un juego de rol narrativo. No escribís historia.
Tu trabajo es decidir el próximo movimiento para que la escena PROGRESE.

SALIDA OBLIGATORIA: devolvés SOLO un JSON con este formato:
{
  "beat": "advance|clarify|reveal|complicate|close_event",
  "intent": "explore|dialog|ask_rumors|quest|combat|meta|other",
  "do": ["..."],
  "avoid": ["..."],
  "next_question": "..." | null,
  "event_close": true|false,
  "active_npc_key": "..." | null,
  "location_key": "..." | null
}

REGLAS:
- Si el jugador ya confirmó una decisión (ej: "sí", "obviamente"), NO repitas la misma pregunta. Elegí beat="advance" o "reveal" y definí una consecuencia/pista concreta en "do".
- Si detectás loop (GM repite pregunta/advertencia), agregá en avoid una etiqueta clara (ej: "repeat_cost_warning") y ordená un avance.
- event_close=true SOLO cuando: se obtuvo una pista concreta, se cerró una conversación, o se cambió de escena.
""".strip()

def _j(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def build_planner_messages(
    *,
    story_summary: str,
    state_min: Dict[str, Any],
    recent_chat: List[Dict[str, str]],
    player_message: str,
) -> List[Dict[str, str]]:
    user_payload = {
        "story_summary": story_summary,
        "state_min": state_min,
        "recent_chat": recent_chat,
        "player_message": player_message,
    }
    return [
        {"role": "system", "content": PLANNER_SYSTEM},
        {"role": "user", "content": _j(user_payload)},
    ]
