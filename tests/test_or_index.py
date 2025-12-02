from __future__ import annotations

import numpy as np

from core.or_index import compute_or_index, compute_or_index_batch, compute_team_or_index


def test_or_index_responsive_vs_random() -> None:
    rng = np.random.default_rng(0)
    t, d = 500, 3
    obs_random = rng.normal(size=(t, d))
    act_random = rng.integers(0, 3, size=t)
    or_random = compute_or_index(obs_random, act_random)

    obs_resp = rng.normal(size=(t, d))
    act_resp = (obs_resp[:, 0] > 0).astype(int)
    or_resp = compute_or_index(obs_resp, act_resp)
    # Flexible behavior (responding to obs) should be more negative
    assert or_resp < or_random


def test_or_index_handles_nans_and_mismatch_lengths() -> None:
    obs = np.array([[0.0, np.nan], [1.0, 2.0], [3.0, 4.0]])
    act = np.array([0, 1, np.nan])
    val = compute_or_index(obs, act)
    assert isinstance(val, float)


def test_or_index_batch_and_team() -> None:
    rng = np.random.default_rng(1)
    obs1 = rng.normal(size=(100, 2))
    act1 = (obs1[:, 0] > 0).astype(int)
    obs2 = rng.normal(size=(100, 2))
    act2 = (obs2[:, 1] > 0).astype(int)
    vals = compute_or_index_batch([(obs1, act1), (obs2, act2)])
    assert len(vals) == 2 and all(isinstance(v, float) for v in vals)
    team = compute_team_or_index([obs1, obs2], [act1, act2], aggregation="mean")
    assert isinstance(team, float)

