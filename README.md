# Cosmic-os
COSMIC OPERATING SYSTEM - Procedural god engine with particle physics

## Running the dashboard

```bash
python cosmic_dashboard.py
```

The app serves an animated FastAPI dashboard on `http://127.0.0.1:8080` with audit-backed intelligence upgrades, a live status feed, pantheon filtering, and rarity metrics.

## Screenshot workflow

A helper script is included for environments that have an attached GUI or Wayland/X11 session:

```bash
./scripts/take_screenshot.sh
```

To install a supported screenshot backend on Ubuntu, use one of the following:

```bash
sudo apt update && sudo apt install -y scrot xclip
sudo apt update && sudo apt install -y grim slurp wl-clipboard
sudo apt update && sudo apt install -y flameshot
```

You can also pass a custom output path:

```bash
./scripts/take_screenshot.sh screenshots/cosmic_dashboard.png
```

If no graphical session is attached, the script exits with a clear message explaining which display variable is missing.
