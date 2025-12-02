# Historical K(t) Index for Civilizational Coherence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data License: CC-BY-4.0](https://img.shields.io/badge/Data%20License-CC--BY--4.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

## Overview

This repository provides data sources, documentation, and replication materials for:

> **A Historical K(t) Index for Civilizational Coherence (1810–2020): Measuring the Great Filter of Co-Creative Wisdom**
> Tristan Stoltz
> *Global Policy* (2025)

The K(t) Index is a multi-harmonic composite measure aggregating seven dimensions of global civilizational coherence spanning from 1810 to 2020, with an extended synthetic series back to 3000 BCE.

## Key Findings

- **K₂₀₂₀ = 0.914** (95% bootstrap CI: [0.58, 1.00])
- **K₁₈₁₀ ≈ 0.52** (moderate historical baseline)
- **76% increase** in civilizational coherence over 210 years (1810-2020)
- **Coherence gap G₂₀₂₀ = -0.04** (actualization slightly exceeds structural capacity)

The index integrates seven harmonies:
1. **Resonant Coherence** (H₁): Democratic participation, political stability
2. **Pan-Sentient Flourishing** (H₂): Human development, equality, health
3. **Integral Wisdom** (H₃): Education, innovation, knowledge institutions
4. **Infinite Play** (H₄): Cultural diversity, creativity, adaptive capacity
5. **Universal Interconnectedness** (H₅): Trade, communication, mobility
6. **Sacred Reciprocity** (H₆): Cooperative norms, trust, mutual aid
7. **Evolutionary Progression** (H₇): Long-run demographic and technological capacity

## Manuscript

The full manuscript is available in this repository:
- **Main text**: [`manuscript/k_index_manuscript.pdf`](manuscript/k_index_manuscript.pdf)
- **Supplementary materials**: [`manuscript/supplementary/`](manuscript/supplementary/)

## Data Sources

All primary data sources are publicly available from established repositories:

