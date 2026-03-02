import json
from pathlib import Path
from datetime import datetime

STATE_PATH = Path("state/STATE.json")

def load_state() -> dict:
    if not STATE_PATH.exists():
        raise FileNotFoundError(f"STATE not found: {STATE_PATH}")
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def append_history(state: dict, kind: str, payload: dict) -> None:
    item = {"ts": datetime.utcnow().isoformat() + "Z", "kind": kind, "payload": payload}
    state.setdefault("history", []).append(item)
