#!/usr/bin/env bash
# Launch QMIX GPU training - Simplified version
set -e

if [ -z "$IN_NIX_SHELL" ]; then
    exec nix develop --command bash "$0" "$@"
fi

SEEDS=(42 123 456)

echo "===================================
Launching QMIX GPU Training
PyTorch: $(poetry run python -c 'import torch; print(torch.__version__)')
CUDA: $(poetry run python -c 'import torch; print(torch.cuda.is_available())')
GPU: $(poetry run python -c 'import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")')
===================================
"

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
