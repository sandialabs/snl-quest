#!/bin/bash

set -e

# Set Input Variables
PACKAGE_NAME="quest"
QUEST_ENV="quest_20"
INSTALL_DIR="$(pwd)"

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

# Set up virtual environment
if [ ! -d "$QUEST_ENV" ]; then
    echo "Creating a virtual environment: $QUEST_ENV"
    python3 -m ensurepip --upgrade
    python3 -m pip install virtualenv
    python3 -m virtualenv $QUEST_ENV
fi

# Activate virtual environment
source $QUEST_ENV/bin/activate

# Check if the package is already installed
if ! pip show $PACKAGE_NAME > /dev/null 2>&1; then
    echo "Installing $PACKAGE_NAME package..."
    pip install -e .
else
    echo "$PACKAGE_NAME package is already installed."
fi

# Run the package
echo "Running $PACKAGE_NAME package..."
python -m $PACKAGE_NAME

# Deactivate virtual environment
deactivate

echo "$PACKAGE_NAME ran successfully."