| Source | Coverage | Access | Citation |
|--------|----------|--------|----------|
| **V-Dem v14** | 1810-2020 | [v-dem.net](https://www.v-dem.net/) | Coppedge et al. (2024) |
| **KOF Globalisation Index** | 1970-2020 | [kof.ethz.ch](https://kof.ethz.ch/en/forecasts-and-indicators/indicators/kof-globalisation-index.html) | Gygli et al. (2019) |
| **HYDE 3.2.1** | 3000 BCE-2020 CE | [DOI: 10.5194/essd-9-927-2017](https://doi.org/10.5194/essd-9-927-2017) | Klein Goldewijk et al. (2017) |
| **Maddison Project** | 1-2020 CE | [rug.nl/ggdc/historicaldevelopment/maddison](https://www.rug.nl/ggdc/historicaldevelopment/maddison/) | Bolt & van Zanden (2020) |

See [`data/sources/DATA_SOURCES.md`](data/sources/DATA_SOURCES.md) for complete documentation of all data sources, proxy variable construction, and harmonization procedures.

## Repository Structure

```
historical-k-index/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── data/
│   └── sources/
│       └── DATA_SOURCES.md           # Complete data source documentation
├── manuscript/
│   ├── k_index_manuscript.pdf        # Published manuscript
│   └── supplementary/
│       ├── README.md
│       ├── SUPPLEMENTARY_METHODS.md
│       └── SUPPLEMENTARY_TABLES.md
└── docs/
    ├── METHODOLOGY_DETAILS.md        # Extended methodological discussion
    └── FAQ.md                        # Frequently asked questions
```

## Replication Materials

**Status**: Full replication code and processed data files will be added upon manuscript acceptance.

The complete replication package will include:
- Processed time series CSV files (K(t), individual harmonies, extended series)
- Python scripts for data collection, harmonization, and normalization
- Analysis code for K(t) calculation, bootstrap CI, sensitivity analysis
- Visualization code reproducing all manuscript figures
- Step-by-step replication instructions with estimated run times
- Verification scripts to confirm outputs match manuscript values

## Methodology Overview

### Seven Harmonies Framework

Each harmony H₁-H₇ is constructed from multiple proxy variables drawn from established global datasets:

- **H₁ (Resonant Coherence)**: Combines V-Dem electoral democracy index, participatory component, and political stability indicators
- **H₂ (Pan-Sentient Flourishing)**: Aggregates life expectancy, education, income (HDI components), plus gender equality and health access
- **H₃ (Integral Wisdom)**: Integrates education attainment, innovation metrics, and knowledge institution quality
- **H₄ (Infinite Play)**: Synthesizes cultural diversity indices, adaptive governance, and creative capacity measures
- **H₅ (Universal Interconnectedness)**: Combines KOF globalization components (trade, information flows, mobility)
- **H₆ (Sacred Reciprocity)**: Aggregates cooperative norms, institutional trust, and mutual aid indicators
- **H₇ (Evolutionary Progression)**: Long-run demographic capacity (HYDE population data) with synthetic extension pre-1810

### K(t) Index Calculation

The aggregate K(t) index is computed as the geometric mean of normalized harmonies:

K(t) = [∏ᵢ₌₁⁷ Hᵢ(t)]^(1/7)

Two formulations are provided:
- **Six-harmony formulation**: H₁-H₆ only (conservative, all real data)
- **Seven-harmony formulation**: H₁-H₇ (extended, includes synthetic pre-1810 H₇)

### Validation

Validation includes:
1. **Bootstrap confidence intervals** (2000 resamples): K₂₀₂₀ ∈ [0.58, 1.00]
2. **External validation**: Strong correlations with HDI (r=0.70), KOF (r=0.70), though under-powered (n=4-6)
3. **Sensitivity analysis**: Minimal variation (2.34%) across weighting schemes and normalization methods

## Citation

If you use this index, data, or methods, please cite:

```bibtex
@article{stoltz2025historical,
  title={A Historical K(t) Index for Civilizational Coherence (1810--2020):
         Measuring the Great Filter of Co-Creative Wisdom},
  author={Stoltz, Tristan},
  journal={Global Policy},
  year={2025},
  publisher={Wiley},
  note={Data and code: \url{https://github.com/Luminous-Dynamics/historical-k-index}}
}
```

## Frequently Asked Questions

**Q: What is the "Great Filter" referenced in the title?**
A: The Great Filter hypothesis (Hanson 1998) suggests rare, difficult-to-pass barriers exist between pre-life matter and advanced spacefaring civilizations. This paper proposes that the hardest filter may be developing "co-creative wisdom"—the capacity for collective coordination, foresight, and ethical restraint needed to navigate advanced technologies without self-destruction.

**Q: Why is K₂₀₂₀ so high (0.914) if the world seems troubled?**
A: The K(t) scale is historically-anchored, not aspirationally-anchored. K₂₀₂₀ = 0.914 means humanity in 2020 showed 91.4% of the maximum coherence observed across 1810-2020, not 91.4% of an ideal future state. Relative to 1810 (severe autocracy, minimal health/education, local economies), 2020 represents substantial progress. However, relative to what's needed to safely govern AI, bioengineering, or climate engineering, current coherence may be grossly insufficient—see Section 4.2 "Adolescent God" discussion.

**Q: Can K(t) be used for individual countries or regions?**
A: The current index is global-aggregate only. Extending to country-level K(t) is possible but requires careful adaptation of proxy variables to sub-global scales. See "Future Work" (Section 4.5) for discussion.

**Q: What about missing data before 1810?**
A: For H₁-H₆, reliable quantitative data begins ~1810 with the advent of systematic political and economic record-keeping. Pre-1810 values for these harmonies would require historical inference from qualitative sources or archeological proxies—an important but separate research program. For H₇ (evolutionary progression), we use HYDE 3.2.1 demographic data back to 3000 BCE as a proxy for long-run capacity, allowing the extended time series to capture deep-time context.

**Q: How does this relate to other indices (HDI, SDG, Fragile States)?**
A: K(t) is conceptually distinct:
- **HDI**: Focuses on human development (health, education, income) = subset of H₂
- **SDG Index**: Tracks UN Sustainable Development Goals (17 dimensions, present-focused)
- **Fragile States**: Measures state weakness and conflict risk
- **K(t)**: Multi-harmonic synthesis capturing not just development or stability, but the integration of democratic governance, knowledge institutions, global connectivity, cooperative norms, and long-run evolutionary capacity—dimensions critical for navigating existential risks from advanced technology.

That said, K(t) shows strong correlations with HDI and globalization (r≈0.70), confirming directional alignment while measuring a broader construct.

## License

- **Code**: [MIT License](LICENSE) - Free to use, modify, and distribute
- **Data**: Processed data will be released under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
- **Original Sources**: Retain their original licenses (see DATA_SOURCES.md)

## Contact

**Tristan Stoltz**
Luminous Dynamics
Richardson, TX, USA
Email: tristan.stoltz@luminousdynamics.org

For questions about the methodology, data, or replication: tristan.stoltz@luminousdynamics.org

---

**Last Updated**: November 25, 2025
**Repository Status**: Initial release (manuscript + supplementary materials). Full replication code coming upon manuscript acceptance.
