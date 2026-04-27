import json
import shlex
from dataclasses import dataclass
from pathlib import Path

import click

from .core.session import SessionStore
from .utils.pyautogui_backend import MockPyAutoGUIBackend, PyAutoGUIBackend


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@dataclass
class Runtime:
    backend: object
    session: SessionStore
    json_output: bool
    dry_run: bool
    mock: bool


def make_backend(mock=False, pause=None, failsafe=None):
    cls = MockPyAutoGUIBackend if mock else PyAutoGUIBackend
    return cls(pause=pause, failsafe=failsafe)


def emit(ctx, payload, message=None):
    if ctx.obj.json_output:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        click.echo(message if message is not None else humanize(payload))
    return payload


def humanize(payload):
    if isinstance(payload, dict):
        return "\n".join(f"{key}: {value}" for key, value in payload.items())
    return str(payload)


def parse_region(values):
    if not values:
        return None
    if len(values) != 4:
        raise click.BadParameter("region requires LEFT TOP WIDTH HEIGHT")
    return tuple(int(value) for value in values)


def action_result(runtime, action):
    if runtime.dry_run:
        return {"dry_run": True, "action": action}
    backend = runtime.backend
    kind = action["type"]
    if kind == "move_to":
        return backend.move_to(action["x"], action["y"], duration=action.get("duration", 0.0))
    if kind == "move_rel":
        return backend.move_rel(action["x"], action["y"], duration=action.get("duration", 0.0))
    if kind == "click":
        return backend.click(
            x=action.get("x"),
            y=action.get("y"),
            button=action.get("button", "left"),
            clicks=action.get("clicks", 1),
            interval=action.get("interval", 0.0),
            duration=action.get("duration", 0.0),
        )
    if kind == "drag_to":
        return backend.drag_to(action["x"], action["y"], button=action.get("button", "left"), duration=action.get("duration", 0.0))
    if kind == "drag_rel":
        return backend.drag_rel(action["x"], action["y"], button=action.get("button", "left"), duration=action.get("duration", 0.0))
    if kind == "scroll":
        return backend.scroll(action["clicks"], x=action.get("x"), y=action.get("y"), horizontal=action.get("horizontal", False))
    if kind == "press":
        return backend.press(action["keys"], presses=action.get("presses", 1), interval=action.get("interval", 0.0))
    if kind == "key_down":
        return backend.key_down(action["key"])
    if kind == "key_up":
        return backend.key_up(action["key"])
    if kind == "write":
        return backend.write(action["text"], interval=action.get("interval", 0.0))
    if kind == "hotkey":
        return backend.hotkey(action["keys"])
    if kind == "run":
        return backend.run_command(action["command"])
    raise click.ClickException(f"Unsupported action type: {kind}")


def recordable_action(runtime, action, undo=None):
    result = action_result(runtime, action)
    runtime.session.record({"action": action, "undo": undo, "result": result}, dry_run=runtime.dry_run)
    return result


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--session-file", type=click.Path(dir_okay=False, path_type=Path), default=Path(".pyautogui-cli-session.json"), show_default=True)
@click.option("--dry-run", is_flag=True, help="Preview actions without touching mouse, keyboard, or screen.")
@click.option("--mock", is_flag=True, help="Use deterministic fake backend for validation and CI.")
@click.option("--pause", type=float, default=None, help="Override pyautogui.PAUSE for this command.")
@click.option("--failsafe/--no-failsafe", default=None, help="Override pyautogui.FAILSAFE for this command.")
@click.pass_context
def cli(ctx, json_output, session_file, dry_run, mock, pause, failsafe):
    """Agent-native CLI harness for PyAutoGUI."""
    ctx.obj = Runtime(
        backend=make_backend(mock=mock, pause=pause, failsafe=failsafe),
        session=SessionStore(session_file),
        json_output=json_output,
        dry_run=dry_run,
        mock=mock,
    )
    if ctx.invoked_subcommand is None:
        repl_loop(ctx)


@cli.command()
@click.pass_context
def status(ctx):
    """Inspect backend, screen, pointer, and session state."""
    runtime = ctx.obj
    payload = runtime.backend.info()
    payload["session"] = runtime.session.status()
    payload["dry_run"] = runtime.dry_run
    emit(ctx, payload)


@cli.command()
@click.pass_context
def position(ctx):
    """Return the current mouse position."""
    emit(ctx, ctx.obj.backend.position())


@cli.command("size")
@click.pass_context
def screen_size(ctx):
    """Return primary screen size."""
    emit(ctx, ctx.obj.backend.size())


@cli.command("on-screen")
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.pass_context
def on_screen(ctx, x, y):
    """Check whether a coordinate is on the primary screen."""
    emit(ctx, {"x": x, "y": y, "on_screen": ctx.obj.backend.on_screen(x, y)})


