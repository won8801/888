import os, json, subprocess
from dotenv import load_dotenv

def sh(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError((p.stdout or "") + "\n" + (p.stderr or ""))
    return (p.stdout or "").strip()

def git_set_remote(owner: str, repo: str, token: str):
    url = f"https://{token}@github.com/{owner}/{repo}.git"
    try:
        sh(["git", "remote", "add", "origin", url])
    except Exception:
        sh(["git", "remote", "set-url", "origin", url])

def git_checkout_new_branch(branch: str):
    sh(["git", "checkout", "-B", branch])

def git_add_commit(msg: str):
    sh(["git", "add", "-A"])
    # 커밋할 게 없으면 에러나니 무시 처리
    p = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
    if p.returncode != 0 and "nothing to commit" not in (p.stdout+p.stderr).lower():
        raise RuntimeError((p.stdout or "") + "\n" + (p.stderr or ""))

def git_push(branch: str):
    sh(["git", "push", "-u", "origin", branch, "--force"])

def create_pr(owner: str, repo: str, token: str, head: str, base: str, title: str, body: str) -> str:
    import urllib.request, urllib.error
    api = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    payload = json.dumps({"title": title, "head": head, "base": base, "body": body}).encode("utf-8")

    req = urllib.request.Request(api, data=payload, method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data.get("html_url", "")
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub PR create failed: {e.code}\n{msg}")

def pr_flow(branch: str, base: str, title: str, body: str) -> str:
    load_dotenv(override=True)
    owner = os.getenv("GITHUB_OWNER","").strip()
    repo  = os.getenv("GITHUB_REPO","").strip()
    token = os.getenv("GITHUB_TOKEN","").strip()
    if not owner or not repo or not token or token.startswith("PUT_"):
        raise RuntimeError("Missing GITHUB_OWNER/GITHUB_REPO/GITHUB_TOKEN in .env")

    git_set_remote(owner, repo, token)
    git_checkout_new_branch(branch)
    git_add_commit(title)
    git_push(branch)

    pr_url = create_pr(owner, repo, token, head=branch, base=base, title=title, body=body)
    return pr_url
