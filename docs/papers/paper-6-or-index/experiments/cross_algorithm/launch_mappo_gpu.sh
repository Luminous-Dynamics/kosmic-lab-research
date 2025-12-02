#!/usr/bin/env bash
# Launch MAPPO GPU training with Poetry+Nix (3 seeds in parallel)

set -e

# Ensure we're in nix shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "Entering nix develop shell..."
    exec nix develop --command bash "$0" "$@"
fi

# Seeds to train
SEEDS=(42 123 456)

echo "==================================="
echo "Launching MAPPO GPU Training"
echo "PyTorch: $(poetry run python -c 'import torch; print(torch.__version__)')"
echo "CUDA: $(poetry run python -c 'import torch; print(torch.cuda.is_available())')"
echo "GPU: $(poetry run python -c 'import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\")')"
echo "==================================="
echo ""

# Launch training for each seed
for seed in "${SEEDS[@]}"; do
    echo "Launching MAPPO training with seed=$seed (GPU enabled)"
    poetry run python ma_mappo_trainer.py \
        --seed $seed \
        --total_episodes 1000 \
        --cuda \
        > logs/mappo_gpu_seed_${seed}.log 2>&1 &

    PID=$!
    echo "  PID: $PID | Log: logs/mappo_gpu_seed_${seed}.log"
done

echo ""
echo "All MAPPO training processes launched!"
echo "Monitor with: watch -n 1 nvidia-smi"
echo "Check logs: tail -f logs/mappo_gpu_seed_42.log"
