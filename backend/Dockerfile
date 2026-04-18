FROM python:3.11-slim

WORKDIR /app

# curl needed for HEALTHCHECK; no gcc needed with psycopg2-binary
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source is bind-mounted at runtime; copy here gives a valid image layer
COPY . .
RUN chmod +x start.sh

HEALTHCHECK --interval=10s --timeout=5s --retries=10 --start-period=30s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["./start.sh"]