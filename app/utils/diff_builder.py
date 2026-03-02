from pathlib import Path

def write_wi_file(wi_dir: Path, name: str, content: str) -> Path:
    wi_dir.mkdir(parents=True, exist_ok=True)
    p = wi_dir / name
    p.write_text(content, encoding="utf-8")
    return p
