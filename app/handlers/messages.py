from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Repite el texto del usuario (ejemplo simple).
    """
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Catch-all para comandos no reconocidos.
    """
    if update.message:
        await update.message.reply_text("No conozco ese comando. Probá /help.")
