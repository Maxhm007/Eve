"""No-network tests of Eve's local-only continuous-evolution turn receiver."""
import importlib.util
import json
from pathlib import Path
from unittest import TestCase, mock


def load():
    path = Path(__file__).resolve().parents[1] / "continuous_evolution.py"
    spec = importlib.util.spec_from_file_location("continuous_eve", path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


m = load()


class TurnTests(TestCase):
    def make_body(self, start, end, state):
        return start + "\n" + m.FENCE + "json\n" + json.dumps(state) + "\n" + m.FENCE + "\n" + end

    def test_no_work_when_genesis_owns_turn(self):
        genesis = self.make_body("<!-- continuous-turn-state -->",
                                 "<!-- /continuous-turn-state -->",
                                 {"version": 1, "sequence": 1,
                                  "owner": "genesis", "status": "ready"})
        with mock.patch.object(m, "api", return_value={"body": genesis}) as api:
            self.assertEqual(m.tick("eve-local"), "no_eve_turn")
            self.assertEqual(api.call_count, 1)
            api.assert_called_once_with(m.GENESIS, "/issues/1212", token="eve-local")

    def test_eve_runs_one_task_and_records_ack_locally(self):
        genesis = self.make_body("<!-- continuous-turn-state -->",
                                 "<!-- /continuous-turn-state -->",
                                 {"version": 1, "sequence": 2,
                                  "owner": "eve", "status": "running"})
        eve = self.make_body(m.START, m.END,
                             {"version": 1, "sequence": 0, "status": "initial"})
        writes = []
        def fake_api(repo, suffix, method="GET", payload=None, token=""):
            if method != "GET":
                self.assertEqual(repo, m.EVE)
                writes.append((suffix, payload))
                return {}
            return {"body": genesis if repo == m.GENESIS else eve}
        worker = mock.Mock(return_value=("completed", "unittest passed"))
        with mock.patch.object(m, "api", side_effect=fake_api):
            self.assertEqual(m.tick("eve-local", work=worker), "completed")
        worker.assert_called_once()
        self.assertEqual(len(writes), 2)
        ack = m.parse_state(writes[0][1]["body"], m.START, m.END)
        self.assertEqual((ack["sequence"], ack["status"]), (2, "completed"))

    def test_eve_can_claim_ready_handoff_without_extra_genesis_heartbeat(self):
        genesis = self.make_body("<!-- continuous-turn-state -->",
                                 "<!-- /continuous-turn-state -->",
                                 {"version": 1, "sequence": 2,
                                  "owner": "eve", "status": "ready"})
        eve = self.make_body(m.START, m.END,
                             {"version": 1, "sequence": 0, "status": "initial"})
        writes = []
        def fake_api(repo, suffix, method="GET", payload=None, token=""):
            if method != "GET":
                writes.append((repo, suffix, payload))
                return {}
            return {"body": genesis if repo == m.GENESIS else eve}
        with mock.patch.object(m, "api", side_effect=fake_api):
            self.assertEqual(m.tick("eve-local",
                                    work=lambda: ("completed", "verified")), "completed")
        self.assertEqual(len(writes), 2)
        self.assertTrue(all(row[0] == m.EVE for row in writes))

    def test_does_not_duplicate_existing_ack(self):
        genesis = self.make_body("<!-- continuous-turn-state -->",
                                 "<!-- /continuous-turn-state -->",
                                 {"version": 1, "sequence": 2,
                                  "owner": "eve", "status": "running"})
        eve = self.make_body(m.START, m.END,
                             {"version": 1, "sequence": 2, "status": "completed"})
        worker = mock.Mock()
        with mock.patch.object(m, "api", side_effect=[
                {"body": genesis}, {"body": eve}]):
            self.assertEqual(m.tick("eve-local", work=worker), "already_acknowledged")
        worker.assert_not_called()

    def test_rejects_cross_repository_write(self):
        with self.assertRaises(ValueError):
            m.api(m.GENESIS, "/issues/1212", method="PATCH",
                  payload={"body": "unsafe"}, token="eve-local")

    def test_invalid_state_markers_fail_closed(self):
        with self.assertRaises(ValueError):
            m.parse_state("untrusted", m.START, m.END)
