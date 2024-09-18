#!/bin/bash

set -e

# Set Input Variables
PYTHON_VERSION="3.9.13"
TARGET_PY_VERSION="Python $PYTHON_VERSION"
PYTHON_URL="https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
PACKAGE_NAME="quest"
QUEST_ENV="quest_20"
INSTALL_DIR="$(pwd)/$QUEST_ENV/Python_3.9.13"

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

# Check if Python is installed system-wide
if ! command -v python3 &> /dev/null
then
    echo "Python is not installed..."
    echo "Downloading Python Installer from python.org..."
    curl -o python-installer.tgz $PYTHON_URL
    echo "Installing Python..."
    tar -xzf python-installer.tgz
    cd Python-$PYTHON_VERSION
    ./configure --prefix=$INSTALL_DIR
    make
    make install
    cd ..
    rm -rf Python-$PYTHON_VERSION python-installer.tgz
else
    SYS_PY_VERSION=$(python3 --version)
    echo "Current Python: $SYS_PY_VERSION"
    echo "Target Python: $TARGET_PY_VERSION"
    if [[ "$SYS_PY_VERSION" != "$TARGET_PY_VERSION" ]]; then
        echo "Installing local Python $PYTHON_VERSION..."
        curl -o python-installer.tgz $PYTHON_URL
        tar -xzf python-installer.tgz
        cd Python-$PYTHON_VERSION
        ./configure --prefix=$INSTALL_DIR
        make
        make install
        cd ..
        rm -rf Python-$PYTHON_VERSION python-installer.tgz
    fi
fi

# Set up virtual environment
if [ ! -d "$QUEST_ENV" ]; then
    echo "Creating a virtual environment: $QUEST_ENV"
    python3 -m pip install --upgrade pip
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