@cli.command()
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.option("--relative", is_flag=True, help="Move relative to current position.")
@click.option("--duration", type=float, default=0.0, show_default=True)
@click.pass_context
def move(ctx, x, y, relative, duration):
    """Move the mouse pointer."""
    runtime = ctx.obj
    before = runtime.backend.position()
    action = {"type": "move_rel" if relative else "move_to", "x": x, "y": y, "duration": duration}
    undo = {"type": "move_to", "x": before["x"], "y": before["y"], "duration": 0.0}
    result = recordable_action(runtime, action, undo=undo)
    emit(ctx, {"before": before, "after": result, "action": action})


@cli.command("click")
@click.argument("x", type=int, required=False)
@click.argument("y", type=int, required=False)
@click.option("--button", type=click.Choice(["left", "right", "middle"]), default="left", show_default=True)
@click.option("--clicks", type=int, default=1, show_default=True)
@click.option("--interval", type=float, default=0.0, show_default=True)
@click.option("--duration", type=float, default=0.0, show_default=True)
@click.pass_context
def mouse_click(ctx, x, y, button, clicks, interval, duration):
    """Click at an optional coordinate."""
    action = {"type": "click", "x": x, "y": y, "button": button, "clicks": clicks, "interval": interval, "duration": duration}
    result = recordable_action(ctx.obj, action)
    emit(ctx, {"after": result, "action": action})


@cli.command()
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.option("--relative", is_flag=True, help="Drag relative to current position.")
@click.option("--button", type=click.Choice(["left", "right", "middle"]), default="left", show_default=True)
@click.option("--duration", type=float, default=0.0, show_default=True)
@click.pass_context
def drag(ctx, x, y, relative, button, duration):
    """Drag the mouse pointer."""
    runtime = ctx.obj
    before = runtime.backend.position()
    action = {"type": "drag_rel" if relative else "drag_to", "x": x, "y": y, "button": button, "duration": duration}
    undo = {"type": "move_to", "x": before["x"], "y": before["y"], "duration": 0.0}
    result = recordable_action(runtime, action, undo=undo)
    emit(ctx, {"before": before, "after": result, "action": action})


@cli.command()
@click.argument("clicks", type=int)
@click.option("--x", type=int, default=None)
@click.option("--y", type=int, default=None)
@click.option("--horizontal", is_flag=True, help="Use horizontal scroll.")
@click.pass_context
def scroll(ctx, clicks, x, y, horizontal):
    """Scroll vertically or horizontally."""
    action = {"type": "scroll", "clicks": clicks, "x": x, "y": y, "horizontal": horizontal}
    result = recordable_action(ctx.obj, action)
    emit(ctx, {"after": result, "action": action})


@cli.group()
def key():
    """Keyboard actions."""


@key.command("press")
@click.argument("keys", nargs=-1, required=True)
@click.option("--presses", type=int, default=1, show_default=True)
@click.option("--interval", type=float, default=0.0, show_default=True)
@click.pass_context
def key_press(ctx, keys, presses, interval):
    """Press one or more keys."""
    value = list(keys) if len(keys) > 1 else keys[0]
    action = {"type": "press", "keys": value, "presses": presses, "interval": interval}
    result = recordable_action(ctx.obj, action)
    emit(ctx, {"result": result, "action": action})


@key.command("down")
@click.argument("key_name")
@click.pass_context
def key_down(ctx, key_name):
    """Hold a key down."""
    action = {"type": "key_down", "key": key_name}
    emit(ctx, {"result": recordable_action(ctx.obj, action), "action": action})


@key.command("up")
@click.argument("key_name")
@click.pass_context
def key_up(ctx, key_name):
    """Release a key."""
    action = {"type": "key_up", "key": key_name}
    emit(ctx, {"result": recordable_action(ctx.obj, action), "action": action})


@cli.command("write")
@click.argument("text")
@click.option("--interval", type=float, default=0.0, show_default=True)
@click.pass_context
def write_text(ctx, text, interval):
    """Type text into the currently focused window."""
    action = {"type": "write", "text": text, "interval": interval}
    emit(ctx, {"result": recordable_action(ctx.obj, action), "action": action})


@cli.command()
@click.argument("keys", nargs=-1, required=True)
@click.pass_context
def hotkey(ctx, keys):
    """Press a key chord such as ctrl c."""
    action = {"type": "hotkey", "keys": list(keys)}
    emit(ctx, {"result": recordable_action(ctx.obj, action), "action": action})


@cli.command()
@click.argument("output", required=False, type=click.Path(dir_okay=False, path_type=Path))
@click.option("--region", nargs=4, type=int, help="LEFT TOP WIDTH HEIGHT")
@click.pass_context
def screenshot(ctx, output, region):
    """Capture a screenshot, optionally to a file."""
    runtime = ctx.obj
    if runtime.dry_run:
        result = {"dry_run": True, "output": str(output) if output else None, "region": region}
    else:
        result = runtime.backend.screenshot(output=str(output) if output else None, region=tuple(region) if region else None)
    runtime.session.record({"action": {"type": "screenshot", "output": str(output) if output else None, "region": region}, "result": result}, dry_run=runtime.dry_run)
    emit(ctx, result)


