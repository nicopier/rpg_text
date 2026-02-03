from __future__ import annotations

import re
from ia_engine.prompts.gm.datamodel import GMOutput

FORBIDDEN_PATTERNS = [
    r"\bvos (aceptás|aceptas|atacás|atacas|corrés|corres|decidís|decidis)\b",
    r"\btu personaje (hace|decide|acepta)\b",
]

def validate_gm_output(out: GMOutput) -> None:
    txt = out.reply.lower().strip()

    # Heurística simple: que termine en pregunta o situación abierta.
    # (No lo hagas mega estricto al principio)
    if not (txt.endswith("?") or txt.endswith("...")):
        # no rompemos por esto, pero podrías loguearlo
        pass

    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, txt, flags=re.IGNORECASE):
            # Esto sí conviene bloquear para evitar “decidir por el jugador”
            raise ValueError("La respuesta intenta decidir acciones internas del jugador.")
