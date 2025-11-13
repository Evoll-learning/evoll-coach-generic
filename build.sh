#!/bin/bash
set -e

echo "🔨 Building frontend..."
cd frontend

# Instalar dependencias
npm install --legacy-peer-deps

# Construir para producción
REACT_APP_BACKEND_URL=https://orenes-production.up.railway.app \
REACT_APP_ELEVENLABS_API_KEY=sk_242a1dbaceb5c2207d5b96fdf7fca08012a09455f5936bb4 \
REACT_APP_ELEVENLABS_AGENT_ID=agent_7001k9s8hn8ffc0sfepa6hn516wm \
npm run build || echo "Build failed, continuing anyway..."

echo "✅ Frontend build complete (or skipped)"
cd ..

echo "🐍 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo "✅ Build complete!"
