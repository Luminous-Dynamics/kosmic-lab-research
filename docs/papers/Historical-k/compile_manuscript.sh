#!/usr/bin/env bash
# Full LaTeX compilation sequence for k_index_manuscript.tex

set -e  # Exit on error

cd "$(dirname "$0")"

echo "=== LaTeX Compilation Sequence ==="
echo "Pass 1: Initial compilation..."
pdflatex -interaction=nonstopmode k_index_manuscript.tex > /tmp/latex_pass1.log 2>&1
echo "✓ Pass 1 complete"

echo "BibTeX: Processing citations..."
bibtex k_index_manuscript > /tmp/bibtex.log 2>&1
echo "✓ BibTeX complete"

echo "Pass 2: Incorporating citations..."
pdflatex -interaction=nonstopmode k_index_manuscript.tex > /tmp/latex_pass2.log 2>&1
echo "✓ Pass 2 complete"

echo "Pass 3: Final cross-references..."
pdflatex -interaction=nonstopmode k_index_manuscript.tex > /tmp/latex_pass3.log 2>&1
echo "✓ Pass 3 complete"

echo ""
echo "=== Compilation Summary ==="
ls -lh k_index_manuscript.pdf
pdfinfo k_index_manuscript.pdf 2>/dev/null | grep -E "(Pages|PDF version)" || true

echo ""
echo "=== Warnings/Errors ==="
grep -E "(Warning|Error)" /tmp/latex_pass3.log | head -10 || echo "No major warnings/errors"

echo ""
echo "✅ Compilation complete: k_index_manuscript.pdf"
