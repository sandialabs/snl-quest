#!/bin/bash
set -e

PYTHON_BIN="${QUEST_PYTHON:-python3}"
VENV_PATH="$(cd "$(dirname "$0")" && pwd)/../../../app_envs/env_tech"
LOCAL_TECH_PATH="$(cd "$(dirname "$0")" && pwd)/../../../snl_libraries/snl_tech_selection"
TARGET_PYTHON_VERSION="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

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

if [ -d "$VENV_PATH" ] && [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Existing Tech Selection environment is incomplete. Recreating it..."
    rm -rf "$VENV_PATH"
fi

if [ -f "$VENV_PATH/bin/python3" ]; then
    EXISTING_PYTHON_VERSION="$("$VENV_PATH/bin/python3" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
    if [ -n "$EXISTING_PYTHON_VERSION" ] && [ "$EXISTING_PYTHON_VERSION" != "$TARGET_PYTHON_VERSION" ]; then
        echo "Existing Tech Selection environment uses Python $EXISTING_PYTHON_VERSION but QuESt is using Python $TARGET_PYTHON_VERSION. Recreating it..."
        rm -rf "$VENV_PATH"
    fi
fi

if [ ! -f "$VENV_PATH/bin/activate" ]; then
    "$PYTHON_BIN" -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

export PIP_NO_INDEX=0

if [ ! -f "$LOCAL_TECH_PATH/setup.py" ]; then
    echo "Failed to locate bundled Tech Selection sources at '$LOCAL_TECH_PATH'."
    exit 1
fi

pip install "$LOCAL_TECH_PATH"

install_glpk

deactivate
