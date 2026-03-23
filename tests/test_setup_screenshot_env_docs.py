import unittest
from pathlib import Path


class ScreenshotEnvironmentDocsTests(unittest.TestCase):
    def test_requirements_file_lists_supported_browser_tools(self) -> None:
        requirements = Path('requirements-screenshot.txt').read_text()
        self.assertIn('playwright', requirements)
        self.assertIn('selenium', requirements)
        self.assertIn('webdriver-manager', requirements)

    def test_setup_script_bootstraps_virtual_environment(self) -> None:
        script = Path('scripts/setup_screenshot_env.sh').read_text()
        self.assertIn('python -m pip install -r requirements-screenshot.txt', script)
        self.assertIn('python -m playwright install chromium', script)
        self.assertIn('source "$venv_path/bin/activate"', script)


if __name__ == '__main__':
    unittest.main()
