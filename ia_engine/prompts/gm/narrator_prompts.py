from __future__ import annotations

import json
from typing import Any, Dict, List

NARRATOR_SYSTEM = """
Sos el GM NARRADOR. Tu tarea es escribir la respuesta jugable siguiendo el PLAN.

SALIDA OBLIGATORIA: devolvés SOLO JSON:
{ "reply": string }

REGLAS:
- Segunda persona, tiempo presente. Terminá con una pregunta/elección real.
- Obedecé el plan:
  - ejecutá lo que dice "do"
  - evitá lo que dice "avoid" (especialmente repetir preguntas ya respondidas)
- ANTI-REPETICIÓN: máximo 1 frase de ambiente por turno, luego acción/diálogo.
""".strip()

def _j(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def build_narrator_messages(
    *,
    plan: Dict[str, Any],
    story_summary: str,
    state_min: Dict[str, Any],
    recent_chat: List[Dict[str, str]],
    player_message: str,
) -> List[Dict[str, str]]:
    user_payload = {
        "plan": plan,
        "story_summary": story_summary,
        "state_min": state_min,
        "recent_chat": recent_chat,
        "player_message": player_message,
    }
    return [
        {"role": "system", "content": NARRATOR_SYSTEM},
        {"role": "user", "content": _j(user_payload)},
    ]
