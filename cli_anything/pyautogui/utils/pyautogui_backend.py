import importlib
import platform
import sys
from pathlib import Path


def point_to_dict(value):
    if value is None:
        return None
    if hasattr(value, "x") and hasattr(value, "y"):
        return {"x": int(value.x), "y": int(value.y)}
    if isinstance(value, (tuple, list)) and len(value) >= 2:
        return {"x": int(value[0]), "y": int(value[1])}
    return value


def box_to_dict(value):
    if value is None:
        return None
    names = ("left", "top", "width", "height")
    if all(hasattr(value, name) for name in names):
        return {name: int(getattr(value, name)) for name in names}
    if isinstance(value, (tuple, list)) and len(value) >= 4:
        return {name: int(value[index]) for index, name in enumerate(names)}
    return value


class PyAutoGUIBackend:
    """Thin wrapper around the real pyautogui module."""

    def __init__(self, pause=None, failsafe=None):
        self._module = None
        self.pause = pause
        self.failsafe = failsafe

    @property
    def module(self):
        if self._module is None:
            try:
                self._module = importlib.import_module("pyautogui")
            except Exception as exc:
                raise RuntimeError(
                    "Unable to import pyautogui. From the source repo, run "
                    "`pip install -e ..`, or install PyAutoGUI from PyPI."
                ) from exc
            if self.pause is not None:
                self._module.PAUSE = self.pause
            if self.failsafe is not None:
                self._module.FAILSAFE = self.failsafe
        return self._module

    def info(self):
        pg = self.module
        return {
            "backend": "pyautogui",
            "platform": sys.platform,
            "system": platform.system(),
            "python": sys.version.split()[0],
            "pyautogui_version": getattr(pg, "__version__", None),
            "pause": getattr(pg, "PAUSE", None),
            "failsafe": getattr(pg, "FAILSAFE", None),
            "screen_size": self.size(),
            "position": self.position(),
        }

    def position(self):
        return point_to_dict(self.module.position())

    def size(self):
        size = self.module.size()
        return {"width": int(size[0]), "height": int(size[1])}

    def on_screen(self, x, y):
        return bool(self.module.onScreen(x, y))

    def move_to(self, x, y, duration=0.0):
        self.module.moveTo(x, y, duration=duration)
        return self.position()

    def move_rel(self, x, y, duration=0.0):
        self.module.moveRel(x, y, duration=duration)
        return self.position()

    def click(self, x=None, y=None, button="left", clicks=1, interval=0.0, duration=0.0):
        self.module.click(x=x, y=y, button=button, clicks=clicks, interval=interval, duration=duration)
        return self.position()

    def drag_to(self, x, y, button="left", duration=0.0):
        self.module.dragTo(x, y, duration=duration, button=button)
        return self.position()

    def drag_rel(self, x, y, button="left", duration=0.0):
        self.module.dragRel(x, y, duration=duration, button=button)
        return self.position()

    def scroll(self, clicks, x=None, y=None, horizontal=False):
        if horizontal:
            self.module.hscroll(clicks, x=x, y=y)
        else:
            self.module.scroll(clicks, x=x, y=y)
        return self.position()

    def press(self, keys, presses=1, interval=0.0):
        self.module.press(keys, presses=presses, interval=interval)
        return {"keys": keys, "presses": presses}

    def key_down(self, key):
        self.module.keyDown(key)
        return {"key": key}

    def key_up(self, key):
        self.module.keyUp(key)
        return {"key": key}

    def write(self, text, interval=0.0):
        self.module.write(text, interval=interval)
        return {"text": text, "length": len(text)}

    def hotkey(self, keys):
        self.module.hotkey(*keys)
        return {"keys": list(keys)}

    def screenshot(self, output=None, region=None):
        image = self.module.screenshot(output, region=region)
        result = {"output": str(output) if output else None, "region": region}
        if image is not None:
            result["size"] = {"width": image.size[0], "height": image.size[1]}
        return result

    def locate_on_screen(self, image, confidence=None, center=False):
        kwargs = {}
        if confidence is not None:
            kwargs["confidence"] = confidence
        if center:
            return point_to_dict(self.module.locateCenterOnScreen(image, **kwargs))
        return box_to_dict(self.module.locateOnScreen(image, **kwargs))

    def pixel(self, x, y):
        pixel = self.module.pixel(x, y)
        return {"x": x, "y": y, "rgb": list(pixel)}

    def run_command(self, command):
        self.module.run(command)
        return {"command": command}


