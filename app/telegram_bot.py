import os, json, subprocess, time
from pathlib import Path
from dotenv import load_dotenv
from app.utils.github_pr import pr_flow
from app.pr_bot import handle_text

ROOT = Path(".")
PATCHES = ROOT / "patches"
PY = "/root/aiops-tool/.venv/bin/python"

def sh(cmd: list[str], timeout=70) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return (p.stdout or "") + (p.stderr or "")

def tg_get(token: str, offset: int) -> dict:
    url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=25&limit=20&offset={offset}"
    out = sh(["curl", "-s", "--max-time", "35", url], timeout=40).strip()
    try:
        return json.loads(out)
    except Exception:
        return {"ok": False, "raw": out}

def tg_send(token: str, chat_id: str, text: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    out = sh(["curl", "-s", "--max-time", "20", "-X", "POST",
              "-d", f"chat_id={chat_id}",
              "-d", f"text={text}",
              url], timeout=25).strip()
    try:
        return json.loads(out)
    except Exception:
        return {"ok": False, "raw": out}

def last_wi_dir():
    if not PATCHES.exists():
        return None
    items = sorted([p for p in PATCHES.iterdir() if p.is_dir() and p.name.startswith("WI-")])
    return items[-1] if items else None

def read_file(path: Path, max_chars=3000) -> str:
    if not path or not path.exists():
        return "(파일 없음)"
    s = path.read_text(encoding="utf-8", errors="ignore")
    return s if len(s) <= max_chars else s[:max_chars] + "\n...[TRIM]..."

def run_orchestrator(user_text: str) -> str:
    p = subprocess.run([PY, "-m", "app.orchestrator", user_text], capture_output=True, text=True)
    return ((p.stdout or "") + ("\n"+p.stderr if p.stderr else ""))[-2000:]

def set_dry_run(on: bool):
    conf = ROOT / "MODEL_CONFIG.json"
    d = json.loads(conf.read_text(encoding="utf-8"))
    d.setdefault("runtime", {})["dry_run"] = bool(on)
    conf.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    load_dotenv(override=True)
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    allowed = (os.getenv("TELEGRAM_ALLOWED_USER_ID") or "").strip()
    if not token or not allowed:
        print("ERROR: .env에 TELEGRAM_BOT_TOKEN / TELEGRAM_ALLOWED_USER_ID 필요")
        return

    offset = 0
    while True:
        data = tg_get(token, offset)
        if not data.get("ok"):
            time.sleep(2)
            continue

        for upd in data.get("result", []):
            offset = max(offset, upd.get("update_id", 0) + 1)
            msg = upd.get("message") or {}
            if not msg:
                continue

            chat_id = (msg.get("chat") or {}).get("id")
            user_id = (msg.get("from") or {}).get("id")
            text = (msg.get("text") or "").strip()
            if not chat_id or not text:
                continue

            if str(user_id) != allowed:
                tg_send(token, str(chat_id), "권한 없음.")
                continue

            # === PR 명령 최우선 처리 ===
            # 1) /pr            -> 최신 WI 폴더로 자동 PR
            # 2) /pr A|B        -> A 작업명 + B 커밋메시지로 PR
            if text.strip() == "/pr":
                wi = last_wi_dir()
                if not wi:
                    tg_send(token, str(chat_id), "WI 없음.")
                    continue
                wi_name = wi.name
                # 최신 WI로 PR 생성 (커밋메시지는 고정)
                try:
                    reply = handle_text(f"/pr {wi_name}|auto PR from latest WI")
                    tg_send(token, str(chat_id), reply)
                except Exception as e:
                    tg_send(token, str(chat_id), f"PR 생성 실패: {e}")
                continue

            if text.startswith("/pr"):
                try:
                    reply = handle_text(text)
                    tg_send(token, str(chat_id), reply)
                except Exception as e:
                    tg_send(token, str(chat_id), f"PR 생성 실패: {e}")
                continue


                wi_name = wi.name
                branch = f"feature/{wi_name.lower()}"
                title = f"{wi_name}: patch"
                body = read_file(wi / "FINAL.patch.md", max_chars=100000)

                try:
                    pr_url = pr_flow(branch=branch, base="main", title=title, body=body)
                    tg_send(token, str(chat_id), f"PR 생성 완료: {pr_url}")
                except Exception as e:
                    tg_send(token, str(chat_id), f"PR 생성 실패: {e}")
                continue

            # 일반 작업요청
            tg_send(token, str(chat_id), "작업 시작.")
            _ = run_orchestrator(text)
            wi = last_wi_dir()
            if wi:
                tg_send(token, str(chat_id), f"완료: {wi.name}\n" + read_file(wi/"FINAL.patch.md"))
            else:
                tg_send(token, str(chat_id), "완료했지만 WI 폴더를 못 찾음.")

        time.sleep(1)

if __name__ == "__main__":
    main()
