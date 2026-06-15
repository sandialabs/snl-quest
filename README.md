# QuESt Valuation

QuESt Valuation is a Sandia National Laboratories application for estimating
the maximum potential revenue of grid-connected energy storage systems using
historical market data. It helps evaluate value-stacking opportunities such as
energy arbitrage and ancillary-service participation.

This repository branch contains the standalone `snl_valuation` package used by
the main QuESt application installer.

## Features

- Energy storage valuation workflows
- Historical market data analysis
- Pyomo-based optimization models
- Batch runs and parameter-sweep studies
- Report and chart generation for optimization results

## Requirements

- Windows, macOS, or Linux
- Python 3.9 is recommended for the current dependency set
- A Pyomo-compatible optimization solver, such as GLPK
- Microsoft Visual C++ Redistributable on Windows for native Python wheels

The main QuESt Windows installer provisions Python 3.9.13, GLPK, and the Visual
C++ runtime automatically for this app environment.

## Installation

Install from this package branch:

```bash
python -m pip install "https://github.com/sandialabs/snl-quest/archive/refs/heads/QuESt_Valuation.zip"
```

For local development from a checkout of this package:

```bash
python -m pip install -e .
```

## Running

After installation, launch the app with:

```bash
valuation
```

When installed through the main QuESt application, use the QuESt home screen to
install and launch QuESt Valuation.

## Data Inputs

Valuation workflows rely on market and operations data prepared by QuESt Data
Manager. If an expected market, year, or revenue stream is unavailable, download
the relevant data through QuESt Data Manager before running the valuation tool.

## Solver Notes

Valuation optimization workflows require a solver available to Pyomo. GLPK is
the default open-source option used by the QuESt installer. If you use a
different solver, make sure it is installed and discoverable on your system path
or configured in QuESt.

## License

QuESt Valuation is distributed under the BSD 3-clause license. See `LICENSE` for
details.

## Contact

For issues, feedback, or questions, use the GitHub issue tracker for the main
QuESt repository.

Maintainer: Tu Nguyen, `tunguy@sandia.gov`
