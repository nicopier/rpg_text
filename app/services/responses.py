from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HelpText:
    text: str


def build_help_text() -> HelpText:
    return HelpText(
        text=(
            "Comandos disponibles:\n"
            "/start — bienvenida\n"
            "/help — ayuda\n"
            "/ping — latencia simple\n\n"
            "También podés escribirme cualquier texto y lo voy a repetir (echo)."
        )
    )
