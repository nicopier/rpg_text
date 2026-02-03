from __future__ import annotations

from dataclasses import dataclass
import os


def _getenv(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    return v


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    app_env: str = "dev"
    log_level: str = "INFO"

    @staticmethod
    def from_env() -> "Settings":
        token = _getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise RuntimeError(
                "Falta TELEGRAM_BOT_TOKEN. Creá un .env desde .env.example o exportá la variable."
            )

        return Settings(
            telegram_bot_token=token,
            app_env=_getenv("APP_ENV", "dev") or "dev",
            log_level=_getenv("LOG_LEVEL", "INFO") or "INFO",
        )
