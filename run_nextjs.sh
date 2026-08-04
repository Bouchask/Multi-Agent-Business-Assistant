#!/usr/bin/env bash
set -e

echo "============================================================"
echo "✨ LAUNCHING NEXT.JS REACT FRONTEND WITH GEMINI AESTHETICS ✨"
echo "============================================================"
echo "Checking directory and dependencies..."

cd /Users/ggffghg/Desktop/Multi-Agent-Business-Assistant/frontend_nextjs
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

echo "🚀 Starting Next.js Dev Server on http://localhost:3000..."
exec npm run dev
