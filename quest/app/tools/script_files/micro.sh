#!/bin/bash
set -e

VENV_PATH="$(cd "$(dirname "$0")" && pwd)/../../../app_envs/env_micro"

python3 -m venv "$VENV_PATH"

source "$VENV_PATH/bin/activate"

pip install quest-ssim==1.0.0b3

deactivate
