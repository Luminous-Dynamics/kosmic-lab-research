#!/bin/bash

# Launch script for SAC training using flake.nix (REPRODUCIBLE)
# Usage: ./launch_sac_training.sh

set -e

# Check if we're in flake environment
if [ -z "$IN_NIX_SHELL" ]; then
    echo "Entering flake environment..."
    cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index/experiments/cross_algorithm
    exec nix develop --command bash "$0"
fi

# Create directories
mkdir -p logs checkpoints/sac

# Launch training for 3 seeds in parallel
echo "================================"
echo "Launching SAC Training (Flake)"
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
