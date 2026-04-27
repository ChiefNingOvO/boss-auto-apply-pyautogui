import json

from click.testing import CliRunner

from cli_anything.pyautogui.core.session import SessionStore
from cli_anything.pyautogui.pyautogui_cli import cli
from cli_anything.pyautogui.utils.pyautogui_backend import MockPyAutoGUIBackend


def test_session_create_save_reload(tmp_path):
    path = tmp_path / "session.json"
    store = SessionStore(path)
    store.save()
    reloaded = SessionStore(path)
    assert reloaded.status()["session_id"] == store.status()["session_id"]


def test_session_record_history(tmp_path):
    store = SessionStore(tmp_path / "session.json")
    store.record({"action": {"type": "click"}})
    assert store.history()[0]["action"]["type"] == "click"


def test_session_undo_redo(tmp_path):
    store = SessionStore(tmp_path / "session.json")
    store.record({"action": {"type": "move_to", "x": 2, "y": 3}, "undo": {"type": "move_to", "x": 0, "y": 0}})
    entry = store.pop_undo()
    assert entry["undo"]["x"] == 0
    assert store.pop_redo()["action"]["x"] == 2


def test_mock_backend_move():
    backend = MockPyAutoGUIBackend()
    assert backend.move_to(10, 20) == {"x": 10, "y": 20}
    assert backend.move_rel(5, -5) == {"x": 15, "y": 15}


def test_cli_json_status(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "--mock", "--session-file", str(tmp_path / "s.json"), "status"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["backend"] == "mock"
    assert payload["screen_size"]["width"] == 1920


def test_cli_dry_run_move(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "--mock", "--dry-run", "--session-file", str(tmp_path / "s.json"), "move", "1", "2"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["after"]["dry_run"] is True
    assert payload["action"]["type"] == "move_to"
