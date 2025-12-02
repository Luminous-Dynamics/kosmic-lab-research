#!/usr/bin/env python3
"""Add .to(self.device) to all tensor creations in MAPPO update() method"""

import re

with open('ma_mappo_trainer.py', 'r') as f:
    content = f.read()

# Fix all torch.FloatTensor creations in update() method that don't already have .to(self.device)
# Lines: 216, 218, 219, 224, 236, 237

replacements = [
    # Line 216: b_obs
    (
        r"b_obs = torch.\.FloatTensor\(data\['observations'\]\)",
        r"b_obs = torch.FloatTensor(data['observations']).to(self.device)"
    ),
    # Line 218: b_logprobs
    (
        r"b_logprobs = torch\.FloatTensor\(data\['logprobs'\]\)",
        r"b_logprobs = torch.FloatTensor(data['logprobs']).to(self.device)"
    ),
    # Line 219: b_values
    (
        r"b_values = torch\.FloatTensor\(data\['values'\]\)",
        r"b_values = torch.FloatTensor(data['values']).to(self.device)"
    ),
    # Line 224: next_value computation
    (
        r"torch\.FloatTensor\(data\['observations'\]\[-1:\]\)\n",
        r"torch.FloatTensor(data['observations'][-1:]).to(self.device)\n"
    ),
    # Line 236: b_advantages
    (
        r"b_advantages = torch\.FloatTensor\(advantages\)",
        r"b_advantages = torch.FloatTensor(advantages).to(self.device)"
    ),
    # Line 237: b_returns
    (
        r"b_returns = torch\.FloatTensor\(returns\)",
        r"b_returns = torch.FloatTensor(returns).to(self.device)"
    ),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

with open('ma_mappo_trainer.py', 'w') as f:
    f.write(content)

print("Fixed all tensor creations in update() method!")
print("Added .to(self.device) to lines: 216, 218, 219, 224, 236, 237")
