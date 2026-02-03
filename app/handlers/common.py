from __future__ import annotations

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja excepciones no capturadas en handlers.
    """
    logger.exception("Unhandled exception while handling an update", exc_info=context.error)

    # Intento best-effort de avisar al usuario (si aplica)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Ups, ocurrió un error. Probá de nuevo en unos segundos.",
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to send error message to user")
