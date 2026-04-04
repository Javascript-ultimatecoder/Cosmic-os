import tempfile
import unittest
from unittest import mock
from pathlib import Path

from fastapi.testclient import TestClient

import cosmic_dashboard


class CosmicDashboardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_audit = cosmic_dashboard.audit
        self.original_tier = cosmic_dashboard.INTELLIGENCE_TIER
        self.temp_db_path = Path(self.tempdir.name) / "test_audit.db"
        cosmic_dashboard.audit = cosmic_dashboard.AuditLedger(self.temp_db_path)
        cosmic_dashboard.INTELLIGENCE_TIER = cosmic_dashboard.DEFAULT_TIER
        self.client = TestClient(cosmic_dashboard.app)

    def tearDown(self) -> None:
        cosmic_dashboard.audit.conn.close()
        cosmic_dashboard.audit = self.original_audit
        cosmic_dashboard.INTELLIGENCE_TIER = self.original_tier
        self.tempdir.cleanup()

    def test_status_endpoint_has_cors_headers(self) -> None:
        response = self.client.options(
            '/status',
            headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'GET',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('access-control-allow-origin'), 'http://localhost:5173')

    def test_status_includes_runtime_and_pantheon_metadata(self) -> None:
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["tier"], cosmic_dashboard.DEFAULT_TIER)
        self.assertEqual(payload["pantheon"], cosmic_dashboard.RARITY_COUNTS)
        self.assertEqual(payload["total_entities"], cosmic_dashboard.TOTAL_ENTITIES)
        self.assertEqual(payload["version"], cosmic_dashboard.APP_VERSION)
        self.assertEqual(payload["recent_events"], [])

    def test_homepage_includes_rayo_branding(self) -> None:
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ω RAYO'S NUMBER OF GODS", response.text)
        self.assertIn('Infinite scroll + virtualization simulation enabled', response.text)

    def test_screenshot_route_returns_success_when_playwright_is_available(self) -> None:
        class FakePage:
            async def goto(self, url: str, wait_until: str, timeout: int) -> None:
                self.url = url

            async def wait_for_selector(self, selector: str, timeout: int) -> None:
                self.selector = selector

            async def screenshot(self, path: str, full_page: bool) -> None:
                Path(path).write_bytes(b'png')

        class FakeBrowser:
            async def new_page(self, viewport: dict) -> FakePage:
                self.viewport = viewport
                return FakePage()

            async def close(self) -> None:
                return None

        class FakeChromium:
            async def launch(self, headless: bool) -> FakeBrowser:
                self.headless = headless
                return FakeBrowser()

        class FakePlaywright:
            chromium = FakeChromium()

        class FakePlaywrightContext:
            async def __aenter__(self) -> FakePlaywright:
                return FakePlaywright()

            async def __aexit__(self, exc_type, exc, tb) -> None:
                return None

        output_path = Path(self.tempdir.name) / 'pantheon.png'
        with mock.patch.object(cosmic_dashboard, 'async_playwright', return_value=FakePlaywrightContext()):
            response = self.client.get('/screenshot', params={'output': str(output_path)})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['status'], 'success')
        self.assertEqual(payload['path'], str(output_path))
        self.assertTrue(output_path.exists())

    def test_screenshot_route_reports_missing_playwright(self) -> None:
        with mock.patch.object(cosmic_dashboard, 'async_playwright', None):
            response = self.client.get('/screenshot')

        self.assertEqual(response.status_code, 503)
        self.assertIn('Playwright is not installed', response.json()['detail'])

    def test_upgrade_records_event_and_updates_tier(self) -> None:
        response = self.client.post(
            "/upgrade_intelligence",
            json={"god": "LegendaryGod-7", "tier": cosmic_dashboard.MAX_TIER},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["tier"], cosmic_dashboard.MAX_TIER)
        self.assertTrue(payload["event_id"])

        status_payload = self.client.get("/status").json()
        self.assertEqual(status_payload["tier"], cosmic_dashboard.MAX_TIER)
        self.assertEqual(status_payload["audit_events"], 1)
        self.assertEqual(status_payload["recent_events"][0]["payload"]["god"], "LegendaryGod-7")

    def test_upgrade_rejects_invalid_tier(self) -> None:
        response = self.client.post("/upgrade_intelligence", json={"god": "CommonGod-1", "tier": 99})
        self.assertEqual(response.status_code, 400)
        self.assertIn("tier must be between", response.json()["detail"])

    def test_performance_evolution_records_audit_event(self) -> None:
        response = self.client.post('/evolve_performance', json={'god': 'RareGod-3'})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertIn('PERFORMANCE', payload['result'])

        status_payload = self.client.get('/status').json()
        self.assertEqual(status_payload['audit_events'], 1)
        self.assertEqual(status_payload['recent_events'][0]['type'], 'performance_evolution')
        self.assertEqual(status_payload['recent_events'][0]['payload']['god'], 'RareGod-3')

    def test_mating_evolution_creates_child_event(self) -> None:
        response = self.client.post('/mate_gods', json={'god1': 'DivineGod-2', 'god2': 'MythicalGod-4'})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['child'], 'ChildOf_DivineGod-2_MythicalGod-4')

        status_payload = self.client.get('/status').json()
        self.assertEqual(status_payload['audit_events'], 1)
        self.assertEqual(status_payload['recent_events'][0]['type'], 'mating_evolution')
        self.assertEqual(
            status_payload['recent_events'][0]['payload']['child'],
            'ChildOf_DivineGod-2_MythicalGod-4',
        )

    def test_updates_endpoint_and_broadcast_feed(self) -> None:
        response = self.client.get('/updates')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['version'], cosmic_dashboard.APP_VERSION)
        self.assertTrue(payload['updates'])

        broadcast_response = self.client.post(
            '/broadcast_update',
            json={'title': 'Omega patch', 'detail': 'Constantly add updates to the code'},
        )
        self.assertEqual(broadcast_response.status_code, 200)
        status_payload = self.client.get('/status').json()
        self.assertEqual(status_payload['audit_events'], 1)
        self.assertEqual(status_payload['recent_events'][0]['type'], 'broadcast_update')
        self.assertEqual(status_payload['recent_events'][0]['payload']['title'], 'Omega patch')
        self.assertEqual(status_payload['live_updates'][0]['code'], 'broadcast_update')

    def test_broadcast_requires_title_and_detail(self) -> None:
        response = self.client.post('/broadcast_update', json={'title': '', 'detail': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('required', response.json()['detail'])


if __name__ == "__main__":
    unittest.main()
