from __future__ import annotations

from typing import Any, Dict, List

from ia_engine.prompts.gm._json import extract_first_json_object
from ia_engine.prompts.gm.memory_datamodel import GMMemoryWrite
from ia_engine.prompts.gm.memory_prompts import build_memory_messages

class MemoryWriterService:
    def __init__(self, *, llm_engine: Any) -> None:
        self.llm_engine = llm_engine

    def write(
        self,
        *,
        plan: Dict[str, Any],
        story_current: Dict[str, Any],
        story_summary: str,
        state_min: Dict[str, Any],
        recent_chat: List[Dict[str, str]],
        player_message: str,
        gm_reply: str,
        turn_id: str,
    ) -> GMMemoryWrite:
        messages = build_memory_messages(
            plan=plan,
            story_current=story_current,
            story_summary=story_summary,
            state_min=state_min,
            recent_chat=recent_chat,
            player_message=player_message,
            gm_reply=gm_reply,
            turn_id=turn_id,
        )
        txt = self.llm_engine.chat(messages=messages)
        raw = extract_first_json_object(txt)
        return GMMemoryWrite.model_validate(raw)
