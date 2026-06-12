#!/usr/bin/env sh
set -eu

MODEL_URL="https://github.com/netology-code/py-homeworks-web/raw/new/2.4-celery/upscale/EDSR_x2.pb"
PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

curl -L "$MODEL_URL" -o "$PROJECT_DIR/EDSR_x2.pb"
echo "Downloaded model to $PROJECT_DIR/EDSR_x2.pb"
