# DCA-PES

Decline Curve Analysis (DCA) tool for oil and gas production data, built with
Dash and Plotly for interactive modeling and visualization.

## Overview

This project provides a browser-based workflow to:

- upload production datasets
- inspect and filter uploaded columns
- detect production peaks and select relevant date ranges
- fit decline curve models (Hyperbolic, Exponential, Harmonic, Duong, Arps)
- compare forecast curves and summary metrics
- run Monte Carlo uncertainty analysis
- export fitted results to CSV or Excel

## Repository structure

```text
dca_pes/
├── __init__.py
├── DCA04.py          Core DCA and Monte Carlo logic
├── DashInteface.py    Dash application entry point

data/
├── BarnetteShaleTarrant.csv
├── BarnettShaleDenton.csv
├── BarnettShaleJohnson.csv
├── HuntsvilleShale.csv
├── WagnerRecordedData2018-2020.csv
├── WagnerUnitTotal.csv

examples/
└── monte_carlo/
    └── monte_carlo.py

tools/
├── check_version.py
├── library_installer.py

docs/
└── notes.md

requirements.txt
LICENSE
README.md
```

## Installation

Create a Python environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you are using the bundled environment included in this workspace, you can also run:

```bash
source proccess_env/bin/activate
```

## Run the app

From the project root:

```bash
python dca_pes/DashInteface.py
```

Or with module execution:

```bash
python -m dca_pes.DashInteface
```

The app will launch a local Dash server and open the dashboard in the browser.

## Notes

- The working environment in this workspace uses the bundled virtual environment in `proccess_env/` for local execution.
- If Dash is missing in your active interpreter, reinstall dependencies with `python -m pip install -r requirements.txt`.
- The project is still under active development, and the app layout and callback logic continue to evolve.

## Developer utilities

```bash
python tools/check_version.py
python tools/library_installer.py
```

These scripts help validate dependency versions and install missing Python packages for a given script.
