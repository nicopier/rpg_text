from __future__ import annotations

import json
from typing import Dict, Any


def extract_first_json_object(text: str) -> Dict[str, Any]:
    """Extract the first JSON object from a string."""
    start = text.find("{")
    if start == -1:
        raise ValueError("No se encontró '{' en la respuesta del LLM.")

    depth = 0
    in_str = False
    escape = False

    for i in range(start, len(text)):
        ch = text[i]

        if in_str:
            if escape:
                escape = False
            elif ch == "\\":  # backslash
                escape = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                chunk = text[start : i + 1]
                return json.loads(chunk)

    raise ValueError("No se pudo cerrar el JSON (llaves desbalanceadas).")
