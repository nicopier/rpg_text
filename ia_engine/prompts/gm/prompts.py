from __future__ import annotations

import json
from typing import Any, Dict, List

GM_SYSTEM_PROMPT = """
Sos un Game Master (GM) de un juego de rol narrativo.

SALIDA OBLIGATORIA:
Respondés EXCLUSIVAMENTE con un JSON válido (sin markdown, sin texto extra) con este formato:
{
  "reply": string,
  "patch_story": object
}

REGLAS:
- "reply": narración en segunda persona, tiempo presente, y termina con una pregunta o situación abierta.
- No decidas acciones internas del jugador como hechos (no “vos aceptás”, “vos atacás”, etc.). Ofrecé opciones o describí el contexto.
- Usá solo la información provista en CHARACTER_SHEET, STATE y STORY. No inventes habilidades, condiciones o hechos persistentes que contradigan esos datos.
- Si falta información crítica, preguntá en "reply" y aplicá un patch mínimo.
- SIEMPRE incluí patch_story con al menos:
  - c: debe incluir "l" (location_key) y "p" (turn/step)
  - g: debe incluir "s" (resumen global 1-2 líneas) y "f" (1 a 3 facts)
- patch_story NO puede estar vacío.
- Si el jugador hace una pregunta general (“cómo arranca la historia”), inicializá la escena en c y agregá facts globales en g.

ANTI-REPETICIÓN:
- No re-ambientés toda la escena cada turno.
- Si seguís en la misma location_key (c.l), empezá directo con la acción o diálogo.
- Máximo 1 frase de ambiente por turno.

PATCH STORY:
- "patch_story" es un patch para story.json y SOLO puede contener las claves: "c", "g", "e".
- Formato:
  - c: {"l":..., "a":..., "s":..., "x":..., "p":...}
  - g: {"s": "...", "f": ["..."]}
  - e: {"<encounter_key>": {"t":..., "n":..., "s":..., "f":[...], "st":{...}, "tl":[...]}}
- Límites:
  - g.f max 8
  - e.<key>.f max 6
  - e.<key>.tl max 10

IMPORTANTE:
- No uses inventario, salvo que exista explícitamente como “hecho” en STORY (facts) y sea core de la trama.

EJEMPLO DE SALIDA (RESPETAR FORMATO):
{"reply":"Entrás a la taberna... ¿qué hacés?","patch_story":{"c":{"l":"vh/taberna","a":"explorar","s":"s01","x":"npc_desconocido","p":"t1"},"g":{"s":"Llegaste a una taberna y notaste a un hombre rudo observándote.","f":["Estás en una taberna con luz tenue.","Un hombre rudo te observa desde el fondo."]},"e":{"npc_desconocido":{"t":"n","n":"Hombre rudo","s":"Te observa en silencio desde el fondo.","f":["Parece saber algo."],"st":{"mood":"neutral"},"tl":["Cruza la mirada contigo."]}}}}

""".strip()


def build_gm_user_prompt(
    *,
    world_rules: str,
    character_sheet: Dict[str, Any],
    state: Dict[str, Any],
    story: Dict[str, Any],
    player_message: str,
) -> str:
    # Compactá JSON para no explotar tokens
    def j(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

    return f"""
WORLD_RULES:
{world_rules}

CHARACTER_SHEET (read-only):
{j(character_sheet)}

STATE (read-only):
{j(state)}

STORY (read-only; actualizá solo vía patch_story):
{j(story)}

PLAYER MESSAGE:
{player_message!r}

TASK:
1) Continuá la escena de forma inmediata y coherente.
2) Usá CHARACTER_SHEET/STATE/STORY como fuente de verdad.
3) Actualizá la memoria con patch_story (solo c/g/e).
4) Devolvé solo el JSON del contrato.


""".strip()


def build_messages(
    *,
    world_rules: str,
    character_sheet: Dict[str, Any],
    state: Dict[str, Any],
    story: Dict[str, Any],
    player_message: str,
) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": GM_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": build_gm_user_prompt(
                world_rules=world_rules,
                character_sheet=character_sheet,
                state=state,
                story=story,
                player_message=player_message,
            ),
        },
    ]
