#!/bin/bash

# Temporary file to indicate installation in progress
INSTALL_FLAG="/tmp/glpk_install_in_progress.flag"

# Path to Intel Python installed via Homebrew
INTEL_PYTHON_PATH="/usr/local/opt/python@3.9/bin/python3.9"

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

# Set the repository URL and branch name
REPO_URL="https://github.com/sandialabs/snl-quest.git"
BRANCH_NAME="snl_libraries"

# Set the sparse checkout directory
SPARSE_DIR="snl_libraries/snl_btm"

# Set the path to the virtual environment
VENV_PATH="$(dirname "$0")/../../../app_envs/env_btm"

# Set the path to the sparse checkout directory within the virtual environment
CHECKOUT_PATH="$VENV_PATH/snl-quest/$SPARSE_DIR"

# Check if Intel Python is installed
if [ ! -x "$INTEL_PYTHON_PATH" ]; then
    echo "Intel Python is not installed. Please install it using Homebrew for Intel."
    echo "Run the following command in a terminal with Rosetta enabled:"
    echo "arch -x86_64 /usr/local/bin/brew install python@3.9"
    exit 1
fi

echo "Checking for virtual environment..."
# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment using Intel Python..."
    arch -x86_64 "$INTEL_PYTHON_PATH" -m venv "$VENV_PATH"
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment..."
# Activate the virtual environment
source "$VENV_PATH/bin/activate"

echo "Downgrading pip to <24.1..."
# Downgrade pip to a version below 24.1
pip install "pip<24.1"

echo "Checking Python architecture..."
python -V
uname -m

echo "Cloning repository with sparse checkout..."
# Clone the repository without checking out files
if [ ! -d "$VENV_PATH/snl-quest" ]; then
    git clone --no-checkout -b "$BRANCH_NAME" "$REPO_URL" "$VENV_PATH/snl-quest"
fi

# Navigate to the cloned repository
cd "$VENV_PATH/snl-quest"

# Enable sparse checkout
git sparse-checkout init

# Set sparse checkout path to include only the desired directory
git sparse-checkout set "$SPARSE_DIR"

# Check out the branch
git checkout "$BRANCH_NAME"

# Ensure the sparse checkout directory exists
if [ ! -d "$CHECKOUT_PATH" ]; then
    echo "Sparse checkout failed. Directory $SPARSE_DIR does not exist."
    exit 1
fi

echo "Installing Python package..."
# Install the Python package within the virtual environment
pip install -e "$CHECKOUT_PATH" --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install kivy-garden==0.1.5 --trusted-host pypi.org --trusted-host files.pythonhosted.org

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

GARDEN_PATH="$VENV_PATH/bin/garden"
echo "Garden Path: $GARDEN_PATH"
chmod +x "$GARDEN_PATH"
"$GARDEN_PATH" install matplotlib

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Setup complete."
