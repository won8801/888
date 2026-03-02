import os
import json
import re
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from app.utils.state_store import load_state, save_state, append_history
from app.utils.spec_store import read_texts
from app.utils.diff_builder import write_wi_file

ROOT = Path(".")
PATCHES = ROOT / "patches"
MODEL_CONF = ROOT / "MODEL_CONFIG.json"

def next_wi_id(state: dict) -> str:
    state["wi_seq"] = int(state.get("wi_seq", 0)) + 1
    return f"WI-{state['wi_seq']:04d}"

def route_agents(user_text: str) -> dict:
    t = user_text.lower()
    front_kw = ["버튼","클릭","화면","페이지","레이아웃","css","ui","프론트","js","이벤트","모달"]
    back_kw  = ["api","db","쿼리","sql","로그","에러","서버","톰캣","응답","세션","인증","nginx","apache"]
    front = any(k in t for k in front_kw)
    back  = any(k in t for k in back_kw)
    if not front and not back:
        front = True
        back = True
    return {"qa": True, "front": front, "back": back}

def safe_trim(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "\n...[TRIM]..."

def load_model_config() -> dict:
    if not MODEL_CONF.exists():
        return {"models": {}, "runtime": {"dry_run": True, "max_context_chars": 12000}}
    return json.loads(MODEL_CONF.read_text(encoding="utf-8"))

def call_openai(model: str, system: str, user: str) -> str:
    client = OpenAI()
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
    )
    return getattr(resp, "output_text", str(resp))

def mask_secrets(text: str) -> str:
    text = re.sub(r'(OPENAI_API_KEY\\s*=\\s*["\\\']).+?(["\\\'])', r'\\1***\\2', text, flags=re.I)
    text = re.sub(r'(token\\s*[:=]\\s*["\\\']).+?(["\\\'])', r'\\1***\\2', text, flags=re.I)
    return text

def main():
    load_dotenv()
    state = load_state()
    texts = read_texts()
    conf = load_model_config()

    models = conf.get("models", {})
    runtime = conf.get("runtime", {})
    dry_run = bool(runtime.get("dry_run", True))
    max_chars = int(runtime.get("max_context_chars", 12000))

    manager_model = os.getenv("OPENAI_MODEL_MANAGER", models.get("manager", "gpt-5.2"))
    worker_front  = models.get("front", "gpt-5.2-mini")
    worker_back   = models.get("back",  "gpt-5.2-mini")
    qa_model      = os.getenv("OPENAI_MODEL_QA", models.get("qa", "gpt-5.2-nano"))

    user_text = " ".join(os.sys.argv[1:]).strip() if len(os.sys.argv) >= 2 else input("요청을 입력: ").strip()
    if not user_text:
        print("요청이 비어있음. 종료.")
        return

    wi = next_wi_id(state)
    wi_dir = PATCHES / wi
    route = route_agents(user_text)

    item = {"id": wi, "status": "DOING", "created_at": datetime.utcnow().isoformat() + "Z", "request": user_text}
    state.setdefault("open_items", []).append(item)
    append_history(state, "wi_created", item)

    shared = f"""
[SPEC]
{texts['spec']}

[AGENTS]
{texts['agents']}

[ROUTING]
{texts['routing']}

[STATE]
{safe_trim(json.dumps(state, ensure_ascii=False, indent=2), max_chars)}
""".strip()

    plan = f"""# {wi} PLAN
- Request: {user_text}
- Route: {route}
- Output folder: patches/{wi}/
- Rule: Full-file outputs only (no partial snippets)

## Steps
1) QA: reproduce steps + checklist
2) Workers: Front/Back produce full-file patch proposals
3) Manager: merge + finalize FINAL.patch.md
"""
    write_wi_file(wi_dir, "PLAN.md", plan)

    results = {}

    # QA
    if dry_run:
        qa_out = f"""# {wi} QA (DRY_RUN)
## Repro steps
1) ...
## Expected
- ...
## Actual
- ...
## Checklist
- [ ] 버튼 클릭 이벤트 연결 확인
- [ ] 콘솔 에러 확인
- [ ] 네트워크 요청/응답 확인
## Risks
- 운영 반영 전 백업/헬스체크 필요
"""
    else:
        sys_qa = "You are QA. Do not modify code. Provide repro steps, expected/actual, checklist, risks. Output in Korean."
        usr_qa = mask_secrets(f"{shared}\n\n[Task]\n{user_text}\n\nWrite QA report for {wi}.")
        qa_out = call_openai(qa_model, sys_qa, usr_qa)
    write_wi_file(wi_dir, "QA.md", qa_out)
    results["qa"] = qa_out

    # Front
    if route["front"]:
        if dry_run:
            front_out = f"""# {wi} FRONT (DRY_RUN)
## 변경 파일
- (예) /var/www/99sms/send.html
- (예) /var/www/99sms/assets/js/send.js

## 변경 이유
- 클릭 이벤트 미연결/중복 바인딩 가능성

## 전체 코드
(여기에 파일 전체 코드가 들어가야 함)

## 테스트 방법
- 브라우저에서 버튼 클릭 → 네트워크 요청 확인
"""
        else:
            sys_front = "You are Front engineer. Only UI/HTML/CSS/JS. Provide: changed file paths, reasons, FULL FILE code, and test steps. Output in Korean."
            usr_front = mask_secrets(f"{shared}\n\n[Task]\n{user_text}\n\nCreate Front patch proposal for {wi}.")
            front_out = call_openai(worker_front, sys_front, usr_front)
        write_wi_file(wi_dir, "FRONT.patch.md", front_out)
        results["front"] = front_out

    # Back
    if route["back"]:
        if dry_run:
            back_out = f"""# {wi} BACK (DRY_RUN)
## 변경 파일
- (예) /was/99sms/tomcat/webapps/ROOT/...

## 변경 이유
- API 응답/서버 로그 에러 가능성

## 전체 코드 또는 SQL
(여기에 전체 코드/SQL이 들어가야 함)

## 테스트 방법
- curl로 API 호출 → 200/응답 확인
"""
        else:
            sys_back = "You are Backend engineer. Only API/DB/server logic. Provide: changed file paths, reasons, FULL code/SQL, and test steps. Output in Korean."
            usr_back = mask_secrets(f"{shared}\n\n[Task]\n{user_text}\n\nCreate Backend patch proposal for {wi}.")
            back_out = call_openai(worker_back, sys_back, usr_back)
        write_wi_file(wi_dir, "BACK.patch.md", back_out)
        results["back"] = back_out

    # Manager final
    if dry_run:
        final = f"""# {wi} FINAL.patch (DRY_RUN)
## 요약
- QA/Front/Back 산출물 생성 완료(드라이런)

## 다음 행동
1) 실제 코드/파일 경로를 확정
2) FRONT.patch.md / BACK.patch.md를 '전체 코드' 형태로 채우기
3) Phase 2: 텔레그램 연동
"""
    else:
        sys_mgr = "You are Manager(PM). Merge outputs. Resolve conflicts per SPEC. Produce FINAL patch plan and clear next steps. Output in Korean."
        usr_mgr = mask_secrets(
            f"{shared}\n\n[Task]\n{user_text}\n\n"
            f"[QA_OUTPUT]\n{results.get('qa','')}\n\n"
            f"[FRONT_OUTPUT]\n{results.get('front','')}\n\n"
            f"[BACK_OUTPUT]\n{results.get('back','')}\n\n"
            f"Create FINAL.patch.md for {wi}."
        )
        final = call_openai(manager_model, sys_mgr, usr_mgr)

    write_wi_file(wi_dir, "FINAL.patch.md", final)
    results["final"] = final

    state["last_outputs"][wi] = {"route": route, "dir": str(wi_dir), "ts": datetime.utcnow().isoformat() + "Z"}
    for it in state.get("open_items", []):
        if it.get("id") == wi:
            it["status"] = "DONE"
            break

    state["conversation_summary"] = safe_trim((state.get("conversation_summary","") + "\n" + f"{wi}: {user_text}").strip(), 3000)
    append_history(state, "wi_done", {"id": wi, "dir": str(wi_dir)})

    save_state(state)

    print(f"\n[OK] {wi} created.")
    print(f"[OK] outputs: {wi_dir}/")
    print(f"[OK] final: {wi_dir/'FINAL.patch.md'}")

if __name__ == "__main__":
    main()
