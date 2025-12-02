# 📋 Day 1 Action Plan: Cross-Algorithm Setup

**Date**: Start Day 1 of 30
**Goal**: Launch DQN training runs
**Time Estimate**: 6-8 hours
**Status**: Ready to begin

---

## Morning Session (3-4 hours)

### Task 1: Environment Setup (1 hour)
**Goal**: Install dependencies and verify environment

```bash
# 1. Navigate to experiments directory
cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index
mkdir -p experiments/cross_algorithm
cd experiments/cross_algorithm

# 2. Clone CleanRL (recommended implementation)
git clone https://github.com/vwxyzjn/cleanrl.git
cd cleanrl

# 3. Install dependencies
pip install -r requirements/requirements.txt
pip install -r requirements/requirements-pettingzoo.txt

# 4. Test installation
python cleanrl/dqn.py --help
```

**Verification**:
- [ ] CleanRL cloned successfully
- [ ] Dependencies installed without errors
- [ ] Help command shows available arguments

---

### Task 2: MPE Environment Setup (1 hour)
**Goal**: Configure Cooperative Navigation environment

```bash
# 1. Install PettingZoo with MPE
pip install pettingzoo[mpe]

# 2. Test environment
python -c "
from pettingzoo.mpe import simple_spread_v3
env = simple_spread_v3.parallel_env(N=3, local_ratio=0.5, max_cycles=25)
print('Environment loaded successfully!')
print(f'Observation space: {env.observation_space(\"agent_0\")}')
print(f'Action space: {env.action_space(\"agent_0\")}')
"

# 3. Create config file
cat > config_mpe_navigation.yaml << EOF
env_name: "simple_spread_v3"
num_agents: 3
max_cycles: 25
local_ratio: 0.5
num_episodes: 1000
num_seeds: 3
save_freq: 100
EOF
```

**Verification**:
- [ ] PettingZoo installed
- [ ] Environment loads without errors
- [ ] Config file created

---

### Task 3: Adapt DQN for Multi-Agent (1-2 hours)
**Goal**: Modify CleanRL DQN for multi-agent setting

```bash
# Create multi-agent DQN wrapper
cat > ma_dqn.py << 'EOF'
"""Multi-Agent DQN for MPE Cooperative Navigation"""
import numpy as np
import torch
import torch.nn as nn
from cleanrl.dqn import QNetwork
from pettingzoo.mpe import simple_spread_v3

class MultiAgentDQN:
    def __init__(self, env, args):
        self.env = env
        self.agents = env.possible_agents

        # Create separate Q-networks for each agent
        self.q_networks = {}
        self.target_networks = {}
        self.optimizers = {}

        for agent in self.agents:
            obs_space = env.observation_space(agent)
            action_space = env.action_space(agent)

            self.q_networks[agent] = QNetwork(obs_space, action_space).to(args.device)
            self.target_networks[agent] = QNetwork(obs_space, action_space).to(args.device)
            self.target_networks[agent].load_state_dict(self.q_networks[agent].state_dict())

            self.optimizers[agent] = torch.optim.Adam(
                self.q_networks[agent].parameters(),
                lr=args.learning_rate
            )

    def get_actions(self, observations, epsilon):
        """Get actions for all agents"""
        actions = {}
        for agent, obs in observations.items():
            if np.random.random() < epsilon:
                actions[agent] = self.env.action_space(agent).sample()
            else:
                q_values = self.q_networks[agent](torch.Tensor(obs))
                actions[agent] = torch.argmax(q_values).item()
        return actions

    def update(self, batch, agent, args):
        """Update Q-network for one agent"""
        obs, actions, rewards, next_obs, dones = batch

        # Current Q values
        q_values = self.q_networks[agent](obs).gather(1, actions)

        # Target Q values
        with torch.no_grad():
            next_q_values = self.target_networks[agent](next_obs).max(1)[0]
            target_q_values = rewards + args.gamma * next_q_values * (1 - dones)

        # Compute loss
        loss = nn.functional.mse_loss(q_values.squeeze(), target_q_values)

        # Optimize
        self.optimizers[agent].zero_grad()
        loss.backward()
        self.optimizers[agent].step()

        return loss.item()

# Add training loop
def train_ma_dqn(args):
    env = simple_spread_v3.parallel_env(
        N=args.num_agents,
        local_ratio=args.local_ratio,
        max_cycles=args.max_cycles
    )

    ma_dqn = MultiAgentDQN(env, args)

    # Training loop
    for episode in range(args.num_episodes):
        obs = env.reset()
        episode_reward = 0

        while env.agents:
            # Epsilon-greedy exploration
            epsilon = max(0.01, 1.0 - episode / (args.num_episodes * 0.5))
            actions = ma_dqn.get_actions(obs, epsilon)

            # Environment step
            next_obs, rewards, dones, infos = env.step(actions)

            # Store transition and update (simplified - needs replay buffer)
            # TODO: Add replay buffer and batch updates

            obs = next_obs
            episode_reward += sum(rewards.values())

        if episode % args.save_freq == 0:
            print(f"Episode {episode}, Reward: {episode_reward}")
            # TODO: Save checkpoint

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_agents", type=int, default=3)
    parser.add_argument("--local_ratio", type=float, default=0.5)
    parser.add_argument("--max_cycles", type=int, default=25)
    parser.add_argument("--num_episodes", type=int, default=1000)
    parser.add_argument("--learning_rate", type=float, default=1e-4)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--save_freq", type=int, default=100)
    args = parser.parse_args()

    train_ma_dqn(args)
EOF
```

