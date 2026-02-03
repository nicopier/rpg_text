from __future__ import annotations

import json
from typing import Any, Dict, List

from ia_engine.gpt_engine.gpt_engine import LLMEngine


class CombatPlannerService:
    """Planner de enemigos.

    Devuelve SIEMPRE JSON:
      {"enemy_intents": [{"actor_id":"goblin_1","action_id":"ATTACK","target_id":"Nico"}, ...]}

    El LLM decide *intenciones* (quién ataca a quién, etc.).
    El motor calcula números y resultados.
    """

    def __init__(self, *, llm_engine: LLMEngine) -> None:
        self.llm = llm_engine

    def plan(self, *, state_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        system = (
            "Sos un planner táctico para enemigos en un combate por turnos. "
            "Tenés que devolver SOLO JSON válido. "
            "No inventes ids: usa únicamente los ids provistos. "
            "Acciones válidas: ATTACK, DEFEND, PASS. "
            "Si un enemigo no puede actuar, usa PASS."
        )

        user = {
            "turn": state_summary.get("turn"),
            "players": state_summary.get("players"),
            "enemies": state_summary.get("enemies"),
            "valid_targets": state_summary.get("valid_targets"),
        }

        raw = self.llm.chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
            ],
            temperature=0.2,
            max_output_tokens=400,
        )

        try:
            data = json.loads(raw)
            intents = data.get("enemy_intents")
            if isinstance(intents, list):
                return intents
        except Exception:
            pass

        # Fallback: todos atacan al primer player si existe
        intents_out: List[Dict[str, Any]] = []
        player_ids = [p.get("id") for p in (state_summary.get("players") or []) if p.get("id")]
        target_id = player_ids[0] if player_ids else None
        for e in state_summary.get("enemies") or []:
            eid = e.get("id")
            if eid and target_id:
                intents_out.append({"actor_id": eid, "action_id": "ATTACK", "target_id": target_id})
            elif eid:
                intents_out.append({"actor_id": eid, "action_id": "PASS"})
        return intents_out
