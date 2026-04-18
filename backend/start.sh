#!/bin/bash
# Needed: waits for Postgres readiness, then runs Alembic, then starts uvicorn.
# Docker's depends_on health check covers Redis; we double-check Postgres here
# because Alembic will fail if the DB isn't fully accepting connections yet.
set -e

echo "⏳  Waiting for PostgreSQL..."
until python - <<'EOF'
import psycopg2, os, sys
try:
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
EOF
do
  echo "  PostgreSQL not ready — sleeping 2s"
  sleep 2
done

echo "✅  PostgreSQL ready"
echo "🔄  Running Alembic migrations..."
alembic upgrade head
echo "✅  Migrations complete"
echo "🚀  Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload