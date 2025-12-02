#!/usr/bin/env bash
# Launch QMIX GPU training - Fixed version (uses nix shell Python directly)
# Fixes ImportError: libz.so.1 by using nix develop's Python instead of poetry

set -e

if [ -z "$IN_NIX_SHELL" ]; then
    echo "Entering nix develop shell..."
    exec nix develop --command bash "$0" "$@"
fi

SEEDS=(42 123 456)

echo "==================================="
echo "Launching QMIX GPU Training (Fixed)"
echo "Python: $(which python)"
echo "PyTorch: $(python -c 'import torch; print(torch.__version__)')"
echo "CUDA: $(python -c 'import torch; print(torch.cuda.is_available())')"
GPU_NAME=$(python -c 'import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")')
echo "GPU: $GPU_NAME"
echo "==================================="
echo ""

for seed in "${SEEDS[@]}"; do
    echo "Launching QMIX training with seed=$seed (GPU enabled)"
    poetry run python ma_qmix_trainer.py \
        --seed $seed \
        --total-episodes 1000 \
        --cuda \
        > logs/qmix_gpu_seed_${seed}.log 2>&1 &
    PID=$!
    echo "  PID: $PID | Log: logs/qmix_gpu_seed_${seed}.log"
done

echo ""
echo "All QMIX training processes launched!"
echo "Monitor with: watch -n 1 nvidia-smi"
echo "Check logs: tail -f logs/qmix_gpu_seed_42.log"
echo ""
echo "Training will save checkpoints at episodes: 100, 200, ..., 1000"
echo "Checkpoints location: checkpoints/qmix/seed_X/episode_Y/"
