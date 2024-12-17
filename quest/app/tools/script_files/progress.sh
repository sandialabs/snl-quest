#!/bin/bash

# Temporary file to indicate installation in progress
INSTALL_FLAG="/tmp/glpk_install_in_progress.flag"

# Function to check if GLPK is installed
check_glpk_installed() {
    command -v glpsol >/dev/null 2>&1
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

# Function to install GLPK on macOS from source
install_glpk_on_macos() {
    echo "Installing GLPK on macOS from source..."
    GLPK_TAR="glpk-latest.tar.gz"
    curl -O https://ftp.gnu.org/gnu/glpk/$GLPK_TAR
    tar -xzf $GLPK_TAR
    GLPK_DIR=$(tar -tf $GLPK_TAR | head -n 1 | cut -f1 -d"/")
    
    # Run installation commands without changing directories
    ./configure --prefix=/usr/local "$GLPK_DIR"
    make -C "$GLPK_DIR"
    sudo make -C "$GLPK_DIR" install
    rm -rf $GLPK_TAR "$GLPK_DIR"
}

# Attempt to install GLPK via package manager based on OS
attempt_install_via_package_manager() {
    OS="$(uname)"
    case $OS in
      'Linux')
        DISTRO="$(grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '\"')"
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
VENV_PATH="$(dirname "$0")/../../../app_envs/env_progress"
SETUP_PATH="$(dirname "$0")/../../../app_envs/env_progress/snl_quest_progress"

# Set the equity directory name
progress_dir="snl_quest_progress"

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Install system dependencies
sudo apt-get install -y python3-dev libblas-dev liblapack-dev gfortran



# Create a directory within the virtual environment
mkdir -p "$VENV_PATH/$progress_dir"

# Clone the GitHub repository
git clone https://github.com/sandialabs/quest_progress.git "$VENV_PATH/snl_quest_progress"

# Install using setup.py
pip install -e "$SETUP_PATH"
# Check if GLPK is already installed
if check_glpk_installed; then
    echo "GLPK is already installed."
else
    # Check if installation is in progress
    if [ -e "$INSTALL_FLAG" ]; then
        echo "GLPK installation is already in progress. Skipping GLPK installation."
    else
        # Create the installation flag file
        touch "$INSTALL_FLAG"

        # Ensure the flag file is removed on exit
        trap 'rm -f "$INSTALL_FLAG"' EXIT

        echo "GLPK is not installed. Installing..."
        # Try to install GLPK via package manager
        if ! attempt_install_via_package_manager; then
            echo "Failed to install GLPK. Please install it manually."
        fi
    fi
fi


# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Setup complete."
