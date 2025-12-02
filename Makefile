# Kosmic Lab Makefile - Powerful shortcuts for 10/10 productivity

PYTHON ?= python3
LOGDIR ?= logs/fre_phase1

.PHONY: help init lint test fre-run historical-run docs
.PHONY: dashboard notebook ai-suggest coverage demo clean
.PHONY: holochain-publish holochain-query holochain-verify mycelix-demo
.PHONY: checkpoint-info checkpoint-list checkpoint-copy config-register config-lookup config-diff track-g track-h log-tail log-validate archive-artifacts archive-summary archive-verify
.PHONY: format-code format-fix sac-track-c

help:  # Show all available targets
	@echo "🌊 Kosmic Lab - Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?#' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

format-code:  # Check formatting (Black) and lint (Ruff E,F,I) on code dirs
	poetry run black --check core fre historical_k scripts tests
	poetry run ruff check core fre historical_k scripts tests --select E,F,I

format-fix:  # Auto-format code dirs (Black) and apply Ruff auto-fixes
	poetry run black core fre historical_k scripts tests
	poetry run ruff check core fre historical_k scripts tests --select E,F,I --fix

prune:  # Dry-run prune of generated artifacts (use APPLY=1 to delete)
	poetry run python scripts/prune_artifacts.py $(if $(TARGETS),--targets $(TARGETS),) $(if $(APPLY),--apply,) $(if $(KEEP_DAYS),--keep-days $(KEEP_DAYS),)

init:  # Bootstrap poetry environment and pre-commit hooks
	poetry install --sync
	poetry run pre-commit install
	@echo "✅ Environment ready! Run 'make test' to verify."

lint:  # Run static analysis (black, flake8, mypy)
	poetry run pre-commit run --all-files

test:  # Run unit + integration tests
	poetry run pytest --maxfail=1 --disable-warnings -q

test-verbose:  # Run tests with full output
	poetry run pytest -vv --tb=long

coverage:  # Generate test coverage report (HTML)
	poetry run pytest --cov=core --cov=fre --cov=historical_k --cov-report=html --cov-report=term
	@echo "📊 Coverage report: htmlcov/index.html"

test-property:  # Run property-based tests (hypothesis)
	poetry run pytest tests/test_property_based.py -v

fre-run:  # Execute FRE Phase 1 with default config
	poetry run python fre/run.py --config fre/configs/k_config.yaml

fre-summary:  # Aggregate FRE K-passports
	poetry run python fre/analyze.py --logdir $(LOGDIR) --output $(LOGDIR)/summary.json
	@cat $(LOGDIR)/summary.json | jq

historical-run:  # Compute Historical K(t) from 1800-2020
	poetry run python historical_k/compute_k.py --config historical_k/k_config.yaml

historical-compare:  # Compare normalization strategies
	poetry run python historical_k/comparison.py

historical-contrib:  # Harmony rolling correlation contributions
	poetry run python historical_k/contributions.py

historical-report:  # Generate consolidated markdown report
	poetry run python historical_k/report.py

dashboard:  # Launch real-time interactive dashboard
	poetry run python scripts/kosmic_dashboard.py --logdir $(LOGDIR) --port 8050

notebook:  # Auto-generate analysis Jupyter notebook
	poetry run python scripts/generate_analysis_notebook.py \
		--logdir $(LOGDIR) \
		--output analysis/auto_analysis_$(shell date +%Y%m%d).ipynb
	@echo "📓 Notebook: analysis/auto_analysis_$(shell date +%Y%m%d).ipynb"

ai-suggest:  # Get AI-powered experiment suggestions
	poetry run python scripts/ai_experiment_designer.py \
		--train $(LOGDIR) \
		--model models/designer.pkl \
		--suggest 10 \
		--target-k 1.5 \
		--output configs/ai_suggestions_$(shell date +%Y%m%d).yaml
	@echo "🧠 Suggestions: configs/ai_suggestions_$(shell date +%Y%m%d).yaml"

demo:  # Run quick demo (5 min)
	@echo "🚀 Running Kosmic Lab demo..."
	poetry run python fre/run.py --config fre/configs/k_config.yaml --universes 2 --samples 25
	make notebook LOGDIR=logs
	@echo "✅ Demo complete! Check logs/ and analysis/"

docs:  # Build Sphinx documentation
	cd docs && poetry run make html
	@echo "📚 Docs: docs/_build/html/index.html"

