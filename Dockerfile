FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY .env.example ./  # (opcional) referencia

# Se recomienda inyectar TELEGRAM_BOT_TOKEN como variable de entorno en runtime
CMD ["python", "-m", "app"]
