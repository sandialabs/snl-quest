# QuESt Performance

QuESt Performance is the QuESt application for analyzing battery energy storage
system performance impacts from parasitic heating, ventilation, and air
conditioning loads. It uses EnergyPlus building simulation inputs to estimate
the energy consumption associated with battery housing and thermal management.

This branch contains only the `snl_performance` package from the QuESt
application suite so it can be installed independently by the QuESt app hub.

## Installation

Install directly from this branch:

```bash
python -m pip install --upgrade --force-reinstall "https://github.com/snl-quest/snl-quest/archive/refs/heads/QuESt_Performance.zip"
```

The package requires Python 3.6 or newer. The QuESt app hub installer manages a
dedicated app environment and installs this branch automatically.

## Running

After installation, launch the app with either command:

```bash
performance
```

or:

```bash
python -m performance
```

## Package Contents

- `performance/`: QuESt Performance application package and GUI resources.
- `setup.py`: Python package metadata and console entry point.
- `requirements.txt`: Runtime dependencies used by the package.

## Notes

QuESt Performance is part of the Sandia National Laboratories QuESt application
suite for energy storage analysis. The full QuESt source tree includes other
applications such as BTM, Valuation, Technology Selection, and Data Manager.

For issues or feedback, use the GitHub issue tracker for the main QuESt
repository.
