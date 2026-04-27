import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class SessionStore:
    """Small JSON-backed action history with undo and redo stacks."""

    def __init__(self, path):
        self.path = Path(path)
        self.data = self._load()

    def _empty(self):
        now = utc_now()
        return {
            "session_id": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "history": [],
            "redo": [],
            "settings": {
                "pause": None,
                "failsafe": None,
            },
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return self._empty()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data["updated_at"] = utc_now()
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp_path, self.path)

    def status(self):
        return {
            "session_file": str(self.path),
            "session_id": self.data["session_id"],
            "history_count": len(self.data["history"]),
            "redo_count": len(self.data["redo"]),
            "settings": self.data.get("settings", {}),
            "updated_at": self.data["updated_at"],
        }

    def record(self, entry, dry_run=False):
        if dry_run:
            return
        item = dict(entry)
        item.setdefault("id", str(uuid.uuid4()))
        item.setdefault("timestamp", utc_now())
        self.data["history"].append(item)
        self.data["history"] = self.data["history"][-200:]
        self.data["redo"] = []
        self.save()

    def history(self, limit=20):
        return self.data["history"][-limit:]

    def clear(self):
        self.data["history"] = []
        self.data["redo"] = []
        self.save()

    def pop_undo(self):
        while self.data["history"]:
            entry = self.data["history"].pop()
            if entry.get("undo"):
                self.data["redo"].append(entry)
                self.save()
                return entry
        self.save()
        return None

    def pop_redo(self):
        if not self.data["redo"]:
            return None
        entry = self.data["redo"].pop()
        self.data["history"].append(entry)
        self.save()
        return entry
