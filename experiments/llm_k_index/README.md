# LLM K-Index Experiments

Quick notes for running and tweaking the LLM K-Index suite.

## Quickstart
- Ensure Ollama is running locally with the approved models pulled (see `DEFAULT_EXPERIMENT_MODELS` in `ollama_client.py`).
- Default run (all phases): `python experiments/llm_k_index/run_experiments.py`
- Quick mode (fewer samples, capped social pairs): `python experiments/llm_k_index/run_experiments.py --quick`
- Smoke mode (minimal samples, single social pair): `python experiments/llm_k_index/run_experiments.py --smoke`
- Single phase: `python experiments/llm_k_index/run_experiments.py --phase 3`
- Environment check (no runs): `python experiments/llm_k_index/run_experiments.py --check-env`
- Choose models: `python experiments/llm_k_index/run_experiments.py --models "gemma3:1b,mistral:7b"`
- Custom output dir: `python experiments/llm_k_index/run_experiments.py --output-dir /tmp/llm_k_runs`
- Run only stubbed tests (requires pytest): `python -m pytest tests/test_llm_k_index_experiments.py -q`
- Offline self-check (no Ollama calls; requires numpy): `python experiments/llm_k_index/self_check.py`
- Makefile shortcuts:
  - `make llm-k-check-env`
  - `make llm-k-smoke`
  - `make llm-k-selfcheck`
  - `make llm-k-install` (install minimal deps via `requirements-llm-k-index.txt`)

## Minimal setup
- Install core deps (numpy + requests) if missing: `python -m pip install -r requirements.txt` or `-r requirements-dev.txt` for pytest.
- Ensure Ollama is running locally with `embeddinggemma:300m` plus your target generation models pulled.
- If `pytest` is not installed, use the offline self-check instead.

## Quick recipes
- Verify setup only: `make llm-k-check-env`
- Offline sanity (no Ollama): `make llm-k-selfcheck`
- Fast end-to-end smoke: `make llm-k-smoke`
- Full (default models, all phases): `python experiments/llm_k_index/run_experiments.py`
- Custom models: `python experiments/llm_k_index/run_experiments.py --models "gemma3:1b,mistral:7b"`

## Phase controls
- Phase 4 (Prediction): override sample count with `--prediction-samples N`.
- Phase 6 (Social): override sample count with `--social-samples N` and limit evaluated pairs with `--social-max-pairs K` (defaults to min(6, total pairs) and 2 in quick mode).
- Base sample count for other phases: `--samples N` (defaults to 20 in `--quick`, 50 otherwise).
- Reproducibility: set `--seed` to seed numpy and Python random.
- Phase timing: each phase prints and logs its duration; see `logs/llm_k_index/*.json`.
- Summary exports: results log JSON plus timestamped CSV summaries at `experiments/llm_k_index/results/summary_*.csv` (or under your `--output-dir`).

## Common issues
- `ModuleNotFoundError: numpy/pytest`: run `make llm-k-install` (or install `-r requirements-llm-k-index.txt`).
- Ollama connection/embedding model missing: run `make llm-k-check-env` and pull any missing models shown.
- Network/service errors during runs: re-run with `--quick` or `--smoke` after environment passes check.

## Outputs
- Logs: `logs/llm_k_index/`
- Results JSON (per run): printed path after completion.

## Tips
- If embedding or model APIs are unavailable, runs will skip errored prompts; ensure `embeddinggemma:300m` and your target generation models are pulled.
- For lightweight smoke tests, combine `--quick --social-max-pairs 1 --prediction-samples 8 --social-samples 6`.
