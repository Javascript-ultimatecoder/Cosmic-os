# Cosmic-os
COSMIC OPERATING SYSTEM - Procedural god engine with particle physics


## Running the dashboard

```bash
python cosmic_dashboard.py
```

The app serves an animated FastAPI dashboard on `http://127.0.0.1:8080` with audit-backed intelligence upgrades and a live status feed.

## Screenshot workflow

For browser automation tools, use the dedicated screenshot stage:

1. `POST /snapshot/capture` to generate the latest PNG.
2. Open `GET /snapshot/stage` for a deterministic screenshot page.
3. Capture the viewport in your browser tool.
