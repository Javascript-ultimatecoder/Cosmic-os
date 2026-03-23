#!/usr/bin/env bash
set -euo pipefail

venv_path="${1:-.venv-screenshot}"
python_bin="${PYTHON_BIN:-python3}"

if ! command -v "$python_bin" >/dev/null 2>&1; then
  echo "Python interpreter '$python_bin' was not found." >&2
  exit 1
fi

"$python_bin" -m venv "$venv_path"
# shellcheck disable=SC1090
source "$venv_path/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements-screenshot.txt

if python -m playwright install chromium; then
  echo "Playwright Chromium installed successfully in $venv_path"
else
  echo "WARNING: Playwright Chromium install failed. You can still use a system browser or rerun later." >&2
fi

echo "Screenshot environment ready at $venv_path"
echo "Activate it with: source $venv_path/bin/activate"
