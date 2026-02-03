# Telegram Bot (Python) — plantilla modular

Plantilla profesional y modular para crear un bot de Telegram usando **python-telegram-bot** (async).

## Requisitos
- Python **3.10+**
- Token de bot (crealo con **@BotFather** en Telegram)

## Instalación rápida

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

1) Copiá el ejemplo de variables de entorno:

```bash
cp .env.example .env
```

2) Editá `.env` y poné tu `TELEGRAM_BOT_TOKEN`.

## Ejecutar (long polling)

```bash
python -m app
```

## Estructura

- `app/__main__.py`: entrypoint
- `app/bot.py`: crea y configura la Application
- `app/config.py`: configuración (env) + validación
- `app/logging_config.py`: logging consistente
- `app/handlers/`: comandos y handlers
- `app/services/`: lógica de negocio (ejemplo: respuestas)

## Tips
- Para producción suele convenir **webhooks** (no incluido por simplicidad).
- No comitees tu `.env`. Usá secretos del entorno (GitHub Actions, Azure, etc.).