clean:  # Remove generated files
	rm -rf __pycache__ .pytest_cache htmlcov .coverage
	rm -rf logs/*.json analysis/*.ipynb
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "🧹 Cleaned!"

validate:  # Run all checks (tests, lint, coverage)
	@echo "🔍 Running full validation..."
	make lint
	make test
	make coverage
	@echo "✅ All checks passed!"

quick:  # Quick validation (tests only)
	poetry run pytest -x --tb=short -q

test-api:  # Run API-focused tests only
	poetry run pytest -q tests/test_api_*.py

test-te:  # Run transfer entropy tests only
	poetry run pytest -q tests/test_te_bridge_*.py

te-bench:  # Micro-benchmark KSG TE
	poetry run python scripts/bench_te.py

sac-track-c:  # Train Track C SAC controller (CONFIG=configs/track_c_sac.yaml, TIMESTEPS, SEED)
	@CONFIG=$${CONFIG:-configs/track_c_sac.yaml}; \
	TIMESTEPS=$${TIMESTEPS:-100000}; \
	ARGS="--config $$CONFIG --timesteps $$TIMESTEPS"; \
	if [ -n "$(SEED)" ]; then ARGS="$$ARGS --seed $(SEED)"; fi; \
	echo "🎯 Training Track C SAC with $$CONFIG (timesteps=$$TIMESTEPS)"; \
	poetry run python fre/sac_train.py $$ARGS

checkpoint-info:  # Inspect checkpoint metadata (CHECKPOINT=path/to.json)
	@if [ -z "$(CHECKPOINT)" ]; then echo "Set CHECKPOINT=..."; exit 1; fi
	poetry run python scripts/checkpoint_tool.py info --path "$(CHECKPOINT)"

checkpoint-list:  # List checkpoints in directory (DIR=logs/track_g/checkpoints)
	@if [ -z "$(DIR)" ]; then echo "Set DIR=..."; exit 1; fi
	poetry run python scripts/checkpoint_tool.py list --dir "$(DIR)"

checkpoint-copy:  # Copy checkpoint (SRC=... DEST=...)
	@if [ -z "$(SRC)" ] || [ -z "$(DEST)" ]; then echo "Set SRC=... and DEST=..."; exit 1; fi
	poetry run python scripts/checkpoint_tool.py copy --src "$(SRC)" --dest "$(DEST)" $(if $(OVERWRITE),--overwrite,)

config-register:  # Register config hash/label (CONFIG=... LABEL="...")
	@if [ -z "$(CONFIG)" ] || [ -z "$(LABEL)" ]; then echo "Set CONFIG=... and LABEL=..."; exit 1; fi
	poetry run python scripts/config_registry.py register --config "$(CONFIG)" --label "$(LABEL)" $(if $(NOTES),--notes "$(NOTES)",)

config-lookup:  # Lookup config info (HASH=... or CONFIG=...)
	@if [ -z "$(HASH)" ] && [ -z "$(CONFIG)" ]; then echo "Set HASH=... or CONFIG=..."; exit 1; fi
	poetry run python scripts/config_registry.py lookup $(if $(HASH),--hash "$(HASH)",) $(if $(CONFIG),--config "$(CONFIG)",)

config-diff:  # Diff two configs (A=..., B=...)
	@if [ -z "$(A)" ] || [ -z "$(B)" ]; then echo "Set A=... and B=..."; exit 1; fi
	poetry run python scripts/config_registry.py diff --config-a "$(A)" --config-b "$(B)"

log-tail:  # Tail JSONL episode log (PATH=logs/track_g/episodes/*.jsonl, LINES=20, FOLLOW=1)
	@if [ -z "$(PATH)" ]; then echo "Set PATH=..."; exit 1; fi
	poetry run python scripts/log_tool.py tail --path "$(PATH)" --lines $${LINES:-20} $(if $(FOLLOW),--follow,)

log-validate:  # Validate JSONL log structure (PATH=logs/track_g/episodes/*.jsonl)
	@if [ -z "$(PATH)" ]; then echo "Set PATH=..."; exit 1; fi
	poetry run python scripts/log_tool.py validate --path "$(PATH)"

archive-artifacts:  # Snapshot checkpoint + log + config (CHECKPOINT=..., LOG=..., CONFIG=..., OUTPUT optional)
	@if [ -z "$(CHECKPOINT)" ] || [ -z "$(CONFIG)" ]; then echo "Set CHECKPOINT=... CONFIG=... (LOG optional)"; exit 1; fi
	poetry run python scripts/archive_tool.py create --checkpoint "$(CHECKPOINT)" $(if $(LOG),--log "$(LOG)",) --config "$(CONFIG)" $(if $(OUTPUT),--output "$(OUTPUT)",)

archive-verify:  # Verify archive bundle (ARCHIVE=archives/*.tar.gz)
	@if [ -z "$(ARCHIVE)" ]; then echo "Set ARCHIVE=..."; exit 1; fi
	poetry run python scripts/archive_tool.py verify --archive "$(ARCHIVE)"

archive-summary:  # Print archive metadata summary (ARCHIVE=archives/*.tar.gz)
	@if [ -z "$(ARCHIVE)" ]; then echo "Set ARCHIVE=..."; exit 1; fi
	poetry run python scripts/archive_tool.py summary --archive "$(ARCHIVE)"

track-g:  # Run Track G phase (PHASE=g2, CONFIG=fre/configs/track_g_phase_g2.yaml)
	@PHASE=$${PHASE:-g2}; CONFIG=$${CONFIG:-fre/configs/track_g_phase_g2.yaml}; \
	ARGS="--config $$CONFIG --phase $$PHASE"; \
	if [ -n "$(WARM_LOAD)" ]; then ARGS="$$ARGS --warm-start-load '$(WARM_LOAD)'"; fi; \
	if [ -n "$(WARM_SAVE)" ]; then ARGS="$$ARGS --warm-start-save '$(WARM_SAVE)'"; fi; \
	if [ -n "$(SEED)" ]; then ARGS="$$ARGS --seed $(SEED)"; fi; \
	if [ -n "$(ALLOW_MISMATCH)" ]; then ARGS="$$ARGS --warm-start-allow-mismatch"; fi; \
	if [ -n "$(DRY_RUN)" ]; then ARGS="$$ARGS --dry-run"; fi; \
	echo "🌊 Running Track G phase '$$PHASE' with $$CONFIG"; \
	poetry run python fre/track_g_runner.py $$ARGS

track-h:  # Run Track H memory integration (CONFIG=fre/configs/track_h_memory.yaml)
	@CONFIG=$${CONFIG:-fre/configs/track_h_memory.yaml}; \
	ARGS="--config $$CONFIG"; \
	if [ -n "$(WARM_LOAD)" ]; then ARGS="$$ARGS --warm-start-load '$(WARM_LOAD)'"; fi; \
	if [ -n "$(WARM_SAVE)" ]; then ARGS="$$ARGS --warm-start-save '$(WARM_SAVE)'"; fi; \
	if [ -n "$(ALLOW_MISMATCH)" ]; then ARGS="$$ARGS --warm-start-allow-mismatch"; fi; \
	if [ -n "$(SEED)" ]; then ARGS="$$ARGS --seed $(SEED)"; fi; \
	if [ -n "$(DRY_RUN)" ]; then ARGS="$$ARGS --dry-run"; fi; \
	echo "🧠 Running Track H memory integration with $$CONFIG"; \
	poetry run python fre/track_h_runner.py $$ARGS

# ========== Mycelix Integration ==========

holochain-publish:  # Publish K-passports to Mycelix DHT
	@echo "🌊 Publishing K-passports to Holochain DHT..."
	poetry run python scripts/holochain_bridge.py --publish $(LOGDIR)

holochain-query:  # Query corridor passports from DHT
	@echo "🔍 Querying Mycelix corridor..."
	poetry run python scripts/holochain_bridge.py --query --min-k 1.0 --max-k 1.5

holochain-verify:  # Verify passport integrity (usage: make holochain-verify HASH=QmXXX)
	@echo "🔐 Verifying passport..."
	poetry run python scripts/holochain_bridge.py --verify $(HASH)

mycelix-demo:  # Complete Mycelix integration demo
	@echo "🚀 Kosmic-Lab ↔ Mycelix Integration Demo"
	@echo "=========================================="
	@echo ""
	@echo "Step 1: Generate K-passports"
	make fre-run
	@echo ""
	@echo "Step 2: Publish to Holochain DHT"
	make holochain-publish
	@echo ""
	@echo "Step 3: Query corridor"
	make holochain-query
	@echo ""
	@echo "✅ Demo complete! K-passports are now on Mycelix DHT."

# Phase 1: Historical K Improvements (Quick Wins)
.PHONY: historical-sensitivity historical-regimes historical-validate historical-forecast historical-phase1-demo
.PHONY: nox nox-tests nox-lint nox-type nox-format

api-fixtures:  # Generate minimal artifacts for Historical K API
	poetry run python scripts/generate_api_fixtures.py --out logs
	@echo "✅ Wrote sample artifacts under logs/. Now run: poetry run kosmic-api"

api:  # Run Historical K API (honors KOSMIC_* env vars)
	poetry run uvicorn historical_k.api:app --host 0.0.0.0 --port $${PORT:-8052}

api-weak:  # Run API with weak ETag + longer cache
	KOSMIC_API_ETAG=weak KOSMIC_API_CACHE_SECONDS=$${CACHE_SECONDS:-300} \
		poetry run uvicorn historical_k.api:app --host 0.0.0.0 --port $${PORT:-8052}

api-smoke:  # Start API and probe endpoints locally
	poetry run python scripts/generate_api_fixtures.py --out logs
	KOSMIC_LOGS_DIR=logs PORT=$${PORT:-8052} KOSMIC_API_STRICT_READY=1 bash -c '\
	  set -euo pipefail; \
	  poetry run uvicorn historical_k.api:app --host 127.0.0.1 --port $$PORT & \
	  pid=$$!; trap "kill $$pid || true" EXIT; \
	  for i in `seq 1 20`; do code=$$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$$PORT/ready || true); \
	    [ "$$code" = "200" ] && break; sleep 1; done; \
	  curl -fS http://127.0.0.1:$$PORT/health; \
	  curl -fS http://127.0.0.1:$$PORT/meta; \
	  curl -fS http://127.0.0.1:$$PORT/k/series -I; \
	  etag=$$(curl -sI http://127.0.0.1:$$PORT/k/series | awk '/^ETag:/ {print $$2}' | tr -d '\r'); \
	  [ -n "$$etag" ]; \
	  code=$$(curl -s -o /dev/null -w "%{http_code}" -H "If-None-Match: $$etag" http://127.0.0.1:$$PORT/k/series); \
	  [ "$$code" = "304" ]; \
	  echo "✅ API smoke passed"; \
	'

api-protected:  # Run API requiring a token (TOKEN env or 'secret')
	KOSMIC_API_TOKEN=$${TOKEN:-secret} \
	poetry run uvicorn historical_k.api:app --host 0.0.0.0 --port $${PORT:-8052}

historical-sensitivity:  # Run sensitivity analysis (proxy ablation)
	poetry run python -m historical_k.sensitivity --config historical_k/k_config.yaml --plot
	@echo "📊 Sensitivity results: logs/sensitivity/"

historical-regimes:  # Detect coherence regimes (change-points)
	poetry run python -m historical_k.regimes --data logs/historical_k/k_t_series.csv --output logs/regimes
	@echo "📊 Regime analysis: logs/regimes/"

historical-validate:  # Validate events & cross-validation
	poetry run python -m historical_k.validation --data logs/historical_k/k_t_series.csv --event-validation --cross-validation
	@echo "✅ Validation results: logs/validation/"

historical-forecast:  # Forecast K(t) to 2050
	poetry run python -m historical_k.forecasting --data logs/historical_k/k_t_series.csv --method ensemble --horizon 30
	@echo "🔮 Forecast results: logs/forecasting/"

historical-phase1-demo:  # Comprehensive Phase 1 demonstration
	poetry run python scripts/demo_phase1.py

# ========== Nox Convenience Targets ==========

nox:  # List available nox sessions
	poetry run nox -l

nox-tests:  # Run pytest via nox
	poetry run nox -s tests -- $(ARGS)

nox-lint:  # Run pre-commit via nox
	poetry run nox -s lint

nox-type:  # Run mypy via nox
	poetry run nox -s type

nox-format:  # Run format check via nox
	poetry run nox -s format_check

nix-check:  # Run Nix flake checks
	nix flake check --print-build-logs

docker-api:  # Start API service via docker-compose
	docker-compose up -d api
	@echo "🌐 API available at http://localhost:8052"

docker-api-stop:  # Stop API service
	docker-compose stop api

openapi-spec:  # Export OpenAPI schema to logs/openapi.json
	poetry run python scripts/dump_openapi.py --out logs/openapi.json

docker-api-logs:  # Follow API container logs
	docker logs -f historical-k-api

hk-smoke:  # Generate minimal Historical K artifacts under logs/historical_k
	poetry run python scripts/hk_smoke.py

api-hk:  # Generate HK artifacts then run API
	poetry run python scripts/hk_smoke.py
	poetry run uvicorn historical_k.api:app --host 0.0.0.0 --port $${PORT:-8052}

hk-forecast:  # Forecast K(t) using ensemble (requires statsmodels)
	poetry run python -m historical_k.forecasting --data logs/historical_k/k_t_series.csv --method ensemble --horizon $${HORIZON:-30}

hk-regimes:  # Detect coherence regimes
	poetry run python -m historical_k.regimes --data logs/historical_k/k_t_series.csv --output logs/regimes

hk-validate:  # Validate HK outputs under logs/
	poetry run python scripts/validate_hk_outputs.py

hk-mini:  # Generate HK mini dataset from real proxies
	poetry run python scripts/hk_mini_dataset.py

hk-all:  # Generate mini dataset, run regimes + forecast, and validate
	make hk-mini
	make hk-regimes
	make hk-forecast
	make hk-validate
	@echo "🎉 Phase 1 demo complete! Check logs/phase1_demo/"



# Phase 2: Data Enhancement & Extended K(t) (5000 years)
.PHONY: ancient-seshat ancient-hyde ancient-all extended-compute extended-validate extended-plot phase2-demo

ancient-seshat:  # Fetch Seshat Global History Databank
	poetry run python -m historical_k.ancient_data --source seshat --output data/ancient

ancient-hyde:  # Fetch HYDE 3.2 demographic reconstruction
	poetry run python -m historical_k.ancient_data --source hyde --output data/ancient

ancient-all:  # Fetch all ancient data sources
	poetry run python -m historical_k.ancient_data --source both --output data/ancient

extended-compute:  # Compute extended K(t) (3000 BCE - 2020 CE)
	poetry run python historical_k/compute_k_extended.py --config historical_k/k_config_extended.yaml
	@echo "✅ Extended K(t) computed: logs/historical_k_extended/"

extended-validate:  # Validate extended K(t) against all events
	poetry run python -m historical_k.validation \
		--data logs/historical_k_extended/k_t_series_5000y.csv \
		--config historical_k/k_config_extended.yaml \
		--event-validation --cross-validation
	@echo "✅ Extended validation complete"

extended-plot:  # Plot extended K(t) and seventh harmony
	poetry run python -m historical_k.evolutionary_progression \
		--data logs/historical_k_extended/detailed_results.csv \
		--output logs/historical_k_extended/plots
	@echo "📊 Extended plots: logs/historical_k_extended/plots/"

phase2-demo:  # Comprehensive Phase 2 demonstration
	@echo "🚀 Running Phase 2: Data Enhancement Demo"
	@echo "=========================================="
	@echo ""
	@echo "Step 1: Fetch ancient data sources"
	make ancient-all
	@echo ""
	@echo "Step 2: Compute extended K(t) (5000 years)"
	make extended-compute
	@echo ""
	@echo "Step 3: Validate against historical events"
	make extended-validate
	@echo ""
	@echo "Step 4: Generate visualizations"
	make extended-plot
	@echo ""
	@echo "✅ Phase 2 demo complete! Check logs/historical_k_extended/"



# Phase 3: Advanced Analytics
.PHONY: granger-network bayesian-model counterfactuals formulations phase3-demo

granger-network:  # Compute Granger causality network between harmonies
	poetry run python -m historical_k.granger_causality \
		--data logs/historical_k_extended/k_t_series_5000y.csv \
		--output logs/granger \
		--max-lag 5 \
		--layout circular
	@echo "📊 Granger network: logs/granger/"

bayesian-model:  # Fit hierarchical Bayesian model with epoch structure
	poetry run python -m historical_k.bayesian_hierarchical \
		--data logs/historical_k_extended/k_t_series_5000y.csv \
		--output logs/bayesian \
		--samples 2000 \
		--tune 1000
	@echo "📊 Bayesian results: logs/bayesian/"

counterfactuals:  # Run counterfactual "what if" scenarios
	poetry run python -m historical_k.counterfactuals \
		--data logs/historical_k_extended/k_t_series_5000y.csv \
		--output logs/counterfactuals \
		--scenarios all
	@echo "📊 Counterfactuals: logs/counterfactuals/"

formulations:  # Test alternative K-index formulations
	poetry run python -m historical_k.alternative_formulations \
		--data logs/historical_k_extended/k_t_series_5000y.csv \
		--output logs/formulations \
		--formulations all
	@echo "📊 Formulations: logs/formulations/"

phase3-demo:  # Comprehensive Phase 3 demonstration
	@echo "🚀 Running Phase 3: Advanced Analytics Demo"
	@echo "==========================================="
	@echo ""
	@echo "Step 1: Granger causality network"
	make granger-network
	@echo ""
	@echo "Step 2: Bayesian hierarchical model"
	@echo "(Note: This may take several minutes for MCMC sampling)"
	make bayesian-model
	@echo ""
	@echo "Step 3: Counterfactual scenarios"
	make counterfactuals
	@echo ""
	@echo "Step 4: Alternative formulations"
	make formulations
	@echo ""
	@echo "✅ Phase 3 demo complete! Check logs/ directories"


# ============================================================================
# PRE-PUBLICATION IMPROVEMENTS (Phases 1-3 Enhancement)
# ============================================================================

.PHONY: data-fetch-seshat data-fetch-hyde data-fetch-all external-validate robustness-test performance-benchmark docker-build docker-test publication-ready

data-fetch-seshat:  # Fetch real Seshat data
	poetry run python -m historical_k.seshat_integration \
		--download \
		--output data/sources/seshat
	@echo "📥 Seshat data ready in data/sources/seshat/"

data-fetch-hyde:  # Fetch real HYDE 3.2 data
	poetry run python -m historical_k.hyde_integration \
		--check \
		--output data/sources/hyde
	@echo "⚠️  HYDE 3.2 must be downloaded manually - see instructions"

data-fetch-all:  # Check availability of all data sources
	@echo "🔍 Checking data availability..."
	poetry run python -m historical_k.seshat_integration --check
	poetry run python -m historical_k.hyde_integration --check
	@echo ""
	@echo "📋 See DOCKER_README.md for download instructions"

external-validate:  # Cross-validate K(t) with HDI, GDP, Polity, etc.
	@echo "🔬 Cross-validating K(t) with external indices..."
	poetry run python -m historical_k.external_validation --process
	@echo "✅ Validation report: logs/validation_external/validation_report.md"

robustness-test:  # Test robustness to methodological choices
	@echo "🧪 Testing robustness (weights, granularity, normalization, imputation)..."
	poetry run python -m historical_k.robustness_tests --all
	@echo "✅ Robustness report: logs/robustness/robustness_report.md"

performance-benchmark:  # Benchmark serial vs parallel performance
	@echo "⚡ Benchmarking performance optimizations..."
	poetry run python -m historical_k.performance_optimized --benchmark
	@echo "✅ See console output for speedup metrics"

bootstrap-optimized:  # Run optimized bootstrap (2000 samples, parallelized)
	@echo "🔁 Running optimized bootstrap sampling..."
	poetry run python -m historical_k.performance_optimized --bootstrap
	@echo "✅ Bootstrap results: logs/bootstrap_optimized/"

sensitivity-optimized:  # Run optimized sensitivity analysis (parallelized)
	@echo "🔬 Running optimized sensitivity analysis..."
	poetry run python -m historical_k.performance_optimized --sensitivity
	@echo "✅ Sensitivity results: logs/sensitivity_optimized/"

docker-build:  # Build Docker reproducibility container
	@echo "🐳 Building Docker container..."
	docker build -t historical-k:v1.0.0 .
	@echo "✅ Container built: historical-k:v1.0.0"

docker-test:  # Test Docker container
	@echo "🧪 Testing Docker container..."
	docker run historical-k:v1.0.0 make help
	@echo "✅ Docker container working"

docker-compute:  # Run extended computation in Docker
	@echo "🐳 Running extended K(t) computation in Docker..."
	docker-compose run compute make extended-compute
	@echo "✅ Results in logs/historical_k_extended/"

publication-ready:  # Check if ready for publication submission
	@echo "📋 Checking publication readiness..."
	@echo ""
	@echo "=== DATA REQUIREMENTS ==="
	@echo "Checking data availability..."
	@make data-fetch-all 2>&1 | grep -E "(✓|✗)" || true
	@echo ""
	@echo "=== ANALYSIS COMPLETENESS ==="
	@echo "Phase 1 (Quick Wins):"
	@test -f logs/sensitivity/sensitivity_results.csv && echo "  ✓ Sensitivity analysis" || echo "  ✗ Sensitivity analysis (run 'make sensitivity-optimized')"
	@test -f logs/regimes/regimes.csv && echo "  ✓ Regime detection" || echo "  ✗ Regime detection (run 'make historical-regimes')"
	@test -f logs/validation/validation_summary.md && echo "  ✓ Event validation" || echo "  ✗ Event validation (run 'make historical-validate')"
	@test -f logs/forecasting/forecast_2050.csv && echo "  ✓ Forecasting" || echo "  ✗ Forecasting (run 'make historical-forecast')"
	@echo ""
	@echo "Phase 2 (Data Enhancement):"
	@test -f logs/historical_k_extended/k_t_series_5000y.csv && echo "  ✓ Extended K(t) (5000 years)" || echo "  ✗ Extended K(t) (run 'make extended-compute')"
	@echo ""
	@echo "Phase 3 (Advanced Analytics):"
	@test -f logs/granger/causality_report.md && echo "  ✓ Granger causality" || echo "  ✗ Granger causality (run 'make granger-network')"
	@test -f logs/bayesian/bayesian_report.md && echo "  ✓ Bayesian modeling" || echo "  ✗ Bayesian modeling (run 'make bayesian-model')"
	@test -f logs/counterfactuals/counterfactual_report.md && echo "  ✓ Counterfactuals" || echo "  ✗ Counterfactuals (run 'make counterfactuals')"
	@test -f logs/formulations/formulation_report.md && echo "  ✓ Formulations" || echo "  ✗ Formulations (run 'make formulations')"
	@echo ""
	@echo "=== VALIDATION & ROBUSTNESS ==="
	@test -f logs/validation_external/validation_report.md && echo "  ✓ External validation (HDI, GDP, etc.)" || echo "  ✗ External validation (run 'make external-validate')"
	@test -f logs/robustness/robustness_report.md && echo "  ✓ Robustness tests" || echo "  ✗ Robustness tests (run 'make robustness-test')"
	@echo ""
	@echo "=== REPRODUCIBILITY ==="
	@test -f Dockerfile && echo "  ✓ Dockerfile exists" || echo "  ✗ Dockerfile missing"
	@test -f docker-compose.yml && echo "  ✓ docker-compose.yml exists" || echo "  ✗ docker-compose.yml missing"
	@docker images | grep -q "historical-k" && echo "  ✓ Docker image built" || echo "  ✗ Docker image not built (run 'make docker-build')"
	@echo ""
	@echo "=== PUBLICATION READINESS SCORE ==="
	@echo "Run each missing component above to achieve 100%"
	@echo ""
	@echo "📝 See docs/PRE_PUBLICATION_IMPROVEMENT_ROADMAP.md for next steps"

prepub-demo:  # Run complete pre-publication validation pipeline
	@echo "🚀 Running Complete Pre-Publication Validation Pipeline"
	@echo "=========================================================="
	@echo ""
	@echo "This will run:"
	@echo "  1. External validation (HDI, GDP, Polity, battle deaths)"
	@echo "  2. Robustness tests (weights, granularity, normalization)"
	@echo "  3. Performance benchmarks"
	@echo ""
	@echo "Estimated time: 10-15 minutes"
	@echo ""
	@read -p "Press Enter to continue or Ctrl+C to cancel..."
	@echo ""
	@make external-validate
	@echo ""
	@make robustness-test
	@echo ""
	@make performance-benchmark
	@echo ""
	@echo "✅ Pre-publication validation complete!"
	@echo "📊 Check logs/validation_external/ and logs/robustness/"

.PHONY: llm-k-check-env llm-k-smoke llm-k-selfcheck

llm-k-check-env:  # Verify Ollama connectivity and model availability
	@python experiments/llm_k_index/run_experiments.py --check-env

llm-k-smoke:  # Minimal smoke run across phases
	@python experiments/llm_k_index/run_experiments.py --smoke

llm-k-selfcheck:  # Offline self-check (requires numpy)
	@python experiments/llm_k_index/self_check.py

llm-k-install:  # Install minimal dependencies for LLM K-Index utilities
	@python -m pip install -r requirements-llm-k-index.txt
