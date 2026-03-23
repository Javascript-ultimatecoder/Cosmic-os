import tempfile
import unittest
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

    def test_status_includes_runtime_and_pantheon_metadata(self) -> None:
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["tier"], cosmic_dashboard.DEFAULT_TIER)
        self.assertEqual(payload["pantheon"], cosmic_dashboard.RARITY_COUNTS)
        self.assertEqual(payload["total_entities"], cosmic_dashboard.TOTAL_ENTITIES)
        self.assertEqual(payload["version"], cosmic_dashboard.APP_VERSION)
        self.assertEqual(payload["recent_events"], [])

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


if __name__ == "__main__":
    unittest.main()
