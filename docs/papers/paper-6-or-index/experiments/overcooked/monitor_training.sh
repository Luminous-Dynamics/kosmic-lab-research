#!/usr/bin/env bash
# Monitor Overcooked training progress
# Usage: ./monitor_training.sh [log_file]

LOG_FILE="${1:-/tmp/overcooked_training_attempt11.log}"
MODELS_DIR="../../models/overcooked"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Overcooked Training Monitor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if training is still running
TRAINING_PID=$(pgrep -f "train_overcooked.py" | head -1)
if [ -n "$TRAINING_PID" ]; then
    echo "✅ Training ACTIVE (PID: $TRAINING_PID)"
else
    echo "⚠️  Training NOT RUNNING - may have completed or crashed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 Progress Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count completed checkpoints
if [ -d "$MODELS_DIR" ]; then
    TOTAL_CHECKPOINTS=$(find "$MODELS_DIR" -name "*.pth" 2>/dev/null | wc -l)
    echo "✓ Checkpoints saved: $TOTAL_CHECKPOINTS / 24"

    # Count by scenario
    echo ""
    echo "By scenario:"
    for scenario in cramped_room_h400_baseline asymmetric_advantages_h400_baseline \
                    coordination_ring_h400_stress_spatial forced_coordination_h400_stress_sequential \
                    cramped_room_h800_stress_temporal cramped_room_h400_multiagent_sim; do
        if [ -d "$MODELS_DIR/$scenario" ]; then
            count=$(ls "$MODELS_DIR/$scenario"/*.pth 2>/dev/null | wc -l)
            echo "  - $scenario: $count/4"
        fi
    done
else
    echo "⚠️  Models directory not found: $MODELS_DIR"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Recent Log Output (last 30 lines)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$LOG_FILE" ]; then
    tail -30 "$LOG_FILE"
else
    echo "⚠️  Log file not found: $LOG_FILE"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Last updated: $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for errors
if [ -f "$LOG_FILE" ]; then
    ERROR_COUNT=$(grep -i "error\|exception\|traceback" "$LOG_FILE" | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo ""
        echo "⚠️  WARNING: $ERROR_COUNT potential errors found in log"
        echo "    Run: grep -i 'error\|exception\|traceback' $LOG_FILE"
    fi
fi
