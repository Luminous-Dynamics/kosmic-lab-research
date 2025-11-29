#!/bin/bash

# Launch script for SAC training using venv (WORKING APPROACH)
# This matches the successful DQN setup
# Usage: ./launch_sac_training_venv.sh

set -e

# Set library path for nix dependencies
ZLIB_PATH=$(ls -d /nix/store/*-zlib-1.*/lib 2>/dev/null | head -1)
if [ -n "$ZLIB_PATH" ]; then
    export LD_LIBRARY_PATH="${ZLIB_PATH}:${LD_LIBRARY_PATH}"
fi

# Activate virtual environment (provides Python packages)
source venv/bin/activate

# Create directories
mkdir -p logs checkpoints/sac

# Launch training for 3 seeds in parallel
echo "================================"
echo "Launching SAC Training (venv)"
echo "================================"
echo "Seeds: 42, 123, 456"
echo "Episodes per seed: 1000"
echo "Environment: MPE Cooperative Navigation"
echo "Algorithm: Soft Actor-Critic (SAC)"
echo "================================"
echo ""

for seed in 42 123 456; do
    echo "Starting SAC training with seed $seed..."

    python ma_sac_trainer.py \
        --exp-name "sac_mpe_seed${seed}" \
        --seed $seed \
        --total-episodes 1000 \
        --save-freq 100 \
        --log-dir "logs" \
        --checkpoint-dir "checkpoints/sac/seed_${seed}" \
        > logs/sac_seed${seed}.log 2>&1 &

    # Store PID
    echo $! > logs/sac_seed${seed}.pid
    echo "  → Seed $seed started (PID: $(cat logs/sac_seed${seed}.pid))"
    echo "  → Log: logs/sac_seed${seed}.log"
    echo ""
done

echo "================================"
echo "All SAC training runs started!"
echo "================================"
echo ""
echo "Monitor progress:"
echo "  tail -f logs/sac_seed42.log"
echo ""
echo "Check running processes:"
echo "  ps aux | grep ma_sac_trainer"
echo ""
echo "Kill all training:"
echo "  pkill -f ma_sac_trainer"
echo ""
