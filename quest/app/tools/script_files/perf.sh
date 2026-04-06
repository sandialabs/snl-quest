#!/bin/bash
set -e

REPO_URL="https://github.com/sandialabs/snl-quest.git"
BRANCH_NAME="snl_libraries"
SPARSE_DIR="snl_libraries/snl_performance"
VENV_PATH="$(cd "$(dirname "$0")" && pwd)/../../../app_envs/env_perf"
CHECKOUT_PATH="$VENV_PATH/snl-quest/$SPARSE_DIR"

install_glpk() {
    if command -v glpsol >/dev/null 2>&1; then
        echo "GLPK is already installed."
        return
    fi

    case "$(uname)" in
        Darwin)
            if command -v brew >/dev/null 2>&1; then
                brew install glpk
            else
                echo "Homebrew is required to install GLPK on macOS."
                exit 1
            fi
            ;;
        Linux)
            if command -v apt-get >/dev/null 2>&1; then
                sudo apt-get update
                sudo apt-get install -y glpk-utils libglpk-dev
            elif command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y glpk glpk-devel
            elif command -v pacman >/dev/null 2>&1; then
                sudo pacman -Sy --noconfirm glpk
            else
                echo "Unsupported Linux package manager for GLPK installation."
                exit 1
            fi
            ;;
        *)
            echo "Unsupported operating system: $(uname)"
            exit 1
            ;;
    esac
}

if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

if [ ! -d "$VENV_PATH/snl-quest" ]; then
    git clone --no-checkout -b "$BRANCH_NAME" "$REPO_URL" "$VENV_PATH/snl-quest"
fi

cd "$VENV_PATH/snl-quest"
git sparse-checkout init
git sparse-checkout set "$SPARSE_DIR"
git checkout "$BRANCH_NAME"

if [ ! -d "$CHECKOUT_PATH" ]; then
    echo "Sparse checkout failed. Directory $SPARSE_DIR does not exist."
    exit 1
fi

pip install "$CHECKOUT_PATH"

install_glpk

deactivate