class MockPyAutoGUIBackend:
    """Deterministic backend for validation and CI without controlling the OS."""

    def __init__(self, pause=None, failsafe=None):
        self.pause = pause
        self.failsafe = True if failsafe is None else failsafe
        self.x = 100
        self.y = 100
        self.width = 1920
        self.height = 1080
        self.events = []

    def _event(self, name, **payload):
        self.events.append({"event": name, **payload})

    def info(self):
        return {
            "backend": "mock",
            "platform": sys.platform,
            "system": platform.system(),
            "python": sys.version.split()[0],
            "pyautogui_version": "mock",
            "pause": self.pause,
            "failsafe": self.failsafe,
            "screen_size": self.size(),
            "position": self.position(),
        }

    def position(self):
        return {"x": self.x, "y": self.y}

    def size(self):
        return {"width": self.width, "height": self.height}

    def on_screen(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def move_to(self, x, y, duration=0.0):
        self.x, self.y = int(x), int(y)
        self._event("move_to", x=self.x, y=self.y, duration=duration)
        return self.position()

    def move_rel(self, x, y, duration=0.0):
        self.x += int(x)
        self.y += int(y)
        self._event("move_rel", x=x, y=y, duration=duration)
        return self.position()

    def click(self, x=None, y=None, button="left", clicks=1, interval=0.0, duration=0.0):
        if x is not None and y is not None:
            self.x, self.y = int(x), int(y)
        self._event("click", x=self.x, y=self.y, button=button, clicks=clicks, interval=interval)
        return self.position()

    def drag_to(self, x, y, button="left", duration=0.0):
        self.x, self.y = int(x), int(y)
        self._event("drag_to", x=self.x, y=self.y, button=button, duration=duration)
        return self.position()

    def drag_rel(self, x, y, button="left", duration=0.0):
        self.x += int(x)
        self.y += int(y)
        self._event("drag_rel", x=x, y=y, button=button, duration=duration)
        return self.position()

    def scroll(self, clicks, x=None, y=None, horizontal=False):
        self._event("scroll", clicks=clicks, x=x, y=y, horizontal=horizontal)
        return self.position()

    def press(self, keys, presses=1, interval=0.0):
        self._event("press", keys=keys, presses=presses, interval=interval)
        return {"keys": keys, "presses": presses}

    def key_down(self, key):
        self._event("key_down", key=key)
        return {"key": key}

    def key_up(self, key):
        self._event("key_up", key=key)
        return {"key": key}

    def write(self, text, interval=0.0):
        self._event("write", text=text, interval=interval)
        return {"text": text, "length": len(text)}

    def hotkey(self, keys):
        self._event("hotkey", keys=list(keys))
        return {"keys": list(keys)}

    def screenshot(self, output=None, region=None):
        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"mock screenshot\n")
        self._event("screenshot", output=str(output) if output else None, region=region)
        return {"output": str(output) if output else None, "region": region, "size": self.size()}

    def locate_on_screen(self, image, confidence=None, center=False):
        self._event("locate_on_screen", image=image, confidence=confidence, center=center)
        if center:
            return {"x": 50, "y": 50}
        return {"left": 25, "top": 25, "width": 50, "height": 50}

    def pixel(self, x, y):
        return {"x": x, "y": y, "rgb": [0, 0, 0]}

    def run_command(self, command):
        self._event("run", command=command)
        return {"command": command}
