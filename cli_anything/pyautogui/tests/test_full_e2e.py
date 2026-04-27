import json
import shutil
import subprocess
import sys


def base_cmd():
    exe = shutil.which("cli-anything-pyautogui")
    if exe:
        return [exe]
    return [sys.executable, "-m", "cli_anything.pyautogui"]


def run_cli(args, cwd):
    result = subprocess.run(base_cmd() + args, cwd=cwd, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def test_e2e_status(tmp_path):
    payload = run_cli(["--json", "--mock", "--session-file", str(tmp_path / "s.json"), "status"], cwd=tmp_path)
    assert payload["backend"] == "mock"


def test_e2e_move_writes_session(tmp_path):
    session = tmp_path / "s.json"
    payload = run_cli(["--json", "--mock", "--session-file", str(session), "move", "12", "34"], cwd=tmp_path)
    assert payload["after"] == {"x": 12, "y": 34}
    assert session.exists()


def test_e2e_undo_after_move(tmp_path):
    session = tmp_path / "s.json"
    run_cli(["--json", "--mock", "--session-file", str(session), "move", "12", "34"], cwd=tmp_path)
    payload = run_cli(["--json", "--mock", "--session-file", str(session), "session", "undo"], cwd=tmp_path)
    assert payload["undone"] is True
    assert payload["undo"]["type"] == "move_to"


def test_e2e_mock_screenshot_writes_output(tmp_path):
    output = tmp_path / "shot.txt"
    payload = run_cli(["--json", "--mock", "--session-file", str(tmp_path / "s.json"), "screenshot", str(output)], cwd=tmp_path)
    assert payload["output"] == str(output)
    assert output.exists()
