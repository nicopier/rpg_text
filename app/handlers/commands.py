from __future__ import annotations

import logging
from telegram import Update
from telegram.ext import ContextTypes

from app.services.responses import build_help_text

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /start
    """
    user = update.effective_user
    name = user.first_name if user else "👋"
    await update.message.reply_text(
        f"Hola {name}! Soy tu bot.\n\nEscribí /help para ver comandos."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /help
    """
    help_text = build_help_text()
    await update.message.reply_text(help_text.text)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /ping
    """
    await update.message.reply_text("pong ✅")
