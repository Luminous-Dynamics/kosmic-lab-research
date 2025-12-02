#!/usr/bin/env bash
# Launch QMIX GPU training using screen for parallel execution
# This ensures proper environment inheritance and allows monitoring

set -e

if [ -z "$IN_NIX_SHELL" ]; then
    echo "Entering nix develop shell..."
    exec nix develop --command bash "$0" "$@"
fi

SEEDS=(42 123 456)

echo "==================================="
echo "Launching QMIX GPU Training (Screen)"
echo "PyTorch: $(poetry run python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'checking...')"
echo "CUDA: $(poetry run python -c 'import torch; print(torch.cuda.is_available())' 2>/dev/null || echo 'checking...')"
echo "==================================="
echo ""

# Check if screen is available
if ! command -v screen &> /dev/null; then
    echo "ERROR: screen is not installed. Installing via nix..."
    echo "Please run: nix-shell -p screen"
    exit 1
fi

# Create logs directory
mkdir -p logs

echo "Launching 3 parallel QMIX training sessions..."
echo ""

for seed in "${SEEDS[@]}"; do
    SESSION_NAME="qmix_seed_${seed}"

    # Kill existing session if it exists
    screen -S "$SESSION_NAME" -X quit 2>/dev/null || true

    # Launch new screen session
    screen -dmS "$SESSION_NAME" bash -c "
        cd $(pwd)
        poetry run python ma_qmix_trainer.py \\
            --seed $seed \\
            --total-episodes 1000 \\
            --cuda \\
            2>&1 | tee logs/qmix_gpu_seed_${seed}.log
        echo 'Training complete for seed $seed' >> logs/qmix_gpu_seed_${seed}.log
        echo 'Press ENTER to close this screen session...'
        read
    "

    echo "✓ Launched seed=$seed in screen session '$SESSION_NAME'"
    echo "  Monitor: screen -r $SESSION_NAME"
    echo "  Log: tail -f logs/qmix_gpu_seed_${seed}.log"
    echo ""

    # Small delay to avoid race conditions
    sleep 1
done

echo "==================================="
echo "All QMIX training sessions launched!"
echo "==================================="
echo ""
echo "Commands:"
echo "  List sessions:  screen -ls"
echo "  Attach to seed 42:  screen -r qmix_seed_42"
echo "  Detach from session:  Ctrl+A, then D"
echo "  Check all logs:  tail -f logs/qmix_gpu_seed_*.log"
echo "  Monitor GPU:  watch -n 1 nvidia-smi"
echo ""
echo "Training will save checkpoints at episodes: 100, 200, ..., 1000"
echo "Checkpoints location: checkpoints/qmix/seed_X/episode_Y/"
echo ""
echo "Expected completion: 3-5 hours per seed (parallel execution)"
