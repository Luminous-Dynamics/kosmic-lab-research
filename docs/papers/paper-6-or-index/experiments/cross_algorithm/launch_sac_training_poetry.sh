#!/bin/bash

# Launch script for SAC training using Poetry + Nix (PROPER REPRODUCIBLE APPROACH)
# This follows the recommended hybrid pattern from Luminous Dynamics
# Usage: ./launch_sac_training_poetry.sh

set -e

# Check if we're in nix develop shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "Entering nix develop shell..."
    exec nix develop --command bash "$0"
fi

# Now we're in the nix shell with Poetry available
# Poetry manages Python packages, Nix provides system dependencies

# Create directories
mkdir -p logs checkpoints/sac

# Launch training for 3 seeds in parallel
echo "================================"
echo "Launching SAC Training (Poetry + Nix)"
echo "================================"
echo "Seeds: 42, 123, 456"
echo "Episodes per seed: 1000"
echo "Environment: MPE Cooperative Navigation"
echo "Algorithm: Soft Actor-Critic (SAC)"
echo "================================"
echo ""

for seed in 42 123 456; do
    echo "Starting SAC training with seed $seed..."

    poetry run python ma_sac_trainer.py \
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
