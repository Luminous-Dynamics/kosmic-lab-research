#!/usr/bin/env bash
# Monitor training completion and alert when ppo_200k is done

LOG_FILE="/tmp/overcooked_CORRECTED_training.log"
CHECK_INTERVAL=30  # seconds

echo "=== Training Completion Monitor ==="
echo "Monitoring: $LOG_FILE"
echo "Checking every ${CHECK_INTERVAL}s for ppo_200k completion..."
echo ""

while true; do
    # Get current progress
    CURRENT_LINE=$(tail -5 "$LOG_FILE" | grep "Training:" | tail -1)

    # Check if ppo_200k is saved
    if grep -q "Saved: .*ppo_200k.pth" "$LOG_FILE"; then
        echo ""
        echo "✅ TRAINING COMPLETE! ppo_200k.pth has been saved!"
        echo ""
        echo "Next steps:"
        echo "  1. cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index/experiments/overcooked"
        echo "  2. nix develop"
        echo "  3. python collect_overcooked_simple.py"
        echo "  4. python analyze_overcooked_simple.py"
        echo ""

        # Show final status
        echo "=== Training Summary ==="
        grep "Saved:" "$LOG_FILE" | tail -4
        echo ""

        exit 0
    fi

    # Show current progress
    if [ -n "$CURRENT_LINE" ]; then
        echo -ne "\r$(date '+%H:%M:%S') - $CURRENT_LINE"
    fi

    sleep $CHECK_INTERVAL
done
