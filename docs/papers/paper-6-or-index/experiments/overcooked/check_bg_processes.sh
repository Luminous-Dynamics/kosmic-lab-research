#!/usr/bin/env bash
# Check status of all background processes and experiments

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Background Process Audit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Overcooked Training (Current)
echo "═══════════════════════════════════════════════════════════════"
echo "1. OVERCOOKED TRAINING (Primary Task)"
echo "═══════════════════════════════════════════════════════════════"

if pgrep -f "train_overcooked.py" > /dev/null; then
    PID=$(pgrep -f "train_overcooked.py" | head -1)
    echo "✅ ACTIVE - PID $PID"
    echo "   Log: /tmp/overcooked_training_attempt12.log"
    CHECKPOINTS=$(find ../../models/overcooked -name "*.pth" 2>/dev/null | wc -l)
    echo "   Progress: $CHECKPOINTS / 24 checkpoints saved"
else
    echo "⚠️  NOT RUNNING"
fi

# 2. Large Scale Validation
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "2. LARGE SCALE VALIDATION"
echo "═══════════════════════════════════════════════════════════════"

if [ -f "large_scale_output.txt" ]; then
    LINES=$(wc -l < large_scale_output.txt)
    echo "📊 Output file exists: $LINES lines"
    if pgrep -f "large_scale_validation.py" > /dev/null; then
        echo "   Status: RUNNING"
    else
        echo "   Status: COMPLETED or CRASHED"
    fi
    echo "   Preview (last 5 lines):"
    tail -5 large_scale_output.txt | sed 's/^/      /'
else
    echo "⚠️  No output file found"
fi

# 3. LaTeX Compilation
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "3. LaTeX COMPILATION"
echo "═══════════════════════════════════════════════════════════════"

LATEX_PROCESSES=$(pgrep -f "pdflatex.*paper_6" | wc -l)
if [ "$LATEX_PROCESSES" -gt 0 ]; then
    echo "📝 $LATEX_PROCESSES LaTeX process(es) running"
else
    echo "✅ No LaTeX processes"
fi

# Check if PDF exists
if [ -f "../../../session-notes/2025-11-18/paper_6_or_index.pdf" ]; then
    PDF_SIZE=$(ls -lh "../../../session-notes/2025-11-18/paper_6_or_index.pdf" | awk '{print $5}')
    PDF_DATE=$(ls -l "../../../session-notes/2025-11-18/paper_6_or_index.pdf" | awk '{print $6, $7, $8}')
    echo "   ✅ PDF exists: $PDF_SIZE (modified: $PDF_DATE)"
else
    echo "   ⚠️  No PDF generated yet"
fi

# 4. MPE Validation Experiments
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "4. MPE VALIDATION EXPERIMENTS"
echo "═══════════════════════════════════════════════════════════════"

MPE_PROCESSES=$(pgrep -f "mpe_validation.py" | wc -l)
if [ "$MPE_PROCESSES" -gt 0 ]; then
    echo "🔬 $MPE_PROCESSES MPE validation process(es) running"
else
    echo "✅ No MPE processes"
fi

# Check MPE logs
for log in /tmp/mpe_validation*.log; do
    if [ -f "$log" ]; then
        SIZE=$(ls -lh "$log" | awk '{print $5}')
        LAST_LINE=$(tail -1 "$log" 2>/dev/null | head -c 80)
        echo "   Log: $(basename $log) ($SIZE)"
        if [ -n "$LAST_LINE" ]; then
            echo "        Last: $LAST_LINE"
        fi
    fi
done

# 5. Process Summary
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "5. PROCESS SUMMARY"
echo "═══════════════════════════════════════════════════════════════"

echo ""
echo "Active Python processes:"
ps aux | grep -E "python.*train_overcooked|python.*large_scale|python.*mpe_validation" | grep -v grep | \
    awk '{printf "  PID %s: %s (CPU: %s%%, MEM: %s%%)\n", $2, $11, $3, $4}'

echo ""
echo "Active LaTeX/compilation processes:"
ps aux | grep -E "pdflatex|bibtex" | grep -v grep | \
    awk '{printf "  PID %s: %s\n", $2, $11}'

# 6. Recommendations
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "6. RECOMMENDATIONS"
echo "═══════════════════════════════════════════════════════════════"

# Check for completed processes that can be cleaned
STALE_COUNT=0

if ! pgrep -f "large_scale_validation.py" > /dev/null && [ -f "large_scale_output.txt" ]; then
    echo "📋 Large scale validation appears complete"
    STALE_COUNT=$((STALE_COUNT + 1))
fi

if [ "$LATEX_PROCESSES" -gt 3 ]; then
    echo "⚠️  Multiple LaTeX processes detected - may be stale"
    STALE_COUNT=$((STALE_COUNT + LATEX_PROCESSES - 1))
fi

if [ "$MPE_PROCESSES" -gt 2 ]; then
    echo "⚠️  Multiple MPE processes detected - may be duplicates"
    STALE_COUNT=$((STALE_COUNT + MPE_PROCESSES - 2))
fi

if [ "$STALE_COUNT" -eq 0 ]; then
    echo "✅ No stale processes detected"
else
    echo "⚠️  Found $STALE_COUNT potentially stale process(es)"
    echo ""
    echo "To clean up stale processes:"
    echo "  pkill -f 'pdflatex.*paper_6'  # Kill LaTeX compilations"
    echo "  pkill -f 'mpe_validation'      # Kill MPE validations"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Audit Complete: $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
