# rpg_text

Bot de Telegram para jugar un RPG de texto con IA. El bot actúa como Game Master: narra la historia, toma decisiones narrativas y mantiene memoria de lo que pasó, todo en base a tus mensajes.

## Arquitectura

El pipeline de cada turno tiene tres etapas independientes, cada una con su propio llamado al LLM:

```
Mensaje del jugador
        │
        ▼
   [ PLANNER ]       → decide el beat narrativo (avanzar, revelar, complicar...)
        │
        ▼
   [ NARRATOR ]      → escribe la respuesta jugable siguiendo el plan
        │
        ▼
  [ MEMORY WRITER ]  → si el evento se cerró, actualiza story.json con hechos persistentes
```

El estado de cada personaje vive en archivos JSON en disco (`characters/<nombre>/`). El combate tiene su propio engine determinístico; el LLM solo narra y planea las intenciones enemigas.

## Módulos

| Carpeta | Responsabilidad |
|---|---|
| `app/` | Bot de Telegram, handlers, config |
| `ia_engine/` | LLM engine (OpenAI) + prompts del GM (planner, narrator, memory) |
| `combat_engine/` | Resolución de combate, reglas, compilación de entidades |
| `character_engine/` | Modelos de personaje, inventario, stats, story; carga/guardado en disco |

## Requisitos

- Python 3.11+
- Token de bot de Telegram ([@BotFather](https://t.me/BotFather))
- API key de OpenAI

## Setup

```bash
# 1. Clonar e instalar dependencias
git clone https://github.com/nicopier/rpg_text.git
cd rpg_text
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu TELEGRAM_BOT_TOKEN y OPENAI_API_KEY

# 3. Correr
python -m app
```

## Variables de entorno

| Variable | Requerida | Default | Descripción |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | — | Token del bot de Telegram |
| `OPENAI_API_KEY` | ✅ | — | API key de OpenAI |
| `MODEL_NAME` | ❌ | `gpt-4o-mini` | Modelo a usar |
| `APP_ENV` | ❌ | `dev` | `dev` o `prod` |
| `LOG_LEVEL` | ❌ | `INFO` | Nivel de logging |
| `CHARACTERS_DIR` | ❌ | `./characters` | Ruta a los personajes |

## Docker

```bash
docker build -t rpg_text .
docker run -e TELEGRAM_BOT_TOKEN=... -e OPENAI_API_KEY=... rpg_text
```

## Estructura de personaje

Cada personaje tiene su carpeta en `characters/<nombre>/` con cuatro archivos:

```
characters/
└── Nico/
    ├── stats.json      # atributos base (nivel, fuerza, destreza, etc.)
    ├── inventory.json  # objetos equipados e inventario
    ├── state.json      # estado actual (HP, maná, localización)
    └── story.json      # memoria persistente de la historia
```

`story.json` es el único archivo que el LLM puede modificar (vía patch). Guarda el resumen global, facts persistentes y el estado de cada encounter.

## Combate

El combate se resuelve de forma determinística: daño, AC y reglas no dependen del LLM. El LLM solo:
- Planea las intenciones de los enemigos (`CombatPlannerService`)
- Narra el resultado del turno (`CombatNarratorService`)

Si el LLM no está disponible, el combate sigue funcionando con lógica de fallback.

## Estado del proyecto

Work in progress. El engine de IA y combate están funcionales; la integración completa con el bot de Telegram está en desarrollo.
