# FireSight Prototype

This repository contains a simple prototype for the FireSight user interface. It now also includes scripts for generating demo datasets used during development and testing.

## Demo Data Scripts

The `scripts` directory contains two helper utilities:

- `generate_demo_dataset.py` – creates a 24‑hour CSV file with simulated sensor readings and a fire ignition event around noon.
- `replay_fire_scenario.py` – prints dataset rows to the console in sequence so the scenario can be replayed quickly for demos.

### Dataset format

The generated CSV has the following columns:

| column | description |
| --- | --- |
| `timestamp` | ISO‑8601 timestamp for each minute of the day |
| `temperature_c` | temperature in Celsius |
| `humidity_pct` | relative humidity percentage |
| `co2_ppm` | CO₂ concentration in ppm |
| `smoke` | `0` or `1` to indicate smoke detection |
| `flame` | `0` or `1` to indicate flame detection |

The ignition event increases temperature and CO₂ while setting both `smoke` and `flame` to `1` for approximately 15 minutes.

To create the dataset run:

```bash
python3 scripts/generate_demo_dataset.py demo_dataset.csv
```

Then replay it with:

```bash
python3 scripts/replay_fire_scenario.py demo_dataset.csv
```
