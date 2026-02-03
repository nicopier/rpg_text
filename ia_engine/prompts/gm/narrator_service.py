from __future__ import annotations

from typing import Any, Dict, List

from ia_engine.prompts.gm._json import extract_first_json_object
from ia_engine.prompts.gm.narrator_datamodel import GMReply
from ia_engine.prompts.gm.narrator_prompts import build_narrator_messages

class NarratorService:
    def __init__(self, *, llm_engine: Any) -> None:
        self.llm_engine = llm_engine

    def narrate(
        self,
        *,
        plan: Dict[str, Any],
        story_summary: str,
        state_min: Dict[str, Any],
        recent_chat: List[Dict[str, str]],
        player_message: str,
    ) -> GMReply:
        messages = build_narrator_messages(
            plan=plan,
            story_summary=story_summary,
            state_min=state_min,
            recent_chat=recent_chat,
            player_message=player_message,
        )
        txt = self.llm_engine.chat(messages=messages)
        raw = extract_first_json_object(txt)
        return GMReply.model_validate(raw)
