#!/usr/bin/env bash

# Setup script for MuJoCo 210 binaries (required for mujoco-py)
#
# Multi-Agent MuJoCo uses mujoco-py which requires the legacy MuJoCo 210 binaries.
# This script downloads and installs them to ~/.mujoco/mujoco210

set -e

MUJOCO_DIR="$HOME/.mujoco"
MUJOCO_210="$MUJOCO_DIR/mujoco210"

echo "🔧 Setting up MuJoCo 210 binaries for mujoco-py..."

# Create .mujoco directory if it doesn't exist
mkdir -p "$MUJOCO_DIR"

# Check if already installed
if [ -d "$MUJOCO_210" ]; then
    echo "✅ MuJoCo 210 already installed at $MUJOCO_210"
    exit 0
fi

# Download MuJoCo 210 binaries
echo "📥 Downloading MuJoCo 210 (Linux)..."
cd "$MUJOCO_DIR"

# Use the GitHub releases (MuJoCo is now open source)
wget -q --show-progress https://github.com/deepmind/mujoco/releases/download/2.1.0/mujoco210-linux-x86_64.tar.gz \
    -O mujoco210.tar.gz

echo "📦 Extracting MuJoCo 210..."
tar -xzf mujoco210.tar.gz
rm mujoco210.tar.gz

echo "✅ MuJoCo 210 installed successfully at $MUJOCO_210"

# Set up environment variable
echo ""
echo "📝 Add this to your shell rc file (~/.bashrc or ~/.zshrc):"
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:$MUJOCO_210/bin"
echo ""
echo "Or run this command now:"
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:$MUJOCO_210/bin"
