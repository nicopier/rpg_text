from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from combat_engine.actions_provider import available_action_options, valid_attack_targets
from combat_engine.end_conditions import evaluate_end_conditions
from combat_engine.models import ActionIntent
from combat_engine.resolver import resolve_turn
from combat_engine.session import InMemoryCombatSessions

from ia_engine.gpt_engine.gpt_engine import LLMEngine
from ia_engine.prompts.combat.planner_service import CombatPlannerService
from ia_engine.prompts.combat.narrator_service import CombatNarratorService

logger = logging.getLogger(__name__)

_SESS: Optional[InMemoryCombatSessions] = None
_PLANNER: Optional[CombatPlannerService] = None
_NARRATOR: Optional[CombatNarratorService] = None


def _get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _get_sessions() -> InMemoryCombatSessions:
    global _SESS
    if _SESS is None:
        _SESS = InMemoryCombatSessions(project_root=_get_project_root())
    return _SESS


def _pick_character_id(update: Update) -> str:
    if update.effective_user and update.effective_user.username:
        return update.effective_user.username
    if update.effective_user:
        return str(update.effective_user.id)
    return "Nico"


def _render_state_line(state) -> str:
    parts = [f"Turno {state.turn_number}"]

    # player(s)
    for eid, e in state.entities.items():
        if e.team == "players":
            parts.append(f"🧑 {eid}: HP {e.hp_current}/{e.hp_max} AC {e.ac}")

    # enemies alive
    for eid, e in state.entities.items():
        if e.team == "enemies" and e.hp_current > 0:
            parts.append(f"👹 {eid}: HP {e.hp_current}/{e.hp_max} AC {e.ac}")

    return "\n".join(parts)


def _keyboard_actions(update: Update) -> InlineKeyboardMarkup:
    sessions = _get_sessions()
    sess = sessions.get(update.effective_chat.id)  # type: ignore[arg-type]
    if not sess:
        return InlineKeyboardMarkup([])

    player = sess.state.entities.get(sess.player_character_id)
    if not player:
        return InlineKeyboardMarkup([])

    rows = []
    for opt in available_action_options(player):
        rows.append([InlineKeyboardButton(opt.label, callback_data=f"cmb:act:{opt.action_id}")])
    return InlineKeyboardMarkup(rows)


def _keyboard_targets(update: Update) -> InlineKeyboardMarkup:
    sessions = _get_sessions()
    sess = sessions.get(update.effective_chat.id)  # type: ignore[arg-type]
    if not sess:
        return InlineKeyboardMarkup([])

    targets = valid_attack_targets(sess.state, attacker_id=sess.player_character_id)
    rows = [[InlineKeyboardButton(t, callback_data=f"cmb:tgt:{t}")] for t in targets]
    rows.append([InlineKeyboardButton("✅ Confirmar", callback_data="cmb:confirm")])
    rows.append([InlineKeyboardButton("⬅️ Atrás", callback_data="cmb:back")])
    return InlineKeyboardMarkup(rows)


def _get_planner_narrator() -> Tuple[Optional[CombatPlannerService], Optional[CombatNarratorService]]:
    """
    Importante:
    - Si falla una vez (API key, red, etc.), NO cacheamos None para siempre.
    - Reintenta en el próximo turno.
    """
    global _PLANNER, _NARRATOR

    if _PLANNER is not None and _NARRATOR is not None:
        return _PLANNER, _NARRATOR

    try:
        engine = LLMEngine()
        _PLANNER = CombatPlannerService(llm_engine=engine)
        _NARRATOR = CombatNarratorService(llm_engine=engine)
        return _PLANNER, _NARRATOR
    except Exception:
        logger.exception("LLM init failed (planner/narrator). Running without LLM for this turn.")
        # NO cacheamos el fallo, dejamos en None pero permitimos reintento
        _PLANNER = None
        _NARRATOR = None
        return None, None


