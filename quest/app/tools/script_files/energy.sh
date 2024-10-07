#!/bin/bash

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
# Set the path to the virtual environment and requirements file using the updated paths
VENV_PATH="$(dirname "$0")/../../../app_envs/env_energy"
REQ_PATH="$(dirname "$0")/../reqs/energy_reqs.txt"

# Set the equity directory name
equity_dir="equity"

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"
sudo apt-get install -y python3-dev libblas-dev liblapack-dev gfortran
# Install requirements from the requirements file
pip install -r "$REQ_PATH"

# Create a directory within the virtual environment
mkdir -p "$VENV_PATH/$equity_dir"

# Clone the GitHub repository
git clone https://github.com/sandialabs/snl-quest-equity.git "$VENV_PATH/equity"
EQUITY_PATH="$(dirname "$0")/../../../app_envs/env_energy/equity/main.py"
# Try to install GLPK via package manager
if ! attempt_install_via_package_manager; then
    echo "Failed to install GLPK via package manager. Please install GLPK manually."
fi
GARDEN_PATH="$(dirname "$0")/../../../app_envs/env_energy/bin/garden"
echo "Garden Path: $GARDEN_PATH"
chmod +x $GARDEN_PATH
"$GARDEN_PATH" install matplotlib
chmod +x $EQUITY_PATH
# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Setup complete."

