# PyAutoGUI CLI Harness Architecture

## Target

- Source repository: this GitHub repository
- Upstream: `https://github.com/asweigart/pyautogui.git`
- Backend engine: the Python `pyautogui` package
- Harness path: `cli_anything/pyautogui`

## Backend Mapping

PyAutoGUI is already a backend library rather than a GUI application. The harness maps CLI commands directly to the stable public API:

- Mouse:
  - `move` -> `pyautogui.moveTo` / `pyautogui.moveRel`
  - `click` -> `pyautogui.click`
  - `drag` -> `pyautogui.dragTo` / `pyautogui.dragRel`
  - `scroll` -> `pyautogui.scroll` / `pyautogui.hscroll`
- Keyboard:
  - `key press` -> `pyautogui.press`
  - `key down` -> `pyautogui.keyDown`
  - `key up` -> `pyautogui.keyUp`
  - `write` -> `pyautogui.write`
  - `hotkey` -> `pyautogui.hotkey`
- Screen:
  - `screenshot` -> `pyautogui.screenshot`
  - `locate` -> `pyautogui.locateOnScreen` / `pyautogui.locateCenterOnScreen`
  - `pixel` -> `pyautogui.pixel`
- Automation language:
  - `run` -> `pyautogui.run`

## State Model

The CLI writes session data to `.pyautogui-cli-session.json` by default. The session contains:

- action history
- redo stack
- action results
- undo metadata where possible

Only pointer movement and drag commands are safely undoable by returning the mouse to the previous position. Keyboard input, clicks, screenshots, and screen reads are recorded but not treated as reversible operations.

## Safety Model

The harness supports:

- `--mock`: deterministic fake backend for tests and CI
- `--dry-run`: preview a command without touching the desktop
- `--failsafe/--no-failsafe`: explicit PyAutoGUI fail-safe override
- `--pause`: per-command pause override

Real PyAutoGUI commands interact with the active desktop and focused window. Agents should inspect with `status`, `position`, `size`, and use `--dry-run` before executing destructive UI automation.

## Packaging

The harness follows the CLI-Anything namespace layout inside this repository:

```text
boss-auto-apply-pyautogui/
  pyproject.toml
  cli_anything/
    pyautogui/
      __main__.py
      pyautogui_cli.py
      core/
      utils/
      tests/
```

`pyproject.toml` exposes the console script `cli-anything-pyautogui`.

## Known Limitations

- Undo is limited to pointer repositioning.
- The real backend requires a graphical desktop session.
- Multi-monitor behavior inherits PyAutoGUI's upstream primary-monitor limitation.
- Screenshot and locate commands depend on PyAutoGUI/PyScreeze/Pillow platform support.