async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/fight - arranca un combate demo contra characters/bad_boys.json"""
    if not update.message:
        return

    sessions = _get_sessions()
    chat_id = update.effective_chat.id  # type: ignore[union-attr]
    char_id = _pick_character_id(update)

    try:
        sess = sessions.start_demo(chat_id=chat_id, player_character_id=char_id)
    except Exception:
        logger.exception("Failed to start demo with %s, falling back to Nico", char_id)
        sess = sessions.start_demo(chat_id=chat_id, player_character_id="Nico")

    await update.message.reply_text(
        "⚔️ ¡Arranca el combate!\n" + _render_state_line(sess.state),
        reply_markup=_keyboard_actions(update),
    )


async def combat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """CallbackQuery handler para combate."""
    if not update.callback_query:
        return

    q = update.callback_query
    await q.answer()

    data = (q.data or "").strip()
    if not data.startswith("cmb:"):
        return

    sessions = _get_sessions()
    chat_id = update.effective_chat.id  # type: ignore[union-attr]
    sess = sessions.get(chat_id)
    if not sess:
        await q.edit_message_text("No hay combate activo. Usá /fight.")
        return

    parts = data.split(":")
    kind = parts[1] if len(parts) > 1 else ""
    value = parts[2] if len(parts) > 2 else ""

    # --- seleccionar acción
    if kind == "act":
        sessions.set_pending(chat_id, action_id=value)
        if value == "ATTACK":
            await q.edit_message_text("Elegí objetivo:", reply_markup=_keyboard_targets(update))
        else:
            await q.edit_message_text(
                f"Acción seleccionada: {value}. ¿Confirmar?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("✅ Confirmar", callback_data="cmb:confirm")],
                        [InlineKeyboardButton("⬅️ Atrás", callback_data="cmb:back")],
                    ]
                ),
            )
        return

    # --- seleccionar target
    if kind == "tgt":
        sessions.set_pending(chat_id, target_id=value)
        await q.edit_message_text(
            f"Objetivo: {value}\n¿Confirmar?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("✅ Confirmar", callback_data="cmb:confirm")],
                    [InlineKeyboardButton("⬅️ Atrás", callback_data="cmb:back")],
                ]
            ),
        )
        return

    # --- volver
    if kind == "back":
        sess.pending = {}
        await q.edit_message_text(_render_state_line(sess.state), reply_markup=_keyboard_actions(update))
        return

    # --- confirmar turno
    if kind == "confirm":
        # 1) player intent
        p_intent = sessions.consume_pending_intent(chat_id)
        if not p_intent:
            await q.edit_message_text("Primero elegí una acción.", reply_markup=_keyboard_actions(update))
            return

        before = sess.state
        player_id = sess.player_character_id

        if player_id not in before.entities:
            # Esto te salva de ids mal alineados
            logger.error("player_id %s no está en state.entities: %s", player_id, list(before.entities.keys()))
            await q.edit_message_text("Error interno: player_id no encontrado. Reiniciá con /fight.")
            return

        # 2) enemy intents
        planner, narrator = _get_planner_narrator()
        logger.info("Planner: %s | Narrator: %s", "ON" if planner else "OFF", "ON" if narrator else "OFF")

        enemy_intents: list[ActionIntent] = []

        if planner:
            state_summary = {
                "turn": before.turn_number,
                "players": [
                    {
                        "id": player_id,
                        "hp": before.entities[player_id].hp_current,
                        "ac": before.entities[player_id].ac,
                    }
                ],
                "enemies": [
                    {
                        "id": eid,
                        "hp": before.entities[eid].hp_current,
                        "ac": before.entities[eid].ac,
                    }
                    for eid in before.alive_ids(team="enemies")
                ],
                "valid_targets": {eid: [player_id] for eid in before.alive_ids(team="enemies")},
            }

            try:
                enemy_raw = planner.plan(state_summary=state_summary)
            except Exception:
                logger.exception("Planner failed. Falling back to deterministic enemy intents.")
                enemy_raw = []

            if enemy_raw:
                for it in enemy_raw:
                    try:
                        actor_id = str(it.get("actor_id"))
                        action_id = str(it.get("action_id"))
                        target_id = it.get("target_id")

                        if actor_id not in before.entities:
                            continue
                        if action_id not in ("ATTACK", "DEFEND", "PASS"):
                            continue
                        if action_id == "ATTACK" and (not target_id or target_id not in before.entities):
                            continue

                        enemy_intents.append(
                            ActionIntent(actor_id=actor_id, action_id=action_id, target_id=target_id)
                        )
                    except Exception:
                        continue

        # fallback si no hubo planner o devolvió basura
        if not enemy_intents:
            enemy_intents = [
                ActionIntent(actor_id=eid, action_id="ATTACK", target_id=player_id)
                for eid in before.alive_ids(team="enemies")
            ]

        intents = [p_intent, *enemy_intents]

        # 3) resolver turno (engine manda)
        after = resolve_turn(before, intents=intents)
        sess.state = after

        # 4) end conditions
        status = evaluate_end_conditions(after, player_id=player_id)

        if status != "ongoing":
            if status == "defeat":
                text_out = "💀 GAME OVER\nTu vida llegó a 0.\n\n" + _render_state_line(after)
            else:
                text_out = "🏆 VICTORIA\nNo quedan enemigos vivos.\n\n" + _render_state_line(after)

            sessions._sessions.pop(chat_id, None)
            await q.edit_message_text(text_out)
            return

        # 5) narración (una vez por turno)
        narration: Optional[str] = None
        if narrator:
            # Evitar crash si after.events no existe
            events = getattr(after, "events", [])
            payload = {
                "turn": before.turn_number,
                "intents": [i.__dict__ for i in intents],
                "events": [{"type": e.type, "payload": e.payload} for e in events],
                "state_after": {
                    "entities": {
                        eid: {
                            "hp": ent.hp_current,
                            "hp_max": ent.hp_max,
                            "ac": ent.ac,
                            "team": ent.team,
                        }
                        for eid, ent in after.entities.items()
                    }
                },
            }

            try:
                narration = narrator.narrate(turn_payload=payload)
            except Exception:
                logger.exception("Narrator failed. Continuing without narration.")
                narration = None

        text_out = (("📣 " + narration + "\n\n") if narration else "")
        text_out += _render_state_line(after)

        await q.edit_message_text(text_out, reply_markup=_keyboard_actions(update))
        return
