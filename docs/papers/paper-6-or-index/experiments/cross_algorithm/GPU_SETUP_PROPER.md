# Proper GPU Setup with Poetry + Nix 🎯

**Date**: November 25, 2025
**Status**: ✅ Doing it the RIGHT way (reproducible)

---

## 🎓 What We Learned

### ❌ Wrong Approach (What I Initially Did)
```bash
# Installing directly into venv with pip
source venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

**Problems**:
- Breaks reproducibility (not in pyproject.toml)
- Won't work on other machines
- Bypasses the whole Poetry + Nix setup we created

### ✅ Right Approach (What We're Doing Now)
```bash
# 1. Update pyproject.toml to specify GPU PyTorch source
[[tool.poetry.source]]
name = "pytorch-gpu"
url = "https://download.pytorch.org/whl/cu121"
priority = "explicit"

[tool.poetry.dependencies]
torch = {version = "^2.5.0", source = "pytorch-gpu"}

# 2. Clean and reinstall
rm -rf .venv poetry.lock
nix develop  # Triggers poetry install automatically

# 3. Verify
poetry run python -c "import torch; print(torch.cuda.is_available())"
```

**Benefits**:
- 100% reproducible (anyone can run it)
- Locked dependencies (poetry.lock)
- Proper Nix+Poetry hybrid approach
- Works on any NixOS system

---

## 📊 Changes Made

### File: pyproject.toml

**Before** (CPU PyTorch):
```toml
[tool.poetry.dependencies]
python = "^3.11"
torch = {url = "https://download.pytorch.org/whl/cpu/torch-2.5.1%2Bcpu-cp311-cp311-linux_x86_64.whl"}
```

**After** (GPU PyTorch):
```toml
[[tool.poetry.source]]
name = "pytorch-gpu"
url = "https://download.pytorch.org/whl/cu121"
priority = "explicit"

[tool.poetry.dependencies]
python = "^3.11"
torch = {version = "^2.5.0", source = "pytorch-gpu"}
```

**Key Differences**:
1. Added PyTorch GPU source (cu121 = CUDA 12.1)
2. Changed from specific wheel URL to version + source
3. Source priority "explicit" means only use pytorch-gpu for torch
4. Flexible version (^2.5.0) allows Poetry to find compatible wheels

---

## 🚀 Installation Process

### Current Status (In Progress) ✅
```
✅ pyproject.toml updated with GPU source
✅ Old .venv and poetry.lock removed
✅ Python version conflicts fixed (>=3.11,<3.13)
✅ pygame constraint removed
✅ nix develop + poetry install launched SUCCESSFULLY
✅ Python 3.11.14 detected and used
✅ Virtual environment created
✅ Dependencies resolved (48 packages)
🚀 Installing packages (1/48: nvidia-nvjitlink-cu12)
⏳ Downloading and installing GPU PyTorch (will be package ~35-40)
📋 Next: Complete install → Verify CUDA availability
```

**Monitor**: `tail -f logs/poetry_gpu_install.log`
**Started**: November 25, 2025, ~18:45 CST

### Expected Timeline
- ✅ Resolve dependencies: 1-2 min (COMPLETE)
- 🚀 Download PyTorch GPU: 5-10 min (780MB) (IN PROGRESS)
- ⏳ Install other packages: 2-3 min
- **Total**: ~10-15 min
- **ETA**: ~19:00 CST

---

## ✅ Post-Install Verification

### 1. Check CUDA Availability
```bash
poetry run python -c "import torch; print('CUDA:', torch.cuda.is_available())"
# Expected: CUDA: True
```

### 2. Check GPU Details
```bash
poetry run python -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"
# Expected: GPU: NVIDIA GeForce RTX 2070
```

### 3. Check PyTorch Version
```bash
poetry run python -c "import torch; print('Version:', torch.__version__)"
# Expected: Version: 2.5.1+cu121
```

---

## 🔧 Launch Scripts Update

### Current Scripts Use venv
```bash
# launch_sac_training.sh
source venv/bin/activate
python ma_sac_trainer.py ...
```

### Should Use Poetry
```bash
# launch_sac_training_poetry.sh (already exists!)
if [ -z "$IN_NIX_SHELL" ]; then
    exec nix develop --command bash "$0"
