import os, re, shlex, subprocess, datetime
REPO_DIR = os.environ.get("AIOPS_REPO_DIR", os.path.expanduser("~/aiops-tool"))
BASE_BRANCH = os.environ.get("AIOPS_BASE_BRANCH", "main")

def run(cmd: str, cwd: str = REPO_DIR) -> str:
    p = subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stdout.strip())
    return p.stdout.strip()

def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9._-]+", "-", s.strip().lower())
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "work"

def create_pr(task: str, msg: str) -> str:
    task_slug = slugify(task)
    branch = f"feature/{task_slug}"
    run(f"git checkout {shlex.quote(BASE_BRANCH)}")
    run("git pull --rebase")
    run(f"git checkout -B {shlex.quote(branch)}")

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join(REPO_DIR, f"patches/{task_slug}/PR_BOOTSTRAP.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{ts} {task}\n")

    run(f"git add {shlex.quote(path)}")
    run(f"git commit -m {shlex.quote(msg)}")
    run(f"git push -u origin {shlex.quote(branch)}")
    return run(f'gh pr create --base {shlex.quote(BASE_BRANCH)} --head {shlex.quote(branch)} --title {shlex.quote(task)} --body {shlex.quote("Auto PR via Telegram")}')
def handle_text(text: str) -> str:
    m = re.match(r"^\s*/pr\s+(.+?)\s*\|\s*(.+?)\s*$", text, flags=re.S)
    if not m:
        return "사용법: /pr 작업명|커밋메시지"
    return "PR 생성 완료:\n" + create_pr(m.group(1).strip(), m.group(2).strip())
if __name__ == "__main__":
    import sys
    print(handle_text(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""))
