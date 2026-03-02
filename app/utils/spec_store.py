from pathlib import Path

SPEC_PATH = Path("spec/SPEC.md")
AGENTS_PATH = Path("spec/AGENTS.md")
ROUTING_PATH = Path("spec/ROUTING_RULES.md")

def read_texts() -> dict:
    return {
        "spec": SPEC_PATH.read_text(encoding="utf-8"),
        "agents": AGENTS_PATH.read_text(encoding="utf-8"),
        "routing": ROUTING_PATH.read_text(encoding="utf-8"),
    }
