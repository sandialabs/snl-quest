#!/bin/bash

# # Ensure the script is running under Rosetta
# if [[ $(uname -m) != "x86_64" ]]; then
#     echo "This script must be run in an x86_64 (Rosetta) terminal."
#     echo "Right-click Terminal > Get Info > Check 'Open using Rosetta'."
#     exit 1
# fi

# # Settings
# VENV_DIR="venv"
# PYTHON_VERSION="3.9"
# PYTHON_PATH="/usr/local/bin/python3.9"

# # Step 1: Check if venv exists
# if [ ! -d "$VENV_DIR" ]; then
#     if [ ! -x "$PYTHON_PATH" ]; then
#         echo "Python ${PYTHON_VERSION} not found at expected path: $PYTHON_PATH"
#         echo "Make sure x86_64 Homebrew is installed and run:"
#         echo "/usr/local/bin/brew install python@${PYTHON_VERSION}"
#         exit 1
#     fi

#     echo "Creating virtual environment in ./$VENV_DIR"
#     "$PYTHON_PATH" -m venv "$VENV_DIR"
# fi

# # Step 2: Activate the venv
# source "$VENV_DIR/bin/activate"

# # Step 3: Check if 'quest' is installed in editable mode
# if ! pip show -f quest 2>/dev/null | grep -q 'Editable project location'; then
#   echo "Installing QuESt"
#   pip install -e .
# else
#   echo "QuESt is already installed. Launching QuESt"

# fi
# # Step 4: Run the package
# python -m quest

echo "macOS install test"