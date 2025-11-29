#!/bin/bash

# Kill all running training processes

echo "Killing all DQN training processes..."

if [ -f logs/dqn_seed42.pid ]; then
    kill $(cat logs/dqn_seed42.pid) 2>/dev/null && echo "  → Killed seed 42"
fi

if [ -f logs/dqn_seed123.pid ]; then
    kill $(cat logs/dqn_seed123.pid) 2>/dev/null && echo "  → Killed seed 123"
fi

if [ -f logs/dqn_seed456.pid ]; then
    kill $(cat logs/dqn_seed456.pid) 2>/dev/null && echo "  → Killed seed 456"
fi

# Backup: kill by process name
pkill -f "ma_dqn_trainer" 2>/dev/null && echo "  → Killed remaining processes"

echo "Done!"
