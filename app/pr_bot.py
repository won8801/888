import os, re, shlex, subprocess, datetime

REPO_DIR = os.environ.get("AIOPS_REPO_DIR", os.path.expanduser("~/aiops-tool"))
BASE_BRANCH = os.environ.get("AIOPS_BASE_BRANCH", "main")

def run(cmd: str, cwd: str = REPO_DIR, ok=(0,)) -> str:
    p = subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode not in ok:
        raise RuntimeError(p.stdout.strip())
    return (p.stdout or "").strip()

def is_dirty() -> bool:
    return bool(run("git status --porcelain"))

def auto_stash_push() -> bool:
    if not is_dirty():
        return False
    run('git stash push -u -m "auto-stash for pr_bot"')
    return True

def auto_stash_pop():
    run("git stash pop", ok=(0,1))

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "work"

def create_pr(task: str, msg: str) -> str:
    task_slug = slugify(task)
    branch = f"feature/{task_slug}"

    stashed = auto_stash_push()
    try:
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

        title = task.strip()
        body = f"Auto PR via Telegram\n\nTask: {task}\nBranch: {branch}\n"
        out = run(
            f'gh pr create --base {shlex.quote(BASE_BRANCH)} --head {shlex.quote(branch)} '
            f'--title {shlex.quote(title)} --body {shlex.quote(body)}'
        )
        return out
    finally:
        if stashed:
            auto_stash_pop()

def handle_text(text: str) -> str:
    m = re.match(r"^\s*/pr\s+(.+?)\s*\|\s*(.+?)\s*$", text, flags=re.S)
    if not m:
        return "사용법: /pr 작업명|커밋메시지\n예) /pr WI-0025|telegram pr test"
    task, msg = m.group(1).strip(), m.group(2).strip()
    url = create_pr(task, msg)
    return f"PR 생성 완료:\n{url}"

if __name__ == "__main__":
    import sys
    print(handle_text(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""))
