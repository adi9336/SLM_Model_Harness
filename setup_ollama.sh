#!/usr/bin/env bash
set -e

echo "======================================================="
echo "   Two-Level Agent: Local Ollama & xLAM Setup"
echo "======================================================="

# 1. Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "[1/3] Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "[1/3] Ollama is already installed: $(which ollama)"
fi

# 2. Check if Ollama daemon is running
echo ""
echo "[2/3] Checking Ollama daemon (localhost:11434)..."
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
    echo "      Starting Ollama daemon in background..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
    echo "      Ollama daemon is now running on port 11434."
else
    echo "      Ollama daemon is active on port 11434."
fi

# 3. Pull xLAM 1B model
echo ""
echo "[3/3] Pulling local xLAM 1B tool-formatter model..."
echo "      Model: allenporter/xlam:1b..."
ollama pull allenporter/xlam:1b
ollama cp allenporter/xlam:1b xlam:1b 2>/dev/null || true
ollama cp allenporter/xlam:1b xlam2:1b-fc-q4 2>/dev/null || true

echo ""
echo "======================================================="
echo "   Setup Complete! Local xLAM is ready on Ollama."
echo "   Every run will now route Level 2 formatting locally!"
echo "======================================================="

