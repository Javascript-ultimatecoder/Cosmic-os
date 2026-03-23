import unittest
from pathlib import Path


class ScreenshotEnvironmentDocsTests(unittest.TestCase):
    def test_requirements_file_lists_supported_browser_tools(self) -> None:
        requirements = Path('requirements-screenshot.txt').read_text()
        self.assertIn('playwright', requirements)
        self.assertIn('selenium', requirements)
        self.assertIn('webdriver-manager', requirements)

    def test_readme_documents_codex_environment_values(self) -> None:
        readme = Path('README.md').read_text()
        self.assertIn('STRIPE_SECRET_KEY', readme)
        self.assertIn('BINANCE_API_KEY', readme)
        self.assertIn('OPENAI_API_KEY', readme)
        self.assertIn('PLAYWRIGHT_BROWSERS_PATH=0', readme)
        self.assertIn('playwright install chromium', readme)

    def test_setup_script_bootstraps_virtual_environment(self) -> None:
        script = Path('scripts/setup_screenshot_env.sh').read_text()
        self.assertIn('python -m pip install -r requirements-screenshot.txt', script)
        self.assertIn('python -m playwright install chromium', script)
        self.assertIn('source "$venv_path/bin/activate"', script)
        self.assertIn('PLAYWRIGHT_BROWSERS_PATH', script)


if __name__ == '__main__':
    unittest.main()
