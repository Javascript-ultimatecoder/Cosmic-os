#!/usr/bin/env bash
set -euo pipefail

output_path="${1:-screenshots/cosmic_$(date +%Y%m%d_%H%M%S).png}"
resolution="${SCREENSHOT_RESOLUTION:-1920x1080x24}"
xvfb_display="${XVFB_DISPLAY:-:99}"
shift || true

mkdir -p "$(dirname "$output_path")"

xvfb_pid=""
cleanup() {
  if [[ -n "$xvfb_pid" ]] && kill -0 "$xvfb_pid" 2>/dev/null; then
    kill "$xvfb_pid" >/dev/null 2>&1 || true
    wait "$xvfb_pid" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

ensure_display() {
  if [[ -n "${DISPLAY:-}" ]]; then
    return 0
  fi

  if command -v Xvfb >/dev/null 2>&1; then
    Xvfb "$xvfb_display" -screen 0 "$resolution" >/tmp/cosmic_xvfb.log 2>&1 &
    xvfb_pid="$!"
    sleep 1
    export DISPLAY="$xvfb_display"
    return 0
  fi

  cat >&2 <<'EOF'
No graphical display is available.
Install Xvfb for a headless virtual display:
  sudo apt update && sudo apt install -y xvfb scrot xclip
EOF
  return 1
}

capture_with_scrot() {
  scrot "$output_path"
  xclip -selection clipboard -t image/png -i "$output_path" 2>/dev/null || true
  printf 'Saved screenshot to %s using scrot\n' "$output_path"
}

capture_with_grim() {
  grim "$output_path"
  printf 'Saved screenshot to %s using grim\n' "$output_path"
}

capture_with_flameshot() {
  flameshot full -p "$output_path"
  printf 'Saved screenshot to %s using flameshot\n' "$output_path"
}

if command -v scrot >/dev/null 2>&1; then
  ensure_display
  capture_with_scrot
  exit 0
fi

if command -v grim >/dev/null 2>&1; then
  if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
    capture_with_grim
    exit 0
  fi
  printf 'grim is installed but WAYLAND_DISPLAY is not set; attach a Wayland session before capturing.\n' >&2
  exit 1
fi

if command -v flameshot >/dev/null 2>&1; then
  ensure_display
  capture_with_flameshot
  exit 0
fi

cat >&2 <<'EOF'
No supported screenshot tool was found.
Install one of the following and rerun:
  sudo apt update && sudo apt install -y xvfb scrot xclip
  sudo apt update && sudo apt install -y grim slurp wl-clipboard
  sudo apt update && sudo apt install -y flameshot
EOF
exit 1
