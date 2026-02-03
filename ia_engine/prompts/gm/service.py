from __future__ import annotations

import json
from typing import Any, Dict

from ia_engine.prompts.gm.datamodel import GMOutput
from ia_engine.prompts.gm.prompts import build_messages
from ia_engine.prompts.gm.validations import validate_gm_output


def _parse_json_strict(text: str) -> Dict[str, Any]:
    # Asumimos que el modelo devuelve JSON puro. Si a veces mete basura,
    # después metemos un "extract first json object".
    return json.loads(text)


class GMService:
    def __init__(
        self,
        *,
        llm_engine: Any,
        story_service: Any,
        character_store: Any,
        world_rules: str,
    ) -> None:
        self.llm_engine = llm_engine
        self.story_service = story_service
        self.character_store = character_store
        self.world_rules = world_rules

    def run_turn(
        self,
        *,
        character_id: str,
        player_message: str,
    ) -> GMOutput:
        # 1) Cargar datos del personaje (tu store actual)
        character = self.character_store.load(character_id)

        # Ajustá estas keys según tu estructura real:
        character_sheet = character["stats"]  # o una view compacta
        state = character["state"]
        story = character["story"]

        # 2) Construir messages
        messages = build_messages(
            world_rules=self.world_rules,
            character_sheet=character_sheet,
            state=state,
            story=story,
            player_message=player_message,
        )

        # 3) Llamar LLM
        llm_text = self.llm_engine.chat(messages=messages)

        # 4) Parsear + validar schema
        raw = _parse_json_strict(llm_text)
        out = GMOutput.model_validate(raw)

        # 5) Validaciones extra (guardrails)
        validate_gm_output(out)

        # 6) Aplicar patch al story.json (SOLO story)
        new_story = self.story_service.apply_llm_patch(story, out.patch_story)
        character["story"] = new_story

        # 7) Guardar
        self.character_store.save(character_id, character)

        return out
