#!/bin/bash

# Launch script for DQN training with multiple seeds
# Usage: ./launch_dqn_training.sh

set -e

# Check if we're in nix shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "Not in nix shell. Entering nix develop environment..."
    cd /srv/luminous-dynamics/kosmic-lab
    exec nix develop --command bash -c "cd docs/papers/paper-6-or-index/experiments/cross_algorithm && ./launch_dqn_training.sh"
fi

# Set library path for nix dependencies (use correct zlib, not zlib-ng)
ZLIB_PATH=$(ls -d /nix/store/*-zlib-1.*/lib 2>/dev/null | head -1)
if [ -n "$ZLIB_PATH" ]; then
    export LD_LIBRARY_PATH="${ZLIB_PATH}:${LD_LIBRARY_PATH}"
fi

# Activate virtual environment (provides Python packages)
source venv/bin/activate

# Create directories
mkdir -p logs checkpoints/dqn

# Launch training for 3 seeds in parallel
echo "================================"
echo "Launching DQN Training"
echo "================================"
echo "Seeds: 42, 123, 456"
echo "Episodes per seed: 1000"
echo "Environment: MPE Cooperative Navigation"
echo "================================"
echo ""

for seed in 42 123 456; do
    echo "Starting training with seed $seed..."

    python ma_dqn_trainer.py \
        --exp-name "dqn_mpe_seed${seed}" \
        --seed $seed \
        --total-episodes 1000 \
        --save-freq 100 \
        --log-dir "logs" \
        --checkpoint-dir "checkpoints/dqn/seed_${seed}" \
        > logs/dqn_seed${seed}.log 2>&1 &

    # Store PID
    echo $! > logs/dqn_seed${seed}.pid
    echo "  → Seed $seed started (PID: $(cat logs/dqn_seed${seed}.pid))"
    echo "  → Log: logs/dqn_seed${seed}.log"
    echo ""
done

echo "================================"
echo "All training runs started!"
echo "================================"
echo ""
echo "Monitor progress:"
echo "  tail -f logs/dqn_seed42.log"
echo ""
echo "Check running processes:"
echo "  ps aux | grep ma_dqn_trainer"
echo ""
echo "Kill all training:"
echo "  ./kill_training.sh"
echo ""
