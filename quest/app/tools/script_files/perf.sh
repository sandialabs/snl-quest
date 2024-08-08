#!/bin/bash

LOCKFILE="/tmp/glpk_install.lock"

# Function to check if GLPK is installed
is_glpk_installed() {
    if command -v glpsol &> /dev/null; then
        echo "GLPK is already installed."
        return 0
    else
        return 1
    fi
}

# Function to install GLPK on Ubuntu/Debian
install_glpk_on_debian() {
    echo "Installing GLPK on Ubuntu/Debian..."
    sudo apt-get update
    sudo apt-get install -y glpk-utils libglpk-dev
}

# Function to install GLPK on Fedora
install_glpk_on_fedora() {
    echo "Installing GLPK on Fedora..."
    sudo dnf install -y glpk glpk-devel
}

# Function to install GLPK on Arch Linux
install_glpk_on_arch() {
    echo "Installing GLPK on Arch Linux..."
    sudo pacman -Sy --noconfirm glpk
}

# Function to install GLPK on macOS (using Homebrew)
install_glpk_on_macos() {
    echo "Installing GLPK on macOS..."
    brew install glpk
}

# Attempt to install GLPK via package manager based on OS
attempt_install_via_package_manager() {
    OS="`uname`"
    case $OS in
      'Linux')
        DISTRO="`grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '\"'`"
        case $DISTRO in
          'ubuntu' | 'debian')
            install_glpk_on_debian
            return 0
            ;;
          'fedora')
            install_glpk_on_fedora
            return 0
            ;;
          'arch' | 'manjaro')
            install_glpk_on_arch
            return 0
            ;;
          *)
            echo "Unsupported Linux distribution for package manager installation: $DISTRO"
            return 1
            ;;
        esac
        ;;
      'Darwin')
        install_glpk_on_macos
        return 0
        ;;
      *)
        echo "Unsupported operating system for package manager installation: $OS"
        return 1
        ;;
    esac
}

# Function to acquire a lock
acquire_lock() {
    exec 200>$LOCKFILE
    flock -n 200 && return 0 || return 1
}

# Function to release the lock
release_lock() {
    flock -u 200
    rm -f $LOCKFILE
}

# Set the path to the virtual environment and setup.py
VENV_PATH="$(dirname "$0")/../../../app_envs/env_perf"
SETUP_PATH="$(dirname "$0")/../../../snl_libraries/snl_performance"

echo "Checking for virtual environment..."
# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment..."
# Activate the virtual environment
source "$VENV_PATH/bin/activate"

echo "Installing Python package..."
# Install the Python package within the virtual environment
pip install "$SETUP_PATH"
pip install kivy-garden==0.1.5

# Check if GLPK is installed
if ! is_glpk_installed; then
    # Try to acquire the lock
    if acquire_lock; then
        echo "Acquired lock. Installing GLPK..."
        # Try to install GLPK via package manager
        if ! attempt_install_via_package_manager; then
            echo "Failed to install GLPK via package manager. Please install GLPK manually."
        fi
        # Release the lock
        release_lock
    else
        echo "Could not acquire lock. Another installation is in progress. Waiting..."
        # Wait for the lock to be released
        while ! acquire_lock; do
            sleep 1
        done
        echo "Acquired lock after waiting. Checking GLPK installation..."
        # Check if GLPK is installed again after acquiring the lock
        if ! is_glpk_installed; then
            echo "GLPK is still not installed. Installing GLPK..."
            if ! attempt_install_via_package_manager; then
                echo "Failed to install GLPK via package manager. Please install GLPK manually."
            fi
        else
            echo "GLPK was installed by another process."
        fi
        release_lock
    fi
fi

GARDEN_PATH="$VENV_PATH/bin/garden"
echo "Garden Path: $GARDEN_PATH"
chmod +x $GARDEN_PATH
"$GARDEN_PATH" install matplotlib

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Setup complete."
