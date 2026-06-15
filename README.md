# QuESt Behind the Meter

QuESt Behind the Meter (BTM) is a Sandia National Laboratories application for
analyzing behind-the-meter energy storage use cases. The current tool focuses on
estimating customer cost savings for time-of-use and net-energy-metering rate
structures.

This repository branch contains the standalone `snl_btm` package used by the
main QuESt application installer.

## Features

- Behind-the-meter cost-savings workflow
- Support for load profiles, PV profiles, and utility rate structures prepared
  by QuESt Data Manager
- Pyomo-based optimization models
- Report and chart generation for optimization results

## Requirements

- Windows, macOS, or Linux
- Python 3.9 is recommended for the current dependency set
- A Pyomo-compatible linear-programming solver, such as GLPK
- Microsoft Visual C++ Redistributable on Windows for native Python wheels

The main QuESt Windows installer provisions Python 3.9.13, GLPK, and the Visual
C++ runtime automatically for this app environment.

## Installation

Install from this package branch:

```bash
python -m pip install "https://github.com/sandialabs/snl-quest/archive/refs/heads/QuESt_BTM.zip"
```

For local development from a checkout of this package:

```bash
python -m pip install -e .
```

## Running

After installation, launch the app with:

```bash
btm
```

When installed through the main QuESt application, use the QuESt home screen to
install and launch QuESt BTM.

## Data Inputs

BTM expects data in the structure produced by QuESt Data Manager:

- Rate structures as JSON files
- PV profiles as JSON files
- Load profiles as CSV files

Custom data can be added when it follows the same formats used by QuESt Data
Manager.

## Solver Notes

BTM optimization workflows require a solver available to Pyomo. GLPK is the
default open-source option used by the QuESt installer. If you use a different
solver, make sure it is installed and discoverable on your system path or
configured in QuESt.

## License

QuESt Behind the Meter is distributed under the BSD 3-clause license. See
`LICENSE` for details.

## Contact

For issues, feedback, or questions, use the GitHub issue tracker for the main
QuESt repository.

Maintainer: Tu Nguyen, `tunguy@sandia.gov`
