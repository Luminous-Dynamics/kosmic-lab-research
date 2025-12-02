from __future__ import annotations

import numpy as np

from fre.phase4_coordinator import BufferConfig, TrainerConfig, Phase4Coordinator
from core.central_critic import CriticConfig


def _transition(state_dim: int, rng: np.random.Generator, uid: int):
    s = rng.normal(size=(state_dim,)).astype(np.float32)
    a = rng.normal(size=(1,)).astype(np.float32)
    r = float(rng.normal())
    ns = s + rng.normal(scale=0.01, size=(state_dim,)).astype(np.float32)
    d = bool(rng.random() < 0.05)
    return s, a, r, ns, d, uid


def test_phase4_warmup_and_training_batches() -> None:
    state_dim = 3
    rng = np.random.default_rng(0)
    buf_cfg = BufferConfig(capacity=64, batch_size=8, seed=123)
    tr_cfg = TrainerConfig(warmup_steps=8, critic_updates_per_step=2, log_interval=0)
    critic_cfg = CriticConfig(state_dim=state_dim, learning_rate=1e-2)
    coord = Phase4Coordinator(buf_cfg, critic_cfg, tr_cfg)

    # Before warmup reached, training should not run
    for i in range(tr_cfg.warmup_steps - 1):
        s, a, r, ns, d, uid = _transition(state_dim, rng, uid=i % 2)
        coord.record_transition(s, a, r, ns, d, uid)
        log_loss, batches = coord.maybe_train()
        assert log_loss is None and batches == {}

    # Push one more to cross warmup threshold (also >= batch size)
    s, a, r, ns, d, uid = _transition(state_dim, rng, uid=1)
    coord.record_transition(s, a, r, ns, d, uid)
    log_loss, batches = coord.maybe_train()
    # Should have performed critic updates and produced actor batches per uid
    assert isinstance(coord.last_loss, float)
    assert isinstance(batches, dict) and len(batches) >= 1
    for uid_k, tup in batches.items():
        states, actions, adv = tup
        assert states.shape[0] == actions.shape[0] == adv.shape[0]


def test_phase4_log_interval_reports_loss() -> None:
    state_dim = 2
    rng = np.random.default_rng(1)
    buf_cfg = BufferConfig(capacity=64, batch_size=8, seed=321)
    tr_cfg = TrainerConfig(warmup_steps=8, critic_updates_per_step=1, log_interval=2)
    critic_cfg = CriticConfig(state_dim=state_dim, learning_rate=1e-2)
    coord = Phase4Coordinator(buf_cfg, critic_cfg, tr_cfg)

    # Fill buffer to warmup
    for i in range(tr_cfg.warmup_steps):
        s, a, r, ns, d, uid = _transition(state_dim, rng, uid=i % 3)
        coord.record_transition(s, a, r, ns, d, uid)

    # First train call (step_count=1): no log yet
    log1, _ = coord.maybe_train()
    assert log1 is None
    # Second train call (step_count=2): should return last_loss
    log2, _ = coord.maybe_train()
    assert isinstance(log2, float)

