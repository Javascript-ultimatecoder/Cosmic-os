#!/usr/bin/env python3
"""Capture browser screenshots with Playwright."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture a full-page screenshot of a URL with Playwright.")
    parser.add_argument("output", nargs="?", default="screenshots/browser_dashboard.png", help="Output PNG path")
    parser.add_argument("--url", default="http://127.0.0.1:8080/", help="URL to open before taking the screenshot")
    parser.add_argument("--width", type=int, default=1440, help="Viewport width in pixels")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height in pixels")
    parser.add_argument(
        "--wait-for",
        default="#pantheon",
        help="CSS selector to wait for before saving the screenshot",
    )
    parser.add_argument("--timeout-ms", type=int, default=15000, help="Navigation and selector timeout in milliseconds")
    parser.add_argument("--executable-path", default=None, help="Explicit browser executable path to launch")
    return parser


def detect_browser_executable(explicit_path: str | None = None) -> str | None:
    explicit_path = explicit_path or os.environ.get("BROWSER_EXECUTABLE")
    if explicit_path:
        return explicit_path

    for candidate in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - exercised in user environments
        raise SystemExit(
            "Playwright is not installed. Run `pip install -r requirements.txt` and then either "
            "`python -m playwright install chromium` or install a system browser such as `chromium`."
        ) from exc

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    executable_path = detect_browser_executable(args.executable_path)

    try:
        with sync_playwright() as playwright:
            launch_kwargs = {"headless": True}
            if executable_path:
                launch_kwargs["executable_path"] = executable_path
            browser = playwright.chromium.launch(**launch_kwargs)
            page = browser.new_page(viewport={"width": args.width, "height": args.height})
            page.goto(args.url, wait_until="networkidle", timeout=args.timeout_ms)
            if args.wait_for:
                page.wait_for_selector(args.wait_for, timeout=args.timeout_ms)
            page.screenshot(path=str(output_path), full_page=True)
            browser.close()
    except PlaywrightTimeoutError as exc:
        raise SystemExit(f"Timed out while loading {args.url!r} or waiting for {args.wait_for!r}.") from exc
    except Exception as exc:  # pragma: no cover - integration failure path
        if not executable_path:
            raise SystemExit(
                "Unable to launch a browser. Install one with `python -m playwright install chromium` or `apt-get install -y chromium`."
            ) from exc
        raise SystemExit(f"Unable to launch browser executable {executable_path!r}: {exc}") from exc

    browser_name = executable_path or os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or "playwright-managed chromium"
    print(f"Saved browser screenshot to {output_path} using {browser_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
