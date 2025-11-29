#!/bin/bash

# Launch script for DQN training using flake.nix (REPRODUCIBLE)
# Usage: ./launch_dqn_training_flake.sh

set -e

# Check if we're in flake environment
if [ -z "$IN_NIX_SHELL" ]; then
    echo "Entering flake environment..."
    exec nix develop --command bash "$0"
fi

# Create directories
mkdir -p logs checkpoints/dqn

# Launch training for 3 seeds in parallel
echo "================================"
echo "Launching DQN Training (Flake)"
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
