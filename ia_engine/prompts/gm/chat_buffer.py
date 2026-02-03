from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, TypedDict

Role = Literal["user", "assistant"]

class ChatMsg(TypedDict):
    role: Role
    content: str

@dataclass
class ChatBufferConfig:
    max_turns: int = 10          # total user+assistant pairs ~10 => ~20 messages max if you store both
    max_chars_per_msg: int = 800 # safety cap

class InMemoryChatBuffer:
    """
    Buffer corto plazo (no persistente):
    - guarda últimos N mensajes por personaje/sesión
    - recorta chars para controlar tokens
    """

    def __init__(self, *, cfg: ChatBufferConfig | None = None) -> None:
        self.cfg = cfg or ChatBufferConfig()
        self._store: Dict[str, List[ChatMsg]] = {}

    def append(self, session_id: str, *, role: Role, content: str) -> None:
        content = (content or "").strip()
        if not content:
            return
        if len(content) > self.cfg.max_chars_per_msg:
            content = content[: self.cfg.max_chars_per_msg] + "…"

        buf = self._store.setdefault(session_id, [])
        buf.append({"role": role, "content": content})

        # cap: we keep at most 2*max_turns messages (user+assistant)
        max_msgs = self.cfg.max_turns * 2
        if len(buf) > max_msgs:
            self._store[session_id] = buf[-max_msgs:]

    def get(self, session_id: str) -> List[ChatMsg]:
        return list(self._store.get(session_id, []))

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