@cli.command("locate")
@click.argument("image", type=click.Path(exists=False))
@click.option("--confidence", type=float, default=None)
@click.option("--center", is_flag=True)
@click.pass_context
def locate(ctx, image, confidence, center):
    """Locate an image on screen."""
    if ctx.obj.dry_run:
        result = {"dry_run": True, "image": image, "center": center, "confidence": confidence}
    else:
        result = ctx.obj.backend.locate_on_screen(image, confidence=confidence, center=center)
    emit(ctx, {"match": result})


@cli.command()
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.pass_context
def pixel(ctx, x, y):
    """Read a pixel color at a coordinate."""
    result = {"dry_run": True, "x": x, "y": y} if ctx.obj.dry_run else ctx.obj.backend.pixel(x, y)
    emit(ctx, result)


@cli.command("run")
@click.argument("command")
@click.pass_context
def run_command(ctx, command):
    """Run PyAutoGUI's compact command-string language."""
    action = {"type": "run", "command": command}
    emit(ctx, {"result": recordable_action(ctx.obj, action), "action": action})


@cli.group("session")
def session_group():
    """Inspect or mutate the CLI session."""


@session_group.command("status")
@click.pass_context
def session_status(ctx):
    emit(ctx, ctx.obj.session.status())


@session_group.command("history")
@click.option("--limit", type=int, default=20, show_default=True)
@click.pass_context
def session_history(ctx, limit):
    emit(ctx, {"history": ctx.obj.session.history(limit=limit)})


@session_group.command("clear")
@click.pass_context
def session_clear(ctx):
    ctx.obj.session.clear()
    emit(ctx, {"cleared": True})


@session_group.command("undo")
@click.pass_context
def session_undo(ctx):
    runtime = ctx.obj
    entry = runtime.session.pop_undo()
    if entry is None:
        emit(ctx, {"undone": False, "reason": "No undoable action in history."})
        return
    result = action_result(runtime, entry["undo"])
    emit(ctx, {"undone": True, "undo": entry["undo"], "result": result})


@session_group.command("redo")
@click.pass_context
def session_redo(ctx):
    runtime = ctx.obj
    entry = runtime.session.pop_redo()
    if entry is None:
        emit(ctx, {"redone": False, "reason": "No redo action in session."})
        return
    result = action_result(runtime, entry["action"])
    emit(ctx, {"redone": True, "action": entry["action"], "result": result})


def repl_loop(ctx):
    runtime = ctx.obj
    click.echo("cli-anything-pyautogui REPL. Type 'help' or 'exit'.")
    while True:
        try:
            line = input("pyautogui> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo()
            return
        if not line:
            continue
        if line in {"exit", "quit"}:
            return
        if line == "help":
            click.echo("Commands: status, position, move X Y, click [X Y], write TEXT, press KEY, hotkey K..., undo, redo, exit")
            continue
        try:
            parts = shlex.split(line)
            handle_repl_command(runtime, parts)
        except Exception as exc:
            click.echo(f"error: {exc}")


def handle_repl_command(runtime, parts):
    command = parts[0]
    if command == "status":
        click.echo(json.dumps(runtime.backend.info(), indent=2, sort_keys=True))
    elif command == "position":
        click.echo(json.dumps(runtime.backend.position(), indent=2, sort_keys=True))
    elif command == "move" and len(parts) == 3:
        result = recordable_action(runtime, {"type": "move_to", "x": int(parts[1]), "y": int(parts[2])})
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    elif command == "click":
        x = int(parts[1]) if len(parts) >= 3 else None
        y = int(parts[2]) if len(parts) >= 3 else None
        result = recordable_action(runtime, {"type": "click", "x": x, "y": y, "button": "left", "clicks": 1})
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    elif command == "write" and len(parts) >= 2:
        result = recordable_action(runtime, {"type": "write", "text": " ".join(parts[1:])})
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    elif command == "press" and len(parts) == 2:
        result = recordable_action(runtime, {"type": "press", "keys": parts[1]})
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    elif command == "hotkey" and len(parts) >= 2:
        result = recordable_action(runtime, {"type": "hotkey", "keys": parts[1:]})
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    elif command == "undo":
        entry = runtime.session.pop_undo()
        click.echo("nothing to undo" if entry is None else json.dumps(action_result(runtime, entry["undo"]), indent=2, sort_keys=True))
    elif command == "redo":
        entry = runtime.session.pop_redo()
        click.echo("nothing to redo" if entry is None else json.dumps(action_result(runtime, entry["action"]), indent=2, sort_keys=True))
    else:
        click.echo(f"unknown command: {' '.join(parts)}")
