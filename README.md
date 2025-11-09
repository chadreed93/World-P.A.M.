# 🚐️ World P.A.M. — Predictive Analytic Machine

**World P.A.M.** (Predictive Analytic Machine) is a Python-based global risk assessment tool that ingests live international news feeds (Reuters, BBC, AP, UN, NATO, IAEA, Al Jazeera, DW) and estimates probabilities for world events: interstate war, civil unrest, coups, government collapse, nuclear escalation, economic crises, famine, pandemics, and natural disasters.

> *“Analyzing. Probability of hypothesis ‘global_war_risk’: 6.7%. Processing. Monte Carlo mean 12.2%, 5–95% range 1.2–36.7%.”*

---

## Badges

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## Table of Contents

* [Features](#features)
* [Quickstart](#quickstart)
* [Usage](#usage)
* [Readable Output](#readable-output)
* [Configuration](#configuration)
* [Included Scenarios](#included-scenarios)
* [Examples](#examples)
* [Run All Scenarios](#run-all-scenarios)
* [Tips & Troubleshooting](#tips--troubleshooting)
* [Roadmap](#roadmap)
* [License](#license)
* [Background](#background)
* [Contributing](#contributing)

---

## Features

* 📰 **Live data** from multiple global RSS/Atom feeds.
* 🧠 **Bayesian-style** logistic model with optional **Monte Carlo** simulation.
* 👤 **Readable explanations** (“low but notable likelihood,” “significant and rising probability”).
* 🌍 **16+ scenarios** across conflict, state stability, WMD, and societal risks.
* 🧹 Fully configurable via `world_config.json` (sources, signals, hypotheses, keyword sets).
* 🔁 `--run-all` to evaluate every scenario in one pass.
* 🆘 `--help-info` for quick usage help.
* 📦 **Zero external dependencies** (standard library only).

---

## Quickstart

```bash
git clone https://github.com/yourusername/world-pam.git
cd world-pam
# optional: rebuild a default config if missing
python pam_world.py --init
# list scenarios
python pam_world.py --list
```

**Requirements:** Python **3.10+** (no extra packages)

---

## Usage

```bash
# Show quick usage instructions
python pam_world.py --help-info

# List all available scenarios
python pam_world.py --list

# Evaluate a single scenario (plain)
python pam_world.py --scenario global_war_risk

# Add simulation with 5k runs and show signal breakdown
python pam_world.py --scenario global_war_risk --simulate 5000 --explain

# Focus parsing around a country name (adds as keyword)
python pam_world.py --scenario civil_war_risk --country "Ukraine"

# Run every scenario (summary table)
python pam_world.py --run-all

# Run every scenario with MC simulation
python pam_world.py --run-all --simulate 3000
```

Command-line options:

* `--config <path>`: Custom config file (default `world_config.json`)
* `--scenario <name>`: One scenario to run
* `--country "<name>"`: Bias keyword matching toward a country
* `--simulate <N>`: Monte Carlo runs (0 = off)
* `--explain`: Print signal contributions
* `--run-all`: Evaluate all scenarios
* `--help-info`: Show usage guide
* `--list`: List scenarios

---

## Readable Output

Example single-scenario run:

```
P.A.M. assesses the scenario 'civil_war_risk' with a moderate risk that warrants attention (27.4%).
Monte Carlo mean: 28.5% (5–95% CI 10.2%–49.7%)

Signal contributions:
  domestic_unrest            value=0.70  weight=+2.00  → +1.400
  coup_rumors                value=0.22  weight=+2.20  → +0.484
  state_repression           value=0.22  weight=+1.50  → +0.330
  power_sharing              value=0.54  weight=-1.30  → -0.702
```

---

## Configuration

All settings live in **`world_config.json`**:

* **sources**: RSS/Atom feeds (name, url, type, timeout)
* **signals**: weighted evidence inputs (e.g., mobilization, unrest)
* **hypotheses**: scenarios with priors and a list of signals
* **keyword_sets**: term clusters that drive detection
* **signal_bindings**: which sources and keyword sets power each signal

You can add custom scenarios by editing `hypotheses`. Example:

```json
{"name": "cyberwarfare_risk", "prior": 0.02, "signals": ["diplomatic_breakdown", "mobilization_indicators"]}
```

---

## Included Scenarios

**Conflict (global/regional)**

* `global_war_risk`
* `regional_conflict_asia`
* `regional_conflict_europe`
* `regional_conflict_middleeast`

**Civil/Internal**

* `civil_war_risk`
* `coup_d_etat_risk`
* `mass_protest_risk`

**State Stability**

* `government_collapse_risk`
* `state_fragmentation_risk`

**Nuclear / WMD**

* `nuclear_use_risk`
* `nuclear_accident_risk`
* `chemical_bio_wmd_risk`

**Societal/Environmental**

* `economic_collapse_risk`
* `famine_risk`
* `pandemic_risk`
* `natural_disaster_risk`

> You can append your own hypotheses, signals, and keyword sets without changing the Python script.

---

## Examples

**List scenarios**

```bash
python pam_world.py --list
```

**War risk with explanation and simulation**

```bash
python pam_world.py --scenario global_war_risk --simulate 5000 --explain
```

**Civil war risk with country focus**

```bash
python pam_world.py --scenario civil_war_risk --country "Ukraine"
```

**Nuclear use risk quick check**

```bash
python pam_world.py --scenario nuclear_use_risk
```

---

## Run All Scenarios

```bash
python pam_world.py --run-all
```

Sample output:

```
Running all scenarios:

global_war_risk              →  6.7% (avg 12.2%, range 1.2–36.7%)
civil_war_risk               → 25.8% (avg 32.7%, range 2.0–83.4%)
nuclear_use_risk             →  0.6% (avg  0.7%, range 0.2–1.0%)
economic_collapse_risk       → 10.4% (avg 14.9%, range 3.3–29.2%)
pandemic_risk                →  2.1% (avg  3.5%, range 0.5–7.1%)

Tip: use --scenario <name> --explain for detailed breakdowns.
```

---

## Tips & Troubleshooting

* **DeprecationWarning (UTC)**: Ignore or update code to `datetime.datetime.now(datetime.UTC)`.
* **Feed errors/timeouts**: Some feeds rate-limit; results can vary by time of day/network.
* **Noise vs. signal**: Headlines are noisy. For higher fidelity, integrate structured sources (GDELT, ACLED) by adding new signals & bindings.

---

## Roadmap

* 📈 CSV trend logging (`--log results.csv`) for time-series charts
* 🧭 Per-region keyword sets and custom feed groups
* 🔔 Threshold-based notifications
* 🧪 Unit tests & reproducible fixtures

---

## License

**MIT License** — © 2025 Nathan A. Bowman
You may use, modify, and distribute this project freely with attribution.

```
MIT License

Copyright (c) 2025 Nathan A. Bowman

Permission is hereby granted, free of charge, to any person obtaining a copy
...
SOFTWARE.
```

---

## Background

This project began as a Fallout-inspired experiment: *what if an AI could watch the world’s news and estimate how close we are to disaster?*
**World P.A.M.** converts public information flows into daily probability estimates — a small, transparent early-warning gauge for a complex planet.

---

## Contributing

1. **Star** ⭐ the repo to support visibility.
2. **Fork** and add new signals/feeds (e.g., cyberattacks, sanctions, satellite launches).
3. **PR** your improvements. Tag posts with **#WorldPAM** for community discovery.

**Stay curious, stay critical — and may your probabilities trend toward peace.**