fi

poetry run python ma_sac_trainer.py ...
```

**We already have poetry launch scripts!** Just need to use them:
- `launch_sac_training_poetry.sh`
- Can create `launch_mappo_training_poetry.sh`

---

## 🎯 Enabling GPU in Trainers

### Current Issue
Trainers have `cuda: bool = False` in Args, but even if we set it to True, the code doesn't actually move tensors to GPU!

### Need to Add Device Placement

**Add to each trainer's `__init__` or `train()` function**:
```python
# Set device
self.device = torch.device("cuda" if args.cuda and torch.cuda.is_available() else "cpu")
print(f"Using device: {self.device}")

# Move networks to device
for agent in self.agents:
    self.agent_networks[agent].to(self.device)
    if hasattr(self, 'target_networks'):
        self.target_networks[agent].to(self.device)

# In forward pass, move data to device
obs_tensor = torch.FloatTensor(obs).to(self.device)
```

**Files to modify**:
1. `ma_sac_trainer.py` (398 lines)
2. `ma_mappo_trainer.py` (420 lines)
3. `ma_dqn_trainer.py` (322 lines) - for future GPU runs

---

## 📊 Expected Performance

### CPU (Measured)
- SAC: ~1.5 minutes/episode
- Total time: 50+ hours for all training

### GPU (Expected)
**Conservative (10x)**:
- SAC: 9 seconds/episode
- Total time: ~5 hours

**Realistic (20-30x)**:
- SAC: 3-5 seconds/episode
- Total time: **2-3 hours** ← Most likely

**Optimistic (50x)**:
- SAC: 1-2 seconds/episode
- Total time: ~1 hour

---

## 🏆 Why This Matters

### For the Paper
1. **Enables completion today** instead of in 2-3 days
2. **Demonstrates proper research engineering**
3. **Scalable to larger experiments**
4. **Professional presentation**

### For Reproducibility
1. **Anyone can reproduce** with same setup
2. **Locked dependencies** (flake.lock + poetry.lock)
3. **Clear documentation** of environment
4. **No manual steps** needed

### For Future Work
1. **Template for other experiments**
2. **Easy to scale up** (more agents, larger networks)
3. **GPU-first approach** becomes standard
4. **Can handle complex environments**

---

## 📋 Next Steps (After Install Completes)

1. **Verify CUDA** (python -c commands above)
2. **Add device placement** to SAC and MAPPO trainers
3. **Test quick run** (2 episodes) to verify GPU works
4. **Launch full training** (1000 episodes each, 3 seeds)
5. **Monitor GPU usage** (`watch -n 1 nvidia-smi`)
6. **Wait 2-3 hours** for training to complete
7. **Analyze results** and compute O/R Index

---

## 💡 Key Lessons

### What Went Right ✅
1. **User caught the issue** - "Shouldn't we be using flake and poetry?"
2. **Fixed before launching** - Would have been harder to fix mid-training
3. **Learned proper Poetry source management**
4. **Documented the process** for future reference

### What to Remember 🧠
1. **Always use proper package manager** (Poetry, not pip)
2. **Reproducibility is non-negotiable** for research
3. **Check GPU usage** before starting long training
4. **Test with small run** before full training
5. **Document everything** as you go

---

## 🎓 Why Poetry + Nix is Worth It

This took an extra 15-20 minutes to set up properly, but it ensures:
- ✅ Anyone can reproduce our experiments
- ✅ Paper reviewers can verify results
- ✅ Future us (in 5 years) can re-run everything
- ✅ Other researchers can build on our work

**Professional research = Reproducible research**

---

**Status**: 🚀 Installing GPU PyTorch the RIGHT way
**ETA**: 10-15 minutes
**Next**: Verify CUDA and launch training

*This is how you do it properly!* 🏆
