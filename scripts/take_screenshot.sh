#!/usr/bin/env bash
set -euo pipefail

output_path="${1:-screenshots/cosmic_$(date +%Y%m%d_%H%M%S).png}"
mkdir -p "$(dirname "$output_path")"

if command -v scrot >/dev/null 2>&1; then
  if [[ -n "${DISPLAY:-}" ]]; then
    scrot "$output_path"
    printf 'Saved screenshot to %s using scrot\n' "$output_path"
    exit 0
  fi
  printf 'scrot is installed but DISPLAY is not set; attach a GUI session before capturing.\n' >&2
  exit 1
fi

if command -v grim >/dev/null 2>&1; then
  if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
    grim "$output_path"
    printf 'Saved screenshot to %s using grim\n' "$output_path"
    exit 0
  fi
  printf 'grim is installed but WAYLAND_DISPLAY is not set; attach a Wayland session before capturing.\n' >&2
  exit 1
fi

if command -v flameshot >/dev/null 2>&1; then
  if [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    flameshot full -p "$output_path"
    printf 'Saved screenshot to %s using flameshot\n' "$output_path"
    exit 0
  fi
  printf 'flameshot is installed but no graphical session variables are available.\n' >&2
  exit 1
fi

cat >&2 <<'EOF'
No supported screenshot tool was found.
Install one of the following and rerun:
  sudo apt update && sudo apt install -y scrot xclip
  sudo apt update && sudo apt install -y grim slurp wl-clipboard
  sudo apt update && sudo apt install -y flameshot
EOF
exit 1
