# Cosmic-os
COSMIC OPERATING SYSTEM - Procedural god engine with particle physics

## Running the dashboard

```bash
python cosmic_dashboard.py
```

The app serves an animated FastAPI dashboard on `http://127.0.0.1:8080` with audit-backed intelligence upgrades, a live status feed, pantheon filtering, runtime metadata, and rarity metrics.

## Screenshot workflows

### Browser screenshot (recommended for the dashboard)

Use the Playwright-based helper to capture a real browser rendering of the app:

```bash
python scripts/browser_screenshot.py screenshots/browser_dashboard.png --url http://127.0.0.1:8080/
```

Install the browser automation dependency once, then provide either a Playwright-managed browser or a system Chromium binary:

```bash
pip install -r requirements.txt
python -m playwright install chromium
# or, if the Playwright CDN is blocked:
sudo apt update && sudo apt install -y chromium
```

The helper automatically uses `BROWSER_EXECUTABLE` when set, otherwise it looks for `chromium`, `chromium-browser`, or `google-chrome` on `PATH` before falling back to Playwright's managed browser.

### Desktop/Xvfb screenshot helper

A shell helper is also included for environments that have an attached GUI or need a headless Xvfb session:

```bash
./scripts/take_screenshot.sh
```

To install a supported screenshot backend on Ubuntu, use one of the following:

```bash
sudo apt update && sudo apt install -y xvfb scrot xclip
sudo apt update && sudo apt install -y grim slurp wl-clipboard
sudo apt update && sudo apt install -y flameshot
```

The helper automatically starts `Xvfb` on `:99` when no `DISPLAY` is set and `Xvfb` is installed. You can override the virtual display resolution with `SCREENSHOT_RESOLUTION`, for example:

```bash
SCREENSHOT_RESOLUTION=1366x768x24 ./scripts/take_screenshot.sh screenshots/cosmic_dashboard.png
```

## Automated checks

Regression coverage is available with Python's built-in unittest runner:

```bash
python -m unittest discover -s tests
```
