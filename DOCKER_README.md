# Docker Reproducibility Guide
**Historical K(t): Complete Reproduction Environment**

This Docker container provides a complete, reproducible environment for computing the K-index of civilizational coherence across 5000 years (3000 BCE - 2020 CE).

---

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build the container
docker-compose build

# Run complete analysis pipeline
docker-compose up compute

# Run specific analyses
docker-compose run compute make extended-compute
docker-compose run validation
docker-compose run robustness

# Serve API (after compute generates artifacts under logs/)
# Optional: customize env via .env (copy .env.example → .env)
cp -n .env.example .env  # one-time
docker-compose up -d api
# API now available (default port 8052)
curl http://localhost:8052/meta | jq

# Check container health status
docker inspect --format='{{json .State.Health}}' historical-k-api | jq

## Security & Rate Limiting (Optional)

Edit `.env` to enable authentication and rate limiting:

```
# Require token for non-public endpoints
KOSMIC_API_TOKEN=secret
# Add docs to public paths (optional)
KOSMIC_API_PUBLIC_PATHS=/health,/ready,/meta,/info,/docs,/redoc
# Per-client rate limit: 60 req/min
KOSMIC_API_RATE_LIMIT=60
KOSMIC_API_RATE_WINDOW=60
```

Then call endpoints with either header:

```
Authorization: Bearer secret
X-API-Key: secret
```
```

### Option 2: Using Docker Directly

```bash
# Build image
docker build -t historical-k:v1.0.0 .

# Run analysis
docker run -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs \
    historical-k:v1.0.0 make extended-compute

# Run specific command
docker run -v $(pwd)/data:/app/data historical-k:v1.0.0 \
    python historical_k/compute_k_extended.py
```

---

## Prerequisites

1. **Docker** installed (version 20.10+)
   - Installation: https://docs.docker.com/get-docker/

2. **Docker Compose** installed (version 2.0+)
   - Included with Docker Desktop
   - Linux: `sudo apt install docker-compose-plugin`

3. **Data Files** (see [Data Requirements](#data-requirements))

---

## Container Contents

The container includes:

- **Python 3.11** with all required dependencies
- **Historical K(t) modules**:
  - Phase 1: Sensitivity, regimes, validation, forecasting
  - Phase 2: Ancient data integration, extended computation
  - Phase 3: Granger causality, Bayesian modeling, counterfactuals
- **Data processing pipelines**:
  - Seshat integration
  - HYDE 3.2 integration
  - External validation (HDI, GDP, Polity, battle deaths)
- **Performance optimization**:
  - Parallelized bootstrap sampling
  - Parallelized sensitivity analysis
  - Vectorized computations
- **Robustness testing**:
  - Weight sensitivity
  - Granularity sensitivity
  - Normalization methods
  - Imputation methods

---

## Data Requirements

### Required Data Files

Place data files in the following structure before running:

```
data/
├── sources/
│   ├── seshat/
│   │   └── raw/
│   │       ├── polities.csv
│   │       ├── social_complexity.csv
│   │       ├── warfare.csv
│   │       └── religion.csv
│   ├── hyde/
│   │   └── raw/
│   │       ├── population/
│   │       ├── cropland/
│   │       ├── grazing/
│   │       └── urban/
│   └── external/
│       └── raw/
│           ├── hdi.csv
│           ├── maddison_gdp.csv
│           ├── polity5.csv
│           ├── vdem.csv
│           └── ucdp_battle_deaths.csv
```

### How to Obtain Data

**1. Seshat Global History Databank**
```bash
# Download from GitHub
curl -o data/sources/seshat/raw/seshat.zip \
    https://github.com/seshat-ga/seshat/archive/master.zip
unzip data/sources/seshat/raw/seshat.zip -d data/sources/seshat/raw/
```

**2. HYDE 3.2**
```bash
# Download from DANS (requires manual download due to size)
# Visit: https://doi.org/10.17026/dans-25g-gez3
# Extract to: data/sources/hyde/raw/
```

**3. External Validation Datasets**
- HDI: http://hdr.undp.org/en/data
- Maddison GDP: https://www.rug.nl/ggdc/historicaldevelopment/maddison/
- Polity V: https://www.systemicpeace.org/inscrdata.html
- V-Dem: https://www.v-dem.net/data/
- UCDP: https://ucdp.uu.se/downloads/

---

## Available Commands

### Complete Pipeline

```bash
# Run entire extended K(t) computation (3000 BCE - 2020 CE)
docker-compose run compute make extended-compute

# Run all Phase 3 analytics
docker-compose run compute make phase3-demo

### Serve API

