#!/bin/bash

set -e

# Get the current working directory
INSTALL_DIR="$(pwd)"

# Set Input Variables
PACKAGE_NAME="quest"
QUEST_ENV="quest_20"
PYTHON_TAR="$INSTALL_DIR/portable_python/Python-3.9.13.tgz"
PYTHON_DIR="$INSTALL_DIR/portable_python/Python-3.9.13"

# Unzip the Python distribution if it doesn't exist
if [ ! -d "$PYTHON_DIR" ]; then
    echo "Unzipping Python distribution..."
    tar -xzf "$PYTHON_TAR" -C "$INSTALL_DIR/portable_python"
    
    # Check if the unzip was successful
    if [ -d "$PYTHON_DIR" ]; then
        echo "Deleting the tar file..."
        rm "$PYTHON_TAR"
    else
        echo "Failed to unzip the Python distribution."
        exit 1
    fi
fi

# Define the path to the Python executable
PYTHON_PATH="$PYTHON_DIR/bin/python3"

# Check if Git is already installed
if ! command -v git &> /dev/null
then
    echo "Git has not been detected..."
    echo "Installing Git..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y git
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install git
    fi
else
    echo "Git is already installed."
fi

# Set up virtual environment using venv
if [ ! -d "$QUEST_ENV" ]; then
    echo "Creating a virtual environment: $QUEST_ENV"
    "$PYTHON_PATH" -m ensurepip --upgrade
    "$PYTHON_PATH" -m venv "$QUEST_ENV"
fi

# Activate virtual environment
source "$QUEST_ENV/bin/activate"

# Check if the package is already installed
if ! pip show "$PACKAGE_NAME" > /dev/null 2>&1; then
    echo "Installing $PACKAGE_NAME package..."
    pip install -e .
else
    echo "$PACKAGE_NAME package is already installed."
fi

# Run the package
echo "Running $PACKAGE_NAME package..."
python -m "$PACKAGE_NAME"

# Deactivate virtual environment
deactivate

echo "$PACKAGE_NAME ran successfully."