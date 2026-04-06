#!/bin/bash
set -e

VENV_PATH="$(cd "$(dirname "$0")" && pwd)/../../../app_envs/env_viz"
REQ_PATH="$(cd "$(dirname "$0")" && pwd)/../reqs/viz_requirements.txt"

python3 -m venv "$VENV_PATH"

source "$VENV_PATH/bin/activate"

pip install -r "$REQ_PATH"

deactivate
