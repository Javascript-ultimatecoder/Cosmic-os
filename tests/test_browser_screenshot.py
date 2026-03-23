import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / 'scripts' / 'browser_screenshot.py'
SPEC = importlib.util.spec_from_file_location('browser_screenshot', MODULE_PATH)
browser_screenshot = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(browser_screenshot)


class BrowserScreenshotTests(unittest.TestCase):
    def test_detect_browser_executable_prefers_environment_override(self) -> None:
        with mock.patch.dict(os.environ, {'BROWSER_EXECUTABLE': '/tmp/custom-browser'}, clear=False):
            self.assertEqual(browser_screenshot.detect_browser_executable(), '/tmp/custom-browser')

    def test_detect_browser_executable_checks_common_binaries(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch('shutil.which', side_effect=lambda name: '/usr/bin/chromium' if name == 'chromium' else None):
                self.assertEqual(browser_screenshot.detect_browser_executable(), '/usr/bin/chromium')

    def test_parser_uses_dashboard_defaults(self) -> None:
        parser = browser_screenshot.build_parser()
        args = parser.parse_args([])
        self.assertEqual(args.url, 'http://127.0.0.1:8080/')
        self.assertEqual(args.wait_for, '#pantheon')
        self.assertEqual(args.output, 'screenshots/browser_dashboard.png')


if __name__ == '__main__':
    unittest.main()
