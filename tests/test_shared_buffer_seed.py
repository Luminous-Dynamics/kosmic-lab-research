from __future__ import annotations

import numpy as np

from core.shared_buffer import SharedReplayBuffer, Experience


def test_shared_buffer_sampling_deterministic_with_seed() -> None:
    seed = 999
    cap = 32
    bs = 8

    def _make_buf():
        buf = SharedReplayBuffer(capacity=cap, seed=seed)
        for i in range(cap):
            s = np.array([i], dtype=np.float32)
            a = np.array([i * 0.1], dtype=np.float32)
            r = float(i)
            ns = s + 1.0
            d = float(i % 5 == 0)
            e = Experience(state=s, action=a, reward=r, next_state=ns, done=d, universe_id=i % 3)
            buf.push(e)
        return buf

    buf1 = _make_buf()
    buf2 = _make_buf()

    # Sampling sequences should match across buffers given same seed and ops order
    for _ in range(3):
        s1 = buf1.sample(bs)
        s2 = buf2.sample(bs)
        # Compare indices by comparing sampled rewards or states (unique per index)
        assert np.allclose(s1[2], s2[2])  # rewards
        assert np.allclose(s1[0], s2[0])  # states

