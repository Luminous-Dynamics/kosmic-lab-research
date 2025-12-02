#!/bin/bash

# Launch script for MAPPO training using venv
# Usage: ./launch_mappo_training.sh

set -e

# Set library path for nix dependencies
ZLIB_PATH=$(ls -d /nix/store/*-zlib-1.*/lib 2>/dev/null | head -1)
if [ -n "$ZLIB_PATH" ]; then
    export LD_LIBRARY_PATH="${ZLIB_PATH}:${LD_LIBRARY_PATH}"
fi

# Activate virtual environment
source venv/bin/activate

# Create directories
mkdir -p logs checkpoints/mappo

# Launch training for 3 seeds in parallel
echo "================================"
echo "Launching MAPPO Training"
echo "================================"
echo "Seeds: 42, 123, 456"
echo "Episodes per seed: 1000"
echo "Environment: MPE Cooperative Navigation"
echo "Algorithm: Multi-Agent PPO (MAPPO)"
echo "================================"
echo ""

for seed in 42 123 456; do
    echo "Starting MAPPO training with seed $seed..."

    python ma_mappo_trainer.py \
        --exp-name "mappo_mpe_seed${seed}" \
        --seed $seed \
        --total-episodes 1000 \
        --save-freq 100 \
        --log-dir "logs" \
        --checkpoint-dir "checkpoints/mappo/seed_${seed}" \
        > logs/mappo_seed${seed}.log 2>&1 &

    # Store PID
    echo $! > logs/mappo_seed${seed}.pid
    echo "  → Seed $seed started (PID: $(cat logs/mappo_seed${seed}.pid))"
    echo "  → Log: logs/mappo_seed${seed}.log"
    echo ""
done

echo "================================"
echo "All MAPPO training runs started!"
echo "================================"
echo ""
echo "Monitor progress:"
echo "  tail -f logs/mappo_seed42.log"
echo ""
echo "Check running processes:"
echo "  ps aux | grep ma_mappo_trainer"
echo ""
echo "Kill all training:"
echo "  pkill -f ma_mappo_trainer"
echo ""
