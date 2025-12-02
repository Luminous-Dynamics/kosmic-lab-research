# SMAC Setup Guide (Local + Cloud Options)

## Overview
StarCraft Multi-Agent Challenge (SMAC) can run locally or on cloud. **Start local first** - it's free and sufficient for validation (50 teams, 5 episodes). Cloud is optional for larger experiments.

## Option 1: Local Setup (Recommended First)

### Requirements
- **CPU**: Intel i5 or equivalent
- **GPU**: NVIDIA GTX 1060+ (optional but faster)
- **RAM**: 8-16 GB
- **Storage**: 30GB for StarCraft II

### Installation Steps
```bash
# 1. Install StarCraft II Starter Edition (free)
# Download from Battle.net launcher

# 2. Install PySC2
pip install pysc2

# 3. Install SMAC
pip install git+https://github.com/oxwhirl/smac.git

# 4. Download SMAC maps
python -m smac.bin.map_list

# 5. Test setup
python -c "from smac.env import StarCraft2Env; print('SMAC OK')"
```

### Lightweight Alternative: SMAClite
If StarCraft II installation is problematic:
```bash
pip install smac-lite  # No SC2 dependency
```

### Running Locally
```bash
cd /srv/luminous-dynamics/kosmic-lab
poetry run python experiments/smac_validation.py --map 3m --episodes 50
```

**Pros**: Free, full control, no ongoing costs
**Cons**: May be slow without GPU; large experiments take hours

---

## Option 2: Cloud Setup (For Scale)

### When to Use Cloud
- Local machine lacks GPU
- Need parallel training
- Running 100+ teams or complex maps (8m, 2s3z)

### Free Cloud Options

#### Google Colab
- Free GPU (12-24h sessions)
- Install SMAC in notebook
- Mount Drive for SC2 binaries
- Search "SMAC on Colab" tutorials

#### Kaggle Notebooks
- Free GPU (20-30h/week)
- Similar setup to Colab

#### AWS/GCP Free Tier
- EC2 t2.micro or GCP e2-micro
- CPU-only, limited hours
- Good for small tests

### Paid Cloud (AWS EC2)

## Requirements

### Compute
- **Instance Type**: c5.4xlarge (16 vCPU, 32GB RAM) or better
- **Storage**: 100GB SSD
- **Estimated Cost**: ~$0.68/hour (on-demand), ~$0.27/hour (spot)

### Software
- StarCraft II (Linux version)
- SMAC environment
- PyMARL or similar MARL framework

## AWS Setup

### 1. Launch EC2 Instance

```bash
# Using AWS CLI
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \  # Ubuntu 22.04
    --instance-type c5.4xlarge \
    --key-name your-key \
    --security-group-ids sg-xxx \
    --subnet-id subnet-xxx \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100}}]' \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=smac-validation}]'
```

### 2. Install Dependencies

```bash
# Connect to instance
ssh -i your-key.pem ubuntu@<instance-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-venv git unzip

# Create virtual environment
python3 -m venv ~/smac-env
source ~/smac-env/bin/activate

# Install packages
pip install torch numpy scipy pandas matplotlib seaborn tqdm
```

### 3. Install StarCraft II

```bash
# Download SC2 Linux package
cd ~
wget https://blzdistsc2-a.akamaihd.net/Linux/SC2.4.10.zip
unzip -P iagreetotheeula SC2.4.10.zip -d ~/

# Set environment variable
echo 'export SC2PATH=~/StarCraftII' >> ~/.bashrc
source ~/.bashrc
```

### 4. Install SMAC

```bash
pip install git+https://github.com/oxwhirl/smac.git

# Download SMAC maps
python -m smac.bin.map_list
```

### 5. Clone Repository

```bash
git clone https://github.com/your-repo/kosmic-lab.git
cd kosmic-lab
pip install -e .
```

## Running Experiments

### Test Setup
```bash
python -c "from smac.env import StarCraft2Env; env = StarCraft2Env(map_name='3m'); print('SMAC OK')"
```

### Create SMAC Validation Script

```python
# experiments/smac_validation.py
from smac.env import StarCraft2Env
import numpy as np
from core.or_index import compute_or_index

def run_smac_validation(map_name='3m', n_episodes=50):
    """Run O/R Index validation on SMAC."""
    env = StarCraft2Env(map_name=map_name)

    results = []
    for ep in range(n_episodes):
        obs = env.reset()
        done = False
        observations = []
        actions = []

        while not done:
            # Random actions for baseline
            avail_actions = env.get_avail_actions()
            action = [np.random.choice(np.where(avail)[0])
                      for avail in avail_actions]

            observations.append(obs)
            actions.append(action)

            reward, done, info = env.step(action)
            obs = env.get_obs()

        # Compute O/R Index
        or_index = compute_or_index(
            np.array(observations),
            np.array(actions)
        )

        results.append({
            'episode': ep,
            'or_index': or_index,
            'win': info.get('battle_won', False),
            'reward': reward
        })

    env.close()
    return results
```

### Run Validation
```bash
# Quick test
python experiments/smac_validation.py --map 3m --episodes 10

# Full validation
nohup python experiments/smac_validation.py --map 3m --episodes 100 > smac_results.log 2>&1 &
```

## Cost Estimation

### Scenario: Full SMAC Validation
- **Maps**: 3m, 8m, 2s3z (3 maps)
- **Episodes per map**: 100
- **Time per episode**: ~2 minutes
- **Total time**: ~10 hours

### Cost Breakdown
| Instance | Type | Hours | Cost |
|----------|------|-------|------|
| c5.4xlarge | On-demand | 10 | $6.80 |
| c5.4xlarge | Spot | 10 | $2.70 |

**Recommendation**: Use spot instances with 3x bid for cost savings.

## Results Storage

### Upload to S3
```bash
aws s3 cp results/smac_validation/ s3://your-bucket/smac-validation/ --recursive
```

### Download Results
```bash
aws s3 sync s3://your-bucket/smac-validation/ results/smac_validation/
```

## Cleanup

```bash
# Terminate instance when done
aws ec2 terminate-instances --instance-ids <instance-id>
```

## Alternative: Google Cloud

If AWS is unavailable:
```bash
gcloud compute instances create smac-validation \
    --machine-type=c2-standard-16 \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB
```

## Timeline

1. **Week 1**: Set up instance, install dependencies
2. **Week 2**: Run 3m map validation
3. **Week 3**: Run 8m, 2s3z maps
4. **Week 4**: Analyze results, add to paper

## Contact

For issues with cloud setup, contact the research team or consult AWS/GCP documentation.
