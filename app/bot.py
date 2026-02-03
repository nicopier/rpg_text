from __future__ import annotations

import logging

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import Settings
from app.handlers.common import error_handler
from app.handlers.commands import start, help_command, ping
from app.handlers.messages import echo, unknown_command

logger = logging.getLogger(__name__)


def build_application(settings: Settings) -> Application:
    """
    Construye y configura la Application (router de handlers).
    """
    application = ApplicationBuilder().token(settings.telegram_bot_token).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))

    # Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Global error handler
    application.add_error_handler(error_handler)

    logger.info("Application built (env=%s)", settings.app_env)
    return application