**Verification**:
- [ ] Script runs without syntax errors
- [ ] Can initialize multi-agent DQN
- [ ] Can run 1 episode (even if training logic incomplete)

---

## Afternoon Session (3-4 hours)

### Task 4: Complete Training Script (2 hours)
**Goal**: Add replay buffer and full training loop

**Key additions needed**:
1. Replay buffer (shared or per-agent)
2. Target network updates (every N steps)
3. Trajectory logging (for O/R computation)
4. Checkpoint saving
5. TensorBoard logging

**Approach**:
- Use CleanRL's replay buffer implementation
- Adapt for multi-agent case
- Test with 10-episode run

---

### Task 5: Launch Training (1 hour)
**Goal**: Start first training runs

```bash
# Create launch script
cat > launch_dqn_training.sh << 'EOF'
#!/bin/bash

# Launch 3 seeds in parallel (if GPUs available)
for seed in 42 123 456; do
    python ma_dqn.py \
        --num_agents 3 \
        --num_episodes 1000 \
        --seed $seed \
        --save_freq 100 \
        --exp_name "dqn_mpe_seed${seed}" \
        > logs/dqn_seed${seed}.log 2>&1 &
done

echo "Training started for 3 seeds"
echo "Monitor progress: tail -f logs/dqn_seed42.log"
EOF

chmod +x launch_dqn_training.sh

# Create logs directory
mkdir -p logs

# Launch training
./launch_dqn_training.sh
```

**Verification**:
- [ ] 3 processes running (check with `ps aux | grep ma_dqn`)
- [ ] Log files being created
- [ ] No immediate crashes (check logs)

---

### Task 6: Document Setup (30 min)
**Goal**: Document what was done for reproducibility

```bash
cat > README.md << 'EOF'
# Cross-Algorithm Robustness Experiments

## Setup (Day 1)

### Environments
- MPE Cooperative Navigation (simple_spread_v3)
- 3 agents, 25 timesteps, local_ratio=0.5

### Algorithms
- [x] DQN - Setup complete, training started
- [ ] SAC - TODO (Day 2)
- [ ] MAPPO - TODO (Day 2)
- [ ] QMIX - TODO (Day 3)

### Training Status

#### DQN (Started: YYYY-MM-DD)
- Seeds: 42, 123, 456
- Episodes: 1000
- Status: Running
- Logs: logs/dqn_seed*.log

## Monitoring

Check training progress:
```bash
# View recent rewards
tail -20 logs/dqn_seed42.log

# Check if processes still running
ps aux | grep ma_dqn

# TensorBoard (if enabled)
tensorboard --logdir runs/
```

## Next Steps
- Day 2: Set up SAC and MAPPO
- Day 3: Set up QMIX
- Day 4-7: Monitor training, start theory work
EOF
```

---

## End of Day Checklist

### Must Complete
- [ ] DQN training launched (3 seeds)
- [ ] Training processes verified running
- [ ] Setup documented in README
- [ ] Logs directory created and populating

### Nice to Have
- [ ] TensorBoard logging working
- [ ] First checkpoint saved (after 100 episodes)
- [ ] GPU utilization verified (if using GPUs)

### Issues to Resolve
- List any blockers or problems encountered
- Note what needs debugging tomorrow

---

## Tomorrow (Day 2) Preview

**Goals**:
1. Set up SAC for multi-agent
2. Set up MAPPO for multi-agent
3. Launch SAC and MAPPO training
4. Monitor DQN progress (should be ~20% done)

**Prep tonight**:
- Read SAC paper/implementation notes
- Read MAPPO paper/implementation notes
- Verify DQN training stable overnight

---

## Quick Reference Commands

```bash
# Check training status
ps aux | grep python | grep ma_dqn

# Monitor GPU usage
nvidia-smi -l 1

# View latest rewards
tail -f logs/dqn_seed42.log | grep "Episode"

# Kill training if needed
pkill -f ma_dqn

# Restart training
./launch_dqn_training.sh
```

---

## Troubleshooting

### Issue: CUDA out of memory
**Solution**: Reduce batch size or train on CPU

### Issue: Training very slow
**Solution**: Check GPU utilization, may need to optimize

### Issue: Rewards not improving
**Solution**: Check hyperparameters, may need tuning

### Issue: Process crashes
**Solution**: Check logs for error, likely bug in code

---

## Notes & Observations

(Add notes as you work through the day)

---

*Created*: Day 1
*Status*: Ready to execute
*Estimated time*: 6-8 hours
