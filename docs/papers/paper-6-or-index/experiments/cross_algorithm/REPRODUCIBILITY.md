# Reproducibility: Flake vs Venv Approach

**Status**: Both approaches working, flake recommended for future experiments

---

## What We Did (Day 1)

### Hybrid venv + nix approach
```bash
cd /srv/luminous-dynamics/kosmic-lab
nix develop  # Parent flake (provides SDL2, zlib)
cd experiments/cross_algorithm
python -m venv venv
source venv/bin/activate
pip install torch gymnasium pettingzoo pygame
# Manually set LD_LIBRARY_PATH for zlib
```

**Pros**:
- ✅ Got us running quickly
- ✅ Familiar to Python developers
- ✅ Works with packages not in nixpkgs

**Cons**:
- ❌ Not fully reproducible (pip may find different versions)
- ❌ Manual library path fixes needed
- ❌ Violates "ALWAYS USE FLAKES" principle
- ❌ Can't share environment definition easily
- ❌ Dependencies not locked

---

## What We SHOULD Do (Future Experiments)

### Pure flake approach
```bash
cd experiments/cross_algorithm
nix develop  # Local flake.nix
python ma_dqn_trainer.py  # Everything just works
```

**Pros**:
- ✅ **100% reproducible** - Anyone can run `nix develop` and get exact same environment
- ✅ **No manual fixes** - All libraries automatically available
- ✅ **Follows best practices** - Per @.claude/NIXOS_BEST_PRACTICES.md
- ✅ **Locked dependencies** - flake.lock ensures exact versions
- ✅ **Self-documenting** - flake.nix IS the documentation
- ✅ **Shareable** - Copy flake.nix to any NixOS system

**Cons**:
- ⚠️ Some packages (like PettingZoo) not in nixpkgs yet
- ⚠️ Requires understanding Nix language (but we provide template)

---

## Solution: Hybrid Flake (Best of Both Worlds)

Our `flake.nix` provides:
- **Nix-managed**: Python, PyTorch, NumPy, Gymnasium (stable, reproducible)
- **Small venv**: Only for PettingZoo (not in nixpkgs yet)
- **Auto-setup**: `shellHook` creates venv on first entry

### Usage
```bash
cd experiments/cross_algorithm
nix develop  # Everything auto-configured!
python ma_dqn_trainer.py  # Ready to go
```

---

## Comparison Table

| Feature | Venv Approach | Flake Approach | Hybrid Flake |
|---------|---------------|----------------|--------------|
| Reproducibility | ⚠️ Partial | ✅ Full | ✅ Full |
| Setup Time | Fast (5 min) | Slower (10 min first time) | Fast (5 min) |
| Library Paths | Manual | Automatic | Automatic |
| Dep Locking | pip freeze | flake.lock | Both |
| Sharability | Low | High | High |
| NixOS Best Practice | ❌ | ✅ | ✅ |
| Works on non-NixOS | ✅ | ❌ | ❌ |

---

## Why Reproducibility Matters for Paper

For the O/R Index paper cross-algorithm experiments:

1. **Reviewer Verification**: Anyone should be able to run `nix develop` and reproduce results
2. **Long-term Archival**: 5 years from now, exact environment can be restored
3. **Cross-system**: Works identically on any NixOS machine
4. **Dependency Conflicts**: Nix prevents "works on my machine" issues

**Example scenario**: Reviewer wants to verify DQN results
```bash
# With venv approach:
"Can't install PyTorch 2.9.1, getting 2.10.0. Results don't match."

# With flake approach:
git clone repo && cd experiments/cross_algorithm && nix develop
# Exact PyTorch 2.9.1+cpu guaranteed by flake.lock
```

---

## Recommendation for SAC/MAPPO/QMIX (Day 2+)

For tomorrow's implementations, use the flake approach:

```bash
cd experiments/cross_algorithm
nix develop  # Use the flake.nix we created
python ma_sac_trainer.py  # Everything ready
```

**Benefits**:
- Consistent environment across all 4 algorithms
- No library path issues
- Easy for collaborators to reproduce
- Paper reviewers can verify all experiments

---

## Migration Path (If Needed)

If we want to migrate current training:

1. **Don't stop current runs** - They're at episode 900+, let them finish
2. **For future runs**: Use `launch_dqn_training_flake.sh`
3. **For SAC/MAPPO/QMIX**: Start with flake from Day 1

**The venv approach worked and got us results.** But flake approach is better for:
- Paper submission (reproducibility claims)
- Reviewer verification
- Future researchers

---

## Commands Quick Reference

### Current Approach (venv)
```bash
nix develop  # Parent shell
source venv/bin/activate
python ma_dqn_trainer.py
```

### Recommended Approach (flake)
```bash
nix develop  # Local flake
python ma_dqn_trainer.py  # No activation needed
```

### Verify Flake Works
```bash
cd experiments/cross_algorithm
nix develop -c python -c "import torch; import pettingzoo; print('✓ Works!')"
```

---

## Conclusion

**For Day 1**: venv approach was pragmatic and got us results ✅

**For Day 2+**: flake approach follows NixOS best practices and ensures full reproducibility ✅

**For paper submission**: Having flake.nix demonstrates we take reproducibility seriously, which reviewers appreciate.

---

*Both approaches work. Flake is better for science.*
