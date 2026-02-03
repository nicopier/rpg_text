from __future__ import annotations

import json
from typing import Any, Dict

from ia_engine.gpt_engine.gpt_engine import LLMEngine


class CombatNarratorService:
    """Narrador del combate.

    Input: resumen del turno + eventos resueltos.
    Output JSON:
      {"narration": "texto..."}
    """

    def __init__(self, *, llm_engine: LLMEngine) -> None:
        self.llm = llm_engine

    def narrate(self, *, turn_payload: Dict[str, Any]) -> str:
        system = (
            "Sos un narrador de combate tipo RPG. "
            "Narrás UNA sola vez por turno, describiendo todo lo que pasó. "
            "No inventes números ni resultados: usá SOLO los eventos y datos provistos. "
            "Devolvé SOLO JSON válido con la clave 'narration'."
        )

        raw = self.llm.chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(turn_payload, ensure_ascii=False)},
            ],
            temperature=0.7,
            max_output_tokens=700,
        )

        try:
            data = json.loads(raw)
            n = data.get("narration")
            if isinstance(n, str) and n.strip():
                return n.strip()
        except Exception:
            pass

        # Fallback sin LLM
        events = turn_payload.get("events") or []
        lines = []
        for ev in events:
            if ev.get("type") == "attack":
                p = ev.get("payload") or {}
                lines.append(
                    f"{p.get('actor')} ataca a {p.get('target')} ({p.get('result')}, daño {p.get('damage')})."
                )
            elif ev.get("type") == "death":
                p = ev.get("payload") or {}
                lines.append(f"{p.get('who')} cae derrotado.")
        return "\n".join(lines) if lines else "El turno pasa sin eventos destacables."
