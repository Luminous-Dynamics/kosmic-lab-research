#!/bin/bash

# Quick test script for MAPPO
set -e

# Set library path
ZLIB_PATH=$(ls -d /nix/store/*-zlib-1.*/lib 2>/dev/null | head -1)
if [ -n "$ZLIB_PATH" ]; then
    export LD_LIBRARY_PATH="${ZLIB_PATH}:${LD_LIBRARY_PATH}"
fi

# Activate venv
source venv/bin/activate

# Create directories
mkdir -p logs checkpoints/mappo_test

# Test with 2 episodes
echo "Testing MAPPO with 2 episodes..."
python ma_mappo_trainer.py \
    --exp-name "mappo_test" \
    --seed 42 \
    --total-episodes 2 \
    --save-freq 1 \
    --log-dir "logs" \
    --checkpoint-dir "checkpoints/mappo_test"

echo ""
echo "Test complete! Check logs and checkpoints."
