# Overcooked O/R Index Validation Pipeline
# =========================================
#
# Usage:
#   make help              - Show this help
#   make test-env          - Test environment setup
#   make overcooked-train  - Train all policies (4-6 hours GPU)
#   make overcooked-collect - Collect trajectories
#   make overcooked-analyze - Generate figures and CSV
#   make overcooked-all    - Run full pipeline
#   make clean             - Remove generated data

.PHONY: help test-env overcooked-train overcooked-collect overcooked-analyze overcooked-all clean

# Default target: show help
help:
	@echo "🍳 Overcooked O/R Index Validation Pipeline"
	@echo "==========================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make test-env           - Test environment setup"
	@echo "  make overcooked-train   - Train all policies (4-6 hours GPU)"
	@echo "  make overcooked-collect - Collect trajectories (30 seeds × 8)"
	@echo "  make overcooked-analyze - Generate figures and CSV"
	@echo "  make overcooked-all     - Run full pipeline"
	@echo "  make clean              - Remove generated data"
	@echo ""
	@echo "Pipeline steps:"
	@echo "  1. Train policies at 4 checkpoints (random, 5k, 50k, 200k)"
	@echo "  2. Collect 30 trajectories per policy × 2 layouts = 240 total"
	@echo "  3. Analyze O/R correlation and generate publication figures"
	@echo ""
	@echo "Expected results:"
	@echo "  - Pearson correlation: r ≈ -0.55 to -0.65"
	@echo "  - Output: overcooked_summary.csv + 2 PNG figures"
	@echo ""
	@echo "Time estimates:"
	@echo "  - Training: 4-6 hours (GPU recommended)"
	@echo "  - Collection: 15-20 minutes"
	@echo "  - Analysis: 2-3 minutes"
	@echo ""

# Test environment setup
test-env:
	@echo "Testing environment setup..."
	@echo ""
	@echo "1. Testing Python imports..."
	@python -c "import numpy, pandas, matplotlib, torch; print('✓ Core packages OK')"
	@python -c "import overcooked_ai_py; print('✓ Overcooked-AI OK')"
	@python -c "import pettingzoo; print('✓ PettingZoo OK')"
	@echo ""
	@echo "2. Testing environment wrapper..."
	@python env_overcooked.py
	@echo ""
	@echo "✓ Environment setup complete!"

# Train all policies (4 checkpoints × 2 layouts = 8 models)
overcooked-train:
	@echo "🏋️  Training Overcooked policies..."
	@echo ""
	@echo "This will train 8 policies:"
	@echo "  - 2 layouts: cramped_room, asymmetric_advantages"
	@echo "  - 4 checkpoints: random, ppo_5k, ppo_50k, ppo_200k"
	@echo ""
	@echo "Estimated time: 4-6 hours (GPU), 12-18 hours (CPU)"
	@echo ""
	@read -p "Continue? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		python train_overcooked.py; \
	else \
		echo "Training cancelled."; \
	fi

# Collect trajectories (30 seeds × 4 policies × 2 layouts = 240 trajectories)
overcooked-collect:
	@echo "📦 Collecting trajectories..."
	@echo ""
	@echo "This will collect 240 trajectories:"
	@echo "  - 30 seeds per policy"
	@echo "  - 4 policy types (random, ppo_5k, ppo_50k, ppo_200k)"
	@echo "  - 2 layouts (cramped_room, asymmetric_advantages)"
	@echo ""
	@echo "Estimated time: 15-20 minutes"
	@echo ""
	@if [ ! -d "../../models/overcooked" ]; then \
		echo "❌ Error: Models not found. Run 'make overcooked-train' first."; \
		exit 1; \
	fi
	@python collect_overcooked.py

# Analyze trajectories and generate figures
overcooked-analyze:
	@echo "📊 Analyzing trajectories..."
	@echo ""
	@if [ ! -d "cramped_room" ] && [ ! -d "asymmetric_advantages" ]; then \
		echo "❌ Error: Trajectories not found. Run 'make overcooked-collect' first."; \
		exit 1; \
	fi
	@python analyze_overcooked.py
	@echo ""
	@echo "✓ Analysis complete!"
	@echo ""
	@echo "Generated files:"
	@echo "  - overcooked_summary.csv"
	@echo "  - ../../figures/overcooked/figure_overcooked_scatter.png"
	@echo "  - ../../figures/overcooked/figure_overcooked_evolution.png"
	@echo ""
	@if [ -f "overcooked_summary.csv" ]; then \
		echo "Quick stats:"; \
		python -c "import pandas as pd; df = pd.read_csv('overcooked_summary.csv'); print(f'  Total trajectories: {len(df)}'); print(f'  Mean O/R: {df[\"or_index\"].mean():.3f}'); print(f'  Mean coordination: {df[\"coordination_success\"].mean():.3f}')"; \
	fi

# Run full pipeline (train → collect → analyze)
overcooked-all: overcooked-train overcooked-collect overcooked-analyze

# Clean generated data
clean:
	@echo "🧹 Cleaning generated data..."
	@read -p "This will delete all models and trajectories. Continue? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf ../../models/overcooked; \
		rm -rf cramped_room asymmetric_advantages; \
		rm -f overcooked_summary.csv; \
		rm -rf ../../figures/overcooked; \
		echo "✓ Clean complete!"; \
	else \
		echo "Clean cancelled."; \
	fi
