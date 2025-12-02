"""Training script for Track C SAC controller using stable-baselines3."""

from __future__ import annotations

import argparse
import json
import random
import subprocess
from pathlib import Path

import numpy as np
import yaml
from stable_baselines3 import SAC
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.utils import set_random_seed

from fre.sac_env import make_env


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _compute_config_hash(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train SAC for Track C rescue")
    parser.add_argument("--config", type=Path, default=Path("configs/track_c_sac.yaml"))
    parser.add_argument("--timesteps", type=int, default=100_000)
    parser.add_argument("--output", type=Path, default=Path("artifacts/sac_track_c"))
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    args = parser.parse_args()

    cfg = load_config(args.config)
    seed = args.seed if args.seed is not None else cfg.get("seed")
    if seed is not None:
        set_random_seed(int(seed))
        random.seed(int(seed))
        np.random.seed(int(seed))

    env = make_env(cfg)
    if seed is not None:
        try:
            env.reset(seed=int(seed))
        except Exception:
            pass

    sac_kwargs = cfg.get("sac", {})
    policy_kwargs = {
        "net_arch": sac_kwargs.get("actor_layers", [256, 256, 128]),
    }

    model = SAC(
        "MlpPolicy",
        env,
        learning_rate=sac_kwargs.get("lr", 3e-4),
        batch_size=sac_kwargs.get("batch_size", 256),
        buffer_size=sac_kwargs.get("replay_size", 1_000_000),
        gamma=sac_kwargs.get("gamma", 0.99),
        tau=sac_kwargs.get("tau", 0.005),
        policy_kwargs=policy_kwargs,
        verbose=1,
    )

    eval_env = make_env(cfg)
    if seed is not None:
        try:
            eval_env.reset(seed=int(seed) + 1)
        except Exception:
            pass
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(args.output),
        log_path=str(args.output),
        eval_freq=5_000,
        deterministic=True,
        render=False,
    )

    model.learn(total_timesteps=args.timesteps, callback=eval_callback)
    args.output.mkdir(parents=True, exist_ok=True)
    model.save(str(args.output / "sac_track_c"))
    # Record provenance
    meta = {
        "seed": seed,
        "config": str(args.config),
        "config_sha256": _compute_config_hash(args.config),
        "git_commit": _git_commit_sha(),
        "timesteps": args.timesteps,
    }
    (args.output / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
