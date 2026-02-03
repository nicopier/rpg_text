from __future__ import annotations

import os
from dotenv import load_dotenv

from app.config import Settings
from app.logging_config import setup_logging
from app.bot import build_application


def main() -> None:
    # Carga .env si existe (no pisa variables ya exportadas en el entorno)
    load_dotenv(override=False)

    settings = Settings.from_env()
    setup_logging(settings.log_level)

    app = build_application(settings)

    # Long polling
    # drop_pending_updates=True evita procesar backlog si el bot estuvo apagado
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
