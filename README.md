# Cosmic-os
COSMIC OPERATING SYSTEM - Procedural god engine with particle physics

## Running the dashboard

```bash
python cosmic_dashboard.py
```

The app serves an animated FastAPI dashboard on `http://127.0.0.1:8080` with audit-backed intelligence upgrades, a live status feed, pantheon filtering, runtime metadata, and rarity metrics.

## Screenshot workflows

### Isolated screenshot environment setup

If you want a dedicated browser screenshot environment, bootstrap it with the included helper:

```bash
./scripts/setup_screenshot_env.sh
source .venv-screenshot/bin/activate
```

The helper creates a local virtual environment, upgrades `pip`, installs `requirements-screenshot.txt`, exports `PLAYWRIGHT_BROWSERS_PATH`, and attempts to install Playwright Chromium. By default, browser binaries are stored inside `<venv>/playwright-browsers`, but you can override that path:

```bash
PLAYWRIGHT_BROWSERS_PATH=/custom/path/to/browsers ./scripts/setup_screenshot_env.sh
```

If the Playwright CDN is blocked, the environment is still usable with a system browser.

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

The helper automatically uses `--executable-path`, `BROWSER_EXECUTABLE`, or common `chromium` / `google-chrome` binaries on `PATH`. You can also control Playwright's managed browser storage with `PLAYWRIGHT_BROWSERS_PATH`.

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


## React infinite-scroll frontend

A separate Vite/React frontend is available under `transcendence-frontend/` for a virtualized pantheon experience powered by `react-window` and `react-window-infinite-loader`.

```bash
cd transcendence-frontend
npm install
npm run dev
```

By default it talks to `http://127.0.0.1:8080`, or you can override the backend with `VITE_API_BASE_URL`.
