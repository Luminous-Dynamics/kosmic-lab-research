#!/usr/bin/env bash
# Launch QMIX GPU training with LD_LIBRARY_PATH fix for libz.so.1
set -e

if [ -z "$IN_NIX_SHELL" ]; then
    exec nix develop --command bash "$0" "$@"
fi

SEEDS=(42 123 456)

# Find zlib in nix store and set LD_LIBRARY_PATH
ZLIB_PATH=$(nix-store -q --outputs $(nix-instantiate '<nixpkgs>' -A zlib) 2>/dev/null | head -1)
export LD_LIBRARY_PATH="${ZLIB_PATH}/lib:${LD_LIBRARY_PATH}"

echo "===================================
Launching QMIX GPU Training
LD_LIBRARY_PATH: ${LD_LIBRARY_PATH}
PyTorch: $(poetry run python -c 'import torch; print(torch.__version__)')
CUDA: $(poetry run python -c 'import torch; print(torch.cuda.is_available())')
GPU: $(poetry run python -c 'import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")')
===================================
"

for seed in "${SEEDS[@]}"; do
    echo "Launching QMIX training with seed=$seed (GPU enabled)"
    LD_LIBRARY_PATH="${ZLIB_PATH}/lib:${LD_LIBRARY_PATH}" \
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
