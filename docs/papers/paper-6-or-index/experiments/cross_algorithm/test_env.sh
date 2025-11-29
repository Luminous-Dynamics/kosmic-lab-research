#!/bin/bash
# Quick environment test

cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index/experiments/cross_algorithm

# Find zlib (use correct zlib-1.x, not zlib-ng)
ZLIB_PATH=$(ls -d /nix/store/*-zlib-1.*/lib 2>/dev/null | head -1)
echo "Found zlib at: $ZLIB_PATH"

# Set library path
export LD_LIBRARY_PATH="${ZLIB_PATH}:${LD_LIBRARY_PATH}"

# Activate venv
source venv/bin/activate

# Test imports
echo "Testing NumPy..."
python3 -c 'import numpy; print("✓ NumPy imports successfully!")'

echo "Testing PettingZoo MPE..."
python3 -c 'from pettingzoo.mpe import simple_spread_v3; print("✓ PettingZoo MPE imports successfully!")'

echo "Testing PyTorch..."
python3 -c 'import torch; print(f"✓ PyTorch {torch.__version__} ready!")'

echo ""
echo "✓ All tests passed! Ready to launch training."
