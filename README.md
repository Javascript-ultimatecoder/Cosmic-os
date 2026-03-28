# Cosmic-os
COSMIC OPERATING SYSTEM - Procedural god engine with particle physics


## Running the dashboard

```bash
python cosmic_dashboard.py
```

The app serves an animated FastAPI dashboard on `http://127.0.0.1:8080` with audit-backed intelligence upgrades and a live status feed.

## Screenshot workflow

The dashboard includes built-in snapshot endpoints that make visual capture workflows possible even without external browser automation:

- `POST /snapshot/capture` generates `/tmp/cosmic_latest_snapshot.png`.
- `GET /snapshot/latest` serves the most recent PNG.

Example:

```bash
curl -X POST http://127.0.0.1:8080/snapshot/capture
curl http://127.0.0.1:8080/snapshot/latest --output cosmic_snapshot.png
```

For agent runs where browser automation tools are unavailable, use this status note:

`browser_container screenshot (not run because browser_container tooling is unavailable in this environment)`

## Responsible automation policy

Cosmic OS does **not** include or support CAPTCHA bypassing tools, scripts, or workflows.

- Do not integrate repositories or packages that attempt to bypass "I'm not a robot" checks.
- Use official APIs, service accounts, allowlisted integrations, or human-completed verification when CAPTCHA is present.
- Use `GET /automation_policy` in the app to programmatically enforce this rule in automation pipelines.
