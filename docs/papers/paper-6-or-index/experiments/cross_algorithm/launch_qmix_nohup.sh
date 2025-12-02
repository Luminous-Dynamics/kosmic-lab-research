#!/usr/bin/env bash
# Launch QMIX GPU training using nohup with preserved environment
set -e

if [ -z "$IN_NIX_SHELL" ]; then
    exec nix develop --command bash "$0" "$@"
fi

SEEDS=(42 123 456)

echo "==================================="
echo "Launching QMIX GPU Training (Nohup + Direct Execution)"
echo "Strategy: Run training directly in foreground shells"
echo "==================================="
echo ""

# Capture current environment
ENV_VARS=$(env | grep -E "^(PATH|LD_LIBRARY_PATH|PYTHONPATH|NIX_|IN_NIX)" | sed 's/^/export /')

mkdir -p logs

echo "Launching 3 training runs sequentially..."
echo "This will take 9-15 hours total but guarantees success."
echo ""

for seed in "${SEEDS[@]}"; do
    LOG_FILE="logs/qmix_gpu_seed_${seed}.log"

    echo "[$seed] Starting training (this will take 3-5 hours)..."
    echo "[$seed] Log: $LOG_FILE"

    # Run in foreground with output to log
    poetry run python ma_qmix_trainer.py \
        --seed $seed \
        --total-episodes 1000 \
        --cuda \
        2>&1 | tee "$LOG_FILE"

    EXIT_CODE=${PIPESTATUS[0]}

    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$seed] ✓ Training completed successfully"
    else
        echo "[$seed] ✗ Training failed with exit code $EXIT_CODE"
        echo "[$seed] Check log: $LOG_FILE"
        exit 1
    fi

    echo ""
done

echo "==================================="
echo "All QMIX training runs complete!"
echo "==================================="
echo ""
echo "Checkpoints saved in: checkpoints/qmix/seed_X/episode_Y/"
echo ""
echo "Next steps:"
echo "  1. Compute O/R metrics: python compute_or_available_checkpoints.py --algorithm qmix"
echo "  2. Update Section 5.7 with QMIX results"
echo "  3. Recompile paper"
