#!/usr/bin/env bash
# Helper script to start QMIX training in current session
# Run this inside a screen session!

set -e

echo "=========================================="
echo "QMIX Training Launcher"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT: This must run in an interactive nix shell!"
echo ""
echo "If you see this message, you're ready to start."
echo ""

# Check if in nix shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "❌ ERROR: Not in nix shell!"
    echo "Please run: nix develop"
    exit 1
fi

# Verify poetry available
if ! command -v poetry &> /dev/null; then
    echo "❌ ERROR: Poetry not found!"
    exit 1
fi

echo "✅ Environment verified"
echo ""

# Create logs directory
mkdir -p logs

echo "Starting sequential QMIX training for 3 seeds..."
echo "Estimated time: 9-15 hours total"
echo ""
echo "Progress will be saved to:"
echo "  - logs/qmix_gpu_seed_42.log"
echo "  - logs/qmix_gpu_seed_123.log"
echo "  - logs/qmix_gpu_seed_456.log"
echo ""
echo "=========================================="
echo ""

# Train each seed sequentially
for seed in 42 123 456; do
    echo ""
    echo "=========================================="
    echo "Training seed $seed (3-5 hours)..."
    echo "Started: $(date)"
    echo "=========================================="
    echo ""

    poetry run python ma_qmix_trainer.py \
        --seed $seed \
        --total-episodes 1000 \
        --cuda \
        2>&1 | tee logs/qmix_gpu_seed_${seed}.log

    EXIT_CODE=${PIPESTATUS[0]}

    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo "✅ Seed $seed complete!"
        echo "Finished: $(date)"
    else
        echo ""
        echo "❌ Seed $seed FAILED with exit code $EXIT_CODE"
        echo "Check logs/qmix_gpu_seed_${seed}.log"
        exit 1
    fi
done

echo ""
echo "=========================================="
echo "🎉 All QMIX training complete!"
echo "=========================================="
echo ""
echo "Checkpoints saved in: checkpoints/qmix/seed_X/episode_Y/"
echo ""
echo "Next steps:"
echo "  1. Compute O/R metrics:"
echo "     python compute_or_available_checkpoints.py --algorithm qmix"
echo ""
echo "  2. Update Section 5.7 with results"
echo ""
echo "  3. Recompile paper"
echo ""
