from __future__ import annotations

from typing import Any, Dict, List

from ia_engine.prompts.gm._json import extract_first_json_object
from ia_engine.prompts.gm.planner_datamodel import GMPlan
from ia_engine.prompts.gm.planner_prompts import build_planner_messages

class PlannerService:
    def __init__(self, *, llm_engine: Any) -> None:
        self.llm_engine = llm_engine

    def plan(
        self,
        *,
        story_summary: str,
        state_min: Dict[str, Any],
        recent_chat: List[Dict[str, str]],
        player_message: str,
    ) -> GMPlan:
        messages = build_planner_messages(
            story_summary=story_summary,
            state_min=state_min,
            recent_chat=recent_chat,
            player_message=player_message,
        )
        txt = self.llm_engine.chat(messages=messages)
        raw = extract_first_json_object(txt)
        return GMPlan.model_validate(raw)
