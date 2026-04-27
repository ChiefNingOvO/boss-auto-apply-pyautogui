# Test Plan

## Inventory

- `test_core.py`: 6 unit tests planned
  - session create/save/reload
  - session record/history
  - session undo/redo stacks
  - mock backend movement
  - CLI JSON status
  - CLI dry-run action preview
- `test_full_e2e.py`: 4 subprocess tests planned
  - installed/module command status
  - mock move writes session
  - session undo after move
  - screenshot mock writes output file

## Validation Strategy

Tests use the `--mock` backend so they do not move the user's mouse, type into the active window, or read the real screen. E2E tests prefer the installed `cli-anything-pyautogui` console script and fall back to `python -m cli_anything.pyautogui`.

## Manual Real-Backend Smoke Tests

Only run these when it is safe for the mouse and keyboard to be controlled:

```bash
cli-anything-pyautogui --json status
cli-anything-pyautogui --json --dry-run move 10 10
cli-anything-pyautogui --json position
```
