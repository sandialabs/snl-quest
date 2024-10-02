#!/bin/bash

set -e

# Set Input Variables
PYTHON_VERSION="3.9.13"
TARGET_PY_VERSION="Python $PYTHON_VERSION"
PYTHON_URL="https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
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

# Function to check Python version
check_python_version() {
    PYTHON_CMD=$1
    VERSION_OUTPUT=$($PYTHON_CMD --version 2>&1)
    if [[ "$VERSION_OUTPUT" == "$TARGET_PY_VERSION"* ]]; then
        return 0 # 0 means true/success in bash
    else
        return 1 # 1 means false/error in bash
    fi
}

# Check if Python is installed system-wide
if command -v python3 &> /dev/null && check_python_version "python3"
then
    echo "Python $PYTHON_VERSION is already installed system-wide."
    PYTHON_INSTALLED=true
elif [ -x "$INSTALL_DIR/bin/python3" ] && check_python_version "$INSTALL_DIR/bin/python3"
then
    echo "Python $PYTHON_VERSION is already installed in the current directory."
    PYTHON_INSTALLED=true
    export PATH=$INSTALL_DIR/bin:$PATH
else
    echo "Python $PYTHON_VERSION is not installed..."
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
    PYTHON_INSTALLED=true
    export PATH=$INSTALL_DIR/bin:$PATH
fi

# Set up virtual environment
if [ ! -d "$QUEST_ENV" ] && [ "$PYTHON_INSTALLED" = true ]; then
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
