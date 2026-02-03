from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from character_engine.models.character import CharacterModel
from character_engine.models.story import StoryModel

from character_engine.stores.story_service import StoryService
from character_engine.stores.character_store import CharacterStore

from ia_engine.prompts.gm.chat_buffer import InMemoryChatBuffer
from ia_engine.prompts.gm.planner_service import PlannerService
from ia_engine.prompts.gm.narrator_service import NarratorService
from ia_engine.prompts.gm.memory_service import MemoryWriterService

@dataclass
class GMResult:
    reply: str
    plan: Dict[str, Any]
    wrote_memory: bool

class GMOrchestrator:
    """
    Pipeline B:
      Planner -> Narrator -> (MemoryWriter opcional)
    """

    def __init__(
        self,
        *,
        llm_engine: Any,
        character_store: CharacterStore,
        story_service: StoryService | None = None,
        chat_buffer: InMemoryChatBuffer | None = None,
    ) -> None:
        self.llm_engine = llm_engine
        self.character_store = character_store
        self.story_service = story_service or StoryService()
        self.chat_buffer = chat_buffer or InMemoryChatBuffer()

        self.planner = PlannerService(llm_engine=llm_engine)
        self.narrator = NarratorService(llm_engine=llm_engine)
        self.memory_writer = MemoryWriterService(llm_engine=llm_engine)

    def run_turn(self, *, character_id: str, player_message: str) -> GMResult:
        # load
        character: CharacterModel = self.character_store.load(character_id)
        story: StoryModel = character.story

        # short-term memory
        session_id = character_id
        recent_chat = self.chat_buffer.get(session_id)

        # minimal state for prompts (no inventory)
        state_min = {
            "location": getattr(character.state, "location", None) or getattr(character.state, "l", None) or None,
            "hp": getattr(character.state, "hp", None),
        }
        story_summary = (story.g.s or "").strip()

        # Planner
        plan_obj = self.planner.plan(
            story_summary=story_summary,
            state_min=state_min,
            recent_chat=recent_chat,
            player_message=player_message,
        )
        plan = plan_obj.model_dump()

        # Narrator
        reply_obj = self.narrator.narrate(
            plan=plan,
            story_summary=story_summary,
            state_min=state_min,
            recent_chat=recent_chat,
            player_message=player_message,
        )
        reply = reply_obj.reply.strip()

        # update chat buffer
        self.chat_buffer.append(session_id, role="user", content=player_message)
        self.chat_buffer.append(session_id, role="assistant", content=reply)

        wrote_memory = False

        # MemoryWriter (only if plan says close)
        turn_id = f"t{(int((story.c.p or 't0')[1:]) + 1) if str(story.c.p).startswith('t') else 1}"
        if plan.get("event_close") is True:
            mw = self.memory_writer.write(
                plan=plan,
                story_current=story.model_dump(),
                story_summary=story_summary,
                state_min=state_min,
                recent_chat=self.chat_buffer.get(session_id),
                player_message=player_message,
                gm_reply=reply,
                turn_id=turn_id,
            )
            if mw.should_write and mw.patch_story:
                # apply patch (merge)
                self.story_service.apply_llm_patch(story, mw.patch_story)
                character.story = story
                self.character_store.save(character_id, character)
                wrote_memory = True

        return GMResult(reply=reply, plan=plan, wrote_memory=wrote_memory)
