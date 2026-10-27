# Dockerfile — ghl-netsuite-api-appointment (Etapa 1)
# Mismo esquema que Etapas 2 y 3: python:3.11-slim + curl, puerto 8000.

FROM python:3.11-slim

# El servicio registra todo con print(): sin buffer para que los mensajes
# aparezcan en los logs de Coolify en el momento.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# curl: lo usa el healthcheck HTTP de Coolify para pegarle a /health desde
# dentro del contenedor.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py oauth.py netsuite.py mapper.py ghl.py registro_eventos.py ./

EXPOSE 8000

# Health check propio (además del que se configura en Coolify contra /health)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
