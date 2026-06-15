# QuESt Technology Selection

QuESt Technology Selection is a Sandia National Laboratories application for
identifying energy storage technologies that are compatible with a given project
or use case. The tool filters storage technologies against project requirements
and ranks the remaining options by compatibility.

This repository branch contains the standalone `snl_tech_selection` package
used by the main QuESt application installer.

## Features

- Energy storage technology screening
- Compatibility scoring for multiple use cases
- Data-driven filtering of candidate storage technologies
- Interactive Kivy-based user interface
- Report and chart generation for technology-selection results

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
python -m pip install "https://github.com/sandialabs/snl-quest/archive/refs/heads/QuESt_Tech_Selection.zip"
```

For local development from a checkout of this package:

```bash
python -m pip install -e .
```

## Running

After installation, launch the app with the console command created by the
package:

```bash
tech_selection
```

You can also launch the package as a Python module:

```bash
python -m tech_selection
```

When installed through the main QuESt application, use the QuESt home screen to
install and launch QuESt Technology Selection.

## Data Inputs

Technology Selection uses technology and application data packaged with the app.
For best results, review project requirements carefully before running the
selection workflow, including use case, power and energy needs, site constraints,
and any performance requirements.

## Solver Notes

Some workflows use Pyomo-compatible optimization components. GLPK is the default
open-source solver used by the QuESt installer. If you use a different solver,
make sure it is installed and discoverable on your system path or configured in
QuESt.

## License

QuESt Technology Selection is distributed under the BSD 3-clause license. See
`LICENSE` for details.

## Contact

For issues, feedback, or questions, use the GitHub issue tracker for the main
QuESt repository.

Maintainer: Tu Nguyen, `tunguy@sandia.gov`
