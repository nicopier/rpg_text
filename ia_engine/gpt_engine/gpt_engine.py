from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from openai import OpenAI


class LLMEngine:
    """
    Engine simple (NO Azure).
    Lee env:
      - OPENAI_API_KEY (obligatoria)
      - MODEL_NAME (default: gpt-4o-mini)
    """

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta OPENAI_API_KEY en el entorno (.env).")

        self.model = os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.client = OpenAI(api_key=api_key)

    def chat(
        self,
        *,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_output_tokens: int = 700,
    ) -> str:
        resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
                response_format={"type": "json_object"},
            )

        return resp.choices[0].message.content or ""