```bash
# Start API (serves from ./logs mounted into /app/logs)
# Customize env in .env (API_PORT, KOSMIC_API_CACHE_SECONDS, etc.)
docker-compose up -d api

# Inspect readiness and metadata
curl http://localhost:8052/ready
curl http://localhost:8052/meta | jq

# Stop API
docker-compose stop api
```
```

### Individual Analyses

```bash
# Phase 1: Quick wins
docker-compose run compute make historical-regimes
docker-compose run compute make historical-validate
docker-compose run compute make historical-forecast

# Phase 2: Data enhancement
docker-compose run compute make ancient-seshat
docker-compose run compute make ancient-hyde
docker-compose run compute make extended-compute

# Phase 3: Advanced analytics
docker-compose run compute make granger-network
docker-compose run compute make bayesian-model
docker-compose run compute make counterfactuals
docker-compose run compute make formulations
```

### Validation & Robustness

```bash
# Cross-validate with external indices
docker-compose run validation

# Robustness tests
docker-compose run robustness

# Performance benchmarks
docker-compose run compute-optimized
```

---

## Output Files

All results are saved to the `logs/` directory:

```
logs/
├── historical_k/               # Original K(t) (1800-2020)
│   ├── k_series.csv
│   └── harmonies.csv
├── historical_k_extended/      # Extended K(t) (3000 BCE - 2020)
│   ├── k_extended.csv
│   ├── bootstrap_samples.npy
│   └── plots/
├── sensitivity/                # Phase 1 sensitivity analysis
├── regimes/                    # Regime detection
├── validation/                 # Event validation
├── forecasting/                # Time series forecasts
├── granger/                    # Granger causality networks
├── bayesian/                   # Hierarchical Bayesian models
├── counterfactuals/            # "What if" scenarios
├── formulations/               # Alternative K formulations
├── validation_external/        # Cross-validation with HDI, GDP, etc.
└── robustness/                 # Robustness test results
```

---

## Performance

### Expected Runtimes

| Analysis | Serial | Parallel (4 cores) | Parallel (8 cores) |
|----------|--------|-------------------|-------------------|
| Extended K(t) | 3-5 min | 90-120 sec | 60-90 sec |
| Bootstrap (2000) | 120-180 sec | 15-30 sec | 10-20 sec |
| Sensitivity (50 proxies) | 60-120 min | 15-20 min | 10-15 min |
| Phase 3 Complete | 10-15 min | 5-7 min | 3-5 min |

### Setting CPU Cores

In `docker-compose.yml`:
```yaml
environment:
  - COMPUTE_CORES=8  # Adjust based on your system
```

Or via command line:
```bash
docker run -e COMPUTE_CORES=8 historical-k:v1.0.0 make extended-compute
```

---

## Troubleshooting

### Container Won't Build

**Error**: `failed to solve with frontend dockerfile.v0`

**Solution**: Update Docker to version 20.10+
```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

### Out of Memory

**Error**: `Killed` or `MemoryError`

**Solution**: Increase Docker memory limit
- Docker Desktop: Settings → Resources → Memory → 8 GB+
- Linux: No limit by default, check system RAM

### Missing Data Files

**Error**: `FileNotFoundError: data/sources/seshat/raw/polities.csv`

**Solution**: Download required data files (see [Data Requirements](#data-requirements))

### Slow Computation

**Solution**: Use more CPU cores
```yaml
environment:
  - COMPUTE_CORES=8  # Increase from default 4
```

---

## Reproducibility Checklist

Before running analysis:

- [ ] Docker version 20.10+ installed
- [ ] All data files downloaded and placed in correct directories
- [ ] Sufficient disk space (10 GB minimum)
- [ ] Sufficient RAM (8 GB minimum, 16 GB recommended)
- [ ] Configuration files reviewed (`k_config_extended.yaml`)

After running:

- [ ] All log files generated in `logs/`
- [ ] No error messages in console output
- [ ] Results match expected ranges (K ∈ [0, 1])
- [ ] Visualizations generated successfully

---

## Citation

If you use this Docker container for research, please cite:

```
@software{historical_k_2025,
  title = {Historical K(t): 5000-Year Civilizational Coherence Index},
  author = {Luminous Dynamics},
  year = {2025},
  version = {1.0.0},
  doi = {10.5281/zenodo.XXXXXX},
  url = {https://github.com/luminous-dynamics/kosmic-lab}
}
```

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/luminous-dynamics/kosmic-lab/issues
- Email: contact@luminousdynamics.org

---

## License

MIT License - See LICENSE file for details

---

*This Docker environment ensures complete reproducibility of all Historical K(t) analyses across different computing environments.*
