# DCA-PES

Decline Curve Analysis (DCA) tool for oil/gas well production data, with a
Dash-based web interface.

## Structure

```
dca_pes/            Active application
├── DCA04.py           Core decline-curve analysis / curve-fitting logic
└── DashInteface.py     Dash web UI (entry point)

data/                Sample well-production CSVs used for testing/demoing
tools/               Dev utilities
├── check_version.py    Reports installed versions of dca_pes's dependencies
└── library_installer.py  Auto-installs missing imports for an arbitrary script

examples/monte_carlo/  Standalone Monte Carlo example script

docs/notes.md        Misc working notes

archive/             Superseded/earlier versions, kept for reference only
├── v1_root/            Original root-level DCA04.py / DashInteface.py (pre-V2)
├── new_codes/            Earlier experimental variant, incl. a tkinter-based UI
└── tk_prototype/          Early Tkinter UI prototype (v0-1.py)
```

`dca_pes/` was previously named `V2/`; it's the actively maintained version as
of the most recent commits. Everything under `archive/` is not maintained and
is kept only for history — don't build on it.

## Setup

```bash
pip install -r requirements.txt
python -m dca_pes.DashInteface
```

## Dev utilities

```bash
python tools/check_version.py       # print installed versions of dca_pes deps
python tools/library_installer.py   # auto-install imports missing from a script
```
