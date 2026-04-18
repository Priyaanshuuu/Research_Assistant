#!/bin/bash
set -e

echo "🚀 Setting up Research Assistant..."

# --- Prerequisites ---
command -v node  >/dev/null 2>&1 || { echo "❌  Node.js required → https://nodejs.org"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌  Python 3.11+ required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌  Docker required → https://docs.docker.com/get-docker/"; exit 1; }
echo "✅  Prerequisites OK"

# --- .env ---
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅  .env created from .env.example — fill in API keys before starting"
fi

# --- Backend directory tree ---
echo "📁  Scaffolding backend structure..."
mkdir -p backend/core \
         backend/agents/nodes \
         backend/tools \
         backend/services \
         backend/db/migrations/versions \
         backend/api/routes

# Python package markers
touch backend/__init__.py \
      backend/core/__init__.py \
      backend/agents/__init__.py \
      backend/agents/nodes/__init__.py \
      backend/tools/__init__.py \
      backend/services/__init__.py \
      backend/db/__init__.py \
      backend/api/__init__.py \
      backend/api/routes/__init__.py
echo "✅  Backend structure created"

# --- Next.js 14 frontend scaffold ---
if [ ! -f frontend/package.json ]; then
  echo "📦  Scaffolding Next.js 14 (takes 2-3 min)..."
  npx create-next-app@14 frontend \
    --typescript \
    --tailwind \
    --eslint \
    --app \
    --no-src-dir \
    --import-alias "@/*" \
    --yes

  # We use next.config.ts — remove what create-next-app generated
  rm -f frontend/next.config.mjs frontend/next.config.js
  echo "✅  Next.js scaffold complete"
else
  echo "⏭️   frontend/ already exists — skipping scaffold"
fi

# --- Additional frontend dependencies ---
echo "📦  Installing additional frontend packages..."
cd frontend
npm install \
  next-auth@beta \
  "@tanstack/react-query@^5" \
  axios \
  clsx \
  tailwind-merge \
  lucide-react \
  "@radix-ui/react-slot" \
  class-variance-authority
cd ..
echo "✅  Frontend dependencies installed"

echo ""
echo "🎉  Scaffold complete!"
echo "   1. Fill in .env with your API keys"
echo "   2. Create all project files shown in the guide"
echo "   3. Run: docker-compose up --build"