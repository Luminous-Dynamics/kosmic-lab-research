"""
OR-PPO: O/R Index-Guided Proximal Policy Optimization

This implements OR-PPO, an adaptive control algorithm that uses the O/R Index
to dynamically adjust PPO hyperparameters during training. Specifically:

- High O/R → High observation-dependency → More conservative policy updates
- Low O/R → More consistent policy → Allow larger policy updates

This addresses the "PPO paradox" where standard PPO showed weak correlation
with coordination (r=-0.34) compared to REINFORCE (r=-0.71).

Key innovation: O/R as adaptive control signal, not just regularization penalty.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from pathlib import Path
import json
from tqdm import tqdm
from env_overcooked import OvercookedMARLEnv
from sklearn.decomposition import PCA


class ActorCritic(nn.Module):
    """Actor-Critic network for PPO"""

    def __init__(self, obs_dim: int, n_actions: int, hidden_dim: int = 128):
        super().__init__()

        # Shared feature extractor
        self.features = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )

        # Actor head
        self.actor = nn.Linear(hidden_dim, n_actions)

        # Critic head
        self.critic = nn.Linear(hidden_dim, 1)

    def forward(self, obs):
        features = self.features(obs)
        logits = self.actor(features)
        value = self.critic(features)
        return Categorical(logits=logits), value

    def act(self, obs, deterministic=False):
        """Sample action from policy"""
        dist, value = self.forward(obs)
        if deterministic:
            action = torch.argmax(dist.logits)
        else:
            action = dist.sample()
        return action.item(), dist.log_prob(action), value.item()


def compute_or_index_from_trajectory(observations, actions, n_bins=10):
    """
    Compute O/R Index from trajectory data.

    Args:
        observations: (T, obs_dim) or (T,) - observation vectors
        actions: (T, n_agents) - discrete action indices
        n_bins: number of observation bins

    Returns:
        or_index: scalar O/R value
    """
    # Handle scalar observations
    if len(observations.shape) == 1:
        observations = observations.reshape(-1, 1)

    T, obs_dim = observations.shape

    # Handle single agent case
    if len(actions.shape) == 1:
        actions = actions.reshape(-1, 1)

    n_agents = actions.shape[1]

    # Project observations to 1D via PCA if needed
    if obs_dim > 1:
        pca = PCA(n_components=1)
        obs_1d = pca.fit_transform(observations).squeeze()
    else:
        obs_1d = observations.squeeze()

    # Create bins using quantiles
    bin_edges = np.quantile(obs_1d, np.linspace(0, 1, n_bins + 1))
    bin_indices = np.digitize(obs_1d, bin_edges[1:-1], right=True)

    # Convert actions to one-hot vectors for variance computation
    n_actions = int(actions.max()) + 1
    action_onehot = np.zeros((T, n_actions))

    for t in range(T):
        for agent_action in actions[t]:
            action_onehot[t, int(agent_action)] += 1.0 / n_agents

    # Compute total variance (marginal action variance)
    action_mean = action_onehot.mean(axis=0)
    var_total = np.mean(np.sum((action_onehot - action_mean)**2, axis=1))

    # Compute within-bin variances
    bin_vars = []
    for b in range(n_bins):
        mask = (bin_indices == b)
        if np.sum(mask) < 2:
            continue

        actions_bin = action_onehot[mask]
        action_mean_bin = actions_bin.mean(axis=0)
        var_bin = np.mean(np.sum((actions_bin - action_mean_bin)**2, axis=1))
        bin_vars.append(var_bin)

    if len(bin_vars) == 0:
        return 0.0

    var_conditional = np.mean(bin_vars)

    # Handle edge case: constant actions
    if var_total < 1e-9:
        return -1.0

    or_index = var_conditional / var_total - 1.0
    return or_index


class ORGuidedPPO:
    """O/R Index-Guided PPO with adaptive hyperparameters"""

    def __init__(
        self,
        obs_dim: int,
        n_actions: int,
        n_agents: int = 2,
        base_clip: float = 0.2,
        base_lr: float = 3e-4,
        k_clip: float = 0.5,
        k_lr: float = 0.3,
        target_or: float = 0.0,
        sigma: float = 10000,
        use_or_guidance: bool = True,
    ):
        """
        Initialize OR-PPO.

        Args:
            obs_dim: Observation dimensionality
            n_actions: Number of discrete actions
            n_agents: Number of agents (for O/R computation)
            base_clip: Base clip range for PPO
            base_lr: Base learning rate
            k_clip: Clip adaptation strength (0 = no adaptation)
            k_lr: LR adaptation strength (0 = no adaptation)
            target_or: Target O/R Index value (typically 0)
            sigma: Scaling factor for tanh normalization
            use_or_guidance: Whether to use O/R guidance (False = vanilla PPO)
        """
        self.obs_dim = obs_dim
        self.n_actions = n_actions
        self.n_agents = n_agents

        # Hyperparameter adaptation parameters
        self.base_clip = base_clip
        self.base_lr = base_lr
        self.k_clip = k_clip
        self.k_lr = k_lr
        self.target_or = target_or
        self.sigma = sigma
        self.use_or_guidance = use_or_guidance

        # Create policies (one per agent, parameter-shared)
        self.policies = [
            ActorCritic(obs_dim, n_actions) for _ in range(n_agents)
        ]

        # Create optimizers (will be recreated when LR changes)
        self.optimizers = [
            optim.Adam(policy.parameters(), lr=base_lr)
            for policy in self.policies
        ]

        # Current hyperparameters
        self.current_clip = base_clip
        self.current_lr = base_lr

        # Tracking
        self.or_history = []
        self.clip_history = []
        self.lr_history = []

    def compute_adaptive_params(self, current_or):
        """
        Compute adaptive hyperparameters based on O/R feedback.

        Key insight: High O/R (observation-dependent) → More conservative updates
                     Low O/R (consistent) → Allow larger updates

        Returns:
            clip_range: Adaptive clip range
            learning_rate: Adaptive learning rate
        """
        if not self.use_or_guidance:
            return self.base_clip, self.base_lr

        # Normalize delta with tanh
        delta = np.tanh((current_or - self.target_or) / self.sigma)

        # Adaptive clip: high O/R → smaller clip (more conservative)
        clip_range = self.base_clip * (1 - self.k_clip * delta)

        # Adaptive LR: high O/R → smaller LR (more conservative)
        learning_rate = self.base_lr * (1 - self.k_lr * delta)

        # Ensure positive values
        clip_range = max(0.01, clip_range)
        learning_rate = max(1e-5, learning_rate)

        return clip_range, learning_rate

    def update_hyperparameters(self, current_or):
        """Update clip range and learning rate based on O/R"""
        self.current_clip, self.current_lr = self.compute_adaptive_params(current_or)

        # Recreate optimizers with new learning rate
        self.optimizers = [
            optim.Adam(policy.parameters(), lr=self.current_lr)
            for policy in self.policies
        ]

        # Track history
        self.or_history.append(current_or)
        self.clip_history.append(self.current_clip)
        self.lr_history.append(self.current_lr)


def collect_trajectory(env, policies, max_steps=400):
    """Collect a full trajectory from the environment"""
    obs = env.reset()

    trajectory = {
        "observations": [],
        "actions": [],
        "log_probs": [],
        "values": [],
        "rewards": [],
        "raw_rewards": [],  # Track actual task completions
    }

    done = False
    steps = 0

    while not done and steps < max_steps:
        obs_tensor = torch.from_numpy(obs).float()

        # Each agent acts
        actions = []
        log_probs = []
        values = []

        for policy in policies:
            action, log_prob, value = policy.act(obs_tensor)
            actions.append(action)
            log_probs.append(log_prob)
            values.append(value)

        # Step environment with retry logic for illegal actions
        max_retries = 5
        step_success = False

        for retry in range(max_retries + 1):
            try:
                obs_next, reward, done, info = env.step(actions)
                step_success = True
                break
            except ValueError as e:
                if "Illegal action" in str(e):
                    if retry >= max_retries:
                        obs_next = obs
                        reward = -1.0
                        done = False
                        info = {}
                        step_success = True
                        break
                    else:
                        actions = [np.random.randint(0, env.n_actions) for _ in range(len(policies))]
                else:
                    raise

        if not step_success:
            obs_next = obs
            reward = -1.0
            done = False

        # REWARD SHAPING: Very small exploration bonus
        # NOTE: Previous 0.01 was too large - dominated real rewards (400 steps × 0.01 = 4.0)
        # Now using 0.001 so exploration bonus is ~0.4 vs real dish reward of 20
        shaped_reward = reward
        if reward == 0.0:  # No task completion
            shaped_reward = 0.001  # Tiny bonus - won't dominate task rewards

        # Store trajectory data
        trajectory["observations"].append(obs)
        trajectory["actions"].append(actions)
        trajectory["log_probs"].append(torch.stack(log_probs))
        trajectory["values"].append(torch.tensor(values))
        trajectory["rewards"].append(shaped_reward)  # Use shaped reward
        trajectory["raw_rewards"].append(reward)  # Track actual task rewards

        obs = obs_next
        steps += 1

    # Convert to numpy/tensors
    trajectory["observations"] = np.array(trajectory["observations"])
    trajectory["actions"] = np.array(trajectory["actions"])
    trajectory["log_probs"] = torch.stack(trajectory["log_probs"])
    trajectory["values"] = torch.stack(trajectory["values"])
    trajectory["rewards"] = np.array(trajectory["rewards"])
    trajectory["raw_rewards"] = np.array(trajectory["raw_rewards"])

    return trajectory


def compute_gae(rewards, values, gamma=0.99, lam=0.95):
    """Compute Generalized Advantage Estimation"""
    T = len(rewards)
    advantages = np.zeros(T)
    gae = 0

    # Average values across agents to get team-level value
    values_np = values.numpy()
    if len(values_np.shape) > 1:
        values_team = values_np.mean(axis=1)
    else:
        values_team = values_np

    for t in reversed(range(T)):
        if t == T - 1:
            next_value = 0
        else:
            next_value = values_team[t + 1]

        delta = rewards[t] + gamma * next_value - values_team[t]
        gae = delta + gamma * lam * gae
        advantages[t] = gae

    returns = advantages + values_team

    return torch.tensor(advantages, dtype=torch.float32), torch.tensor(returns, dtype=torch.float32)


def ppo_update(policies, optimizers, trajectories, clip_range, n_epochs=4, batch_size=64):
    """Perform PPO update on collected trajectories"""

    # Concatenate all trajectories
    all_obs = torch.from_numpy(np.concatenate([t["observations"] for t in trajectories])).float()
    all_actions = torch.from_numpy(np.concatenate([t["actions"] for t in trajectories])).long()
    all_advantages = torch.cat([t["advantages"] for t in trajectories])
    all_returns = torch.cat([t["returns"] for t in trajectories])
    all_old_log_probs = torch.cat([t["log_probs"] for t in trajectories])

    # Normalize advantages
    all_advantages = (all_advantages - all_advantages.mean()) / (all_advantages.std() + 1e-8)

    n_samples = len(all_obs)

    for epoch in range(n_epochs):
        # Shuffle data
        indices = torch.randperm(n_samples)

        for start in range(0, n_samples, batch_size):
            end = min(start + batch_size, n_samples)
            batch_indices = indices[start:end]

            # Get batch
            obs_batch = all_obs[batch_indices]
            actions_batch = all_actions[batch_indices]
            advantages_batch = all_advantages[batch_indices]
            returns_batch = all_returns[batch_indices]
            old_log_probs_batch = all_old_log_probs[batch_indices]

            # Update each agent's policy independently
            for agent_id, (policy, optimizer) in enumerate(zip(policies, optimizers)):
                optimizer.zero_grad()

                # Get current log probs and values
                dist, values = policy(obs_batch)
                log_probs = dist.log_prob(actions_batch[:, agent_id])
                entropy = dist.entropy().mean()

                # PPO clipped objective
                ratio = torch.exp(log_probs - old_log_probs_batch[:, agent_id].detach())
                surr1 = ratio * advantages_batch.detach()
                surr2 = torch.clamp(ratio, 1 - clip_range, 1 + clip_range) * advantages_batch.detach()
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value loss
                value_loss = ((values.squeeze() - returns_batch.detach()) ** 2).mean()

                # Total loss
                loss = policy_loss + 0.5 * value_loss - 0.01 * entropy

                # Update
                loss.backward()
                torch.nn.utils.clip_grad_norm_(policy.parameters(), 0.5)
                optimizer.step()


def train_or_ppo(
    layout: str,
    algorithm: str,  # "ppo" or "or_ppo"
    n_episodes: int,
    horizon: int = 400,
    save_path: Path = None,
    **or_ppo_kwargs
):
    """Train using PPO or OR-PPO"""

    print(f"\n{'='*60}")
    print(f"Training {algorithm.upper()} on {layout} (horizon={horizon})")
    print(f"{'='*60}")

    # Create environment
    env = OvercookedMARLEnv(layout, horizon=horizon)

    # Create OR-PPO trainer
    use_or_guidance = (algorithm == "or_ppo")
    trainer = ORGuidedPPO(
        obs_dim=env.obs_dim,
        n_actions=env.n_actions,
        n_agents=2,
        use_or_guidance=use_or_guidance,
        **or_ppo_kwargs
    )

    # Training loop
    episode_rewards = []
    raw_episode_rewards = []  # Track actual task completions (not shaped)
    or_indices = []

    update_frequency = 10  # Collect 10 trajectories before update
    trajectories_buffer = []

    for episode in tqdm(range(n_episodes), desc=f"Training {algorithm.upper()}"):
        # Collect trajectory
        trajectory = collect_trajectory(env, trainer.policies, max_steps=horizon)

        # Compute advantages
        advantages, returns = compute_gae(
            trajectory["rewards"],
            trajectory["values"],
            gamma=0.99,
            lam=0.95
        )
        trajectory["advantages"] = advantages
        trajectory["returns"] = returns

        # Store episode reward
        episode_reward = trajectory["rewards"].sum()
        episode_rewards.append(episode_reward)
        raw_reward = trajectory["raw_rewards"].sum()  # Actual task completions
        raw_episode_rewards.append(raw_reward)

        # Compute O/R Index for this trajectory
        or_index = compute_or_index_from_trajectory(
            trajectory["observations"],
            trajectory["actions"],
            n_bins=10
        )
        or_indices.append(or_index)

        # Update hyperparameters based on O/R (if using OR-PPO)
        if use_or_guidance and episode % update_frequency == 0 and episode > 0:
            recent_or = np.mean(or_indices[-update_frequency:])
            trainer.update_hyperparameters(recent_or)

        # Add to buffer
        trajectories_buffer.append(trajectory)

        # Perform update every update_frequency episodes
        if len(trajectories_buffer) >= update_frequency:
            ppo_update(
                trainer.policies,
                trainer.optimizers,
                trajectories_buffer,
                clip_range=trainer.current_clip,
                n_epochs=4,
                batch_size=64
            )
            trajectories_buffer = []

        # Log progress
        if (episode + 1) % 100 == 0:
            mean_reward = np.mean(episode_rewards[-100:])
            mean_raw = np.mean(raw_episode_rewards[-100:])
            mean_or = np.mean(or_indices[-100:])
            print(f"  Episode {episode+1}/{n_episodes}: Shaped={mean_reward:.2f}, Raw={mean_raw:.2f}, O/R={mean_or:.1f}")
            if use_or_guidance:
                print(f"    Adaptive params: clip={trainer.current_clip:.3f}, lr={trainer.current_lr:.6f}")

    # Save results
    if save_path:
        save_path.mkdir(parents=True, exist_ok=True)

        # Save policy weights
        checkpoint = {
            "policy_0": trainer.policies[0].state_dict(),
            "policy_1": trainer.policies[1].state_dict(),
            "algorithm": algorithm,
            "n_episodes": n_episodes,
            "final_mean_reward": float(np.mean(episode_rewards[-100:])),
            "final_or_index": float(np.mean(or_indices[-100:])),
        }
        torch.save(checkpoint, save_path / f"{algorithm}_final.pth")

        # Save training metrics
        metrics = {
            "episode_rewards": [float(r) for r in episode_rewards],
            "raw_episode_rewards": [float(r) for r in raw_episode_rewards],  # Actual task completions
            "or_indices": [float(or_val) for or_val in or_indices],
            "clip_history": [float(c) for c in trainer.clip_history] if use_or_guidance else [],
            "lr_history": [float(lr) for lr in trainer.lr_history] if use_or_guidance else [],
        }
        with open(save_path / f"{algorithm}_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

        print(f"\n✓ Saved {algorithm.upper()} checkpoint and metrics")
        print(f"  Final reward: {checkpoint['final_mean_reward']:.2f}")
        print(f"  Final O/R: {checkpoint['final_or_index']:.1f}")

    return trainer, episode_rewards, or_indices, raw_episode_rewards


def compare_algorithms(layout="cramped_room", horizon=400, n_episodes=2000, n_seeds=3):
    """Compare PPO vs OR-PPO across multiple seeds"""

    print(f"\n{'#'*70}")
    print(f"# Comparing PPO vs OR-PPO on {layout} (horizon={horizon})")
    print(f"# Running {n_seeds} seeds, {n_episodes} episodes each")
    print(f"{'#'*70}\n")

    base_path = Path("models/overcooked/or_ppo_comparison")

    results = {
        "ppo": {"rewards": [], "or_indices": [], "final_rewards": [], "final_or": [], "final_raw": []},
        "or_ppo": {"rewards": [], "or_indices": [], "final_rewards": [], "final_or": [], "final_raw": []},
    }

    for seed in range(n_seeds):
        print(f"\n{'='*60}")
        print(f"SEED {seed+1}/{n_seeds}")
        print(f"{'='*60}")

        # Set random seeds
        np.random.seed(seed)
        torch.manual_seed(seed)

        # Train PPO
        ppo_path = base_path / f"seed_{seed}" / "ppo"
        ppo_trainer, ppo_rewards, ppo_or, ppo_raw = train_or_ppo(
            layout=layout,
            algorithm="ppo",
            n_episodes=n_episodes,
            horizon=horizon,
            save_path=ppo_path,
        )

        results["ppo"]["rewards"].append(ppo_rewards)
        results["ppo"]["or_indices"].append(ppo_or)
        results["ppo"]["final_rewards"].append(np.mean(ppo_rewards[-100:]))
        results["ppo"]["final_or"].append(np.mean(ppo_or[-100:]))
        results["ppo"]["final_raw"].append(np.mean(ppo_raw[-100:]))

        # Reset seeds
        np.random.seed(seed)
        torch.manual_seed(seed)

        # Train OR-PPO
        or_ppo_path = base_path / f"seed_{seed}" / "or_ppo"
        or_ppo_trainer, or_ppo_rewards, or_ppo_or, or_ppo_raw = train_or_ppo(
            layout=layout,
            algorithm="or_ppo",
            n_episodes=n_episodes,
            horizon=horizon,
            save_path=or_ppo_path,
            base_clip=0.2,
            base_lr=3e-4,
            k_clip=0.5,
            k_lr=0.3,
            target_or=0.0,
            sigma=10000,
        )

        results["or_ppo"]["rewards"].append(or_ppo_rewards)
        results["or_ppo"]["or_indices"].append(or_ppo_or)
        results["or_ppo"]["final_rewards"].append(np.mean(or_ppo_rewards[-100:]))
        results["or_ppo"]["final_or"].append(np.mean(or_ppo_or[-100:]))
        results["or_ppo"]["final_raw"].append(np.mean(or_ppo_raw[-100:]))

    # Compute summary statistics
    summary = {
        "ppo": {
            "mean_final_reward": float(np.mean(results["ppo"]["final_rewards"])),
            "std_final_reward": float(np.std(results["ppo"]["final_rewards"])),
            "mean_final_raw": float(np.mean(results["ppo"]["final_raw"])),
            "std_final_raw": float(np.std(results["ppo"]["final_raw"])),
            "mean_final_or": float(np.mean(results["ppo"]["final_or"])),
            "std_final_or": float(np.std(results["ppo"]["final_or"])),
        },
        "or_ppo": {
            "mean_final_reward": float(np.mean(results["or_ppo"]["final_rewards"])),
            "std_final_reward": float(np.std(results["or_ppo"]["final_rewards"])),
            "mean_final_raw": float(np.mean(results["or_ppo"]["final_raw"])),
            "std_final_raw": float(np.std(results["or_ppo"]["final_raw"])),
            "mean_final_or": float(np.mean(results["or_ppo"]["final_or"])),
            "std_final_or": float(np.std(results["or_ppo"]["final_or"])),
        },
    }

    # Save comparison results
    comparison_path = base_path / "comparison_results.json"
    with open(comparison_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"\nPPO:")
    print(f"  Shaped reward: {summary['ppo']['mean_final_reward']:.2f} ± {summary['ppo']['std_final_reward']:.2f}")
    print(f"  Raw reward (task): {summary['ppo']['mean_final_raw']:.2f} ± {summary['ppo']['std_final_raw']:.2f}")
    print(f"  Final O/R: {summary['ppo']['mean_final_or']:.1f} ± {summary['ppo']['std_final_or']:.1f}")
    print(f"\nOR-PPO:")
    print(f"  Shaped reward: {summary['or_ppo']['mean_final_reward']:.2f} ± {summary['or_ppo']['std_final_reward']:.2f}")
    print(f"  Raw reward (task): {summary['or_ppo']['mean_final_raw']:.2f} ± {summary['or_ppo']['std_final_raw']:.2f}")
    print(f"  Final O/R: {summary['or_ppo']['mean_final_or']:.1f} ± {summary['or_ppo']['std_final_or']:.1f}")

    # Compute improvement
    reward_improvement = (
        (summary['or_ppo']['mean_final_reward'] - summary['ppo']['mean_final_reward'])
        / summary['ppo']['mean_final_reward'] * 100
    )
    print(f"\nReward improvement: {reward_improvement:+.1f}%")

    print(f"\nResults saved to: {comparison_path}")

    return summary


if __name__ == "__main__":
    # Run comparison experiment
    compare_algorithms(
        layout="cramped_room",
        horizon=400,
        n_episodes=2000,
        n_seeds=3,
    )
