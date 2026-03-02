# SPEC (Single Source of Truth)

## 프로젝트
- name: 99sms AI 협업 개발/운영 툴 (Phase 1: CLI MVP)

## 목표(Phase 1)
- CLI로 요청을 입력하면 Work Item(WI)을 생성한다.
- Manager가 Front/Back/QA를 호출(또는 DRY_RUN)하여 산출물을 만든다.
- patches/WI-XXXX/ 아래에 계획/QA/패치/최종 패치를 저장한다.
- state/STATE.json에 진행상태와 마지막 결과를 저장한다.

## 고정 규칙(절대)
1) SPEC.md가 최종 기준이다.
2) Front는 UI(HTML/CSS/JS)만. DB/API 수정 금지.
3) Back은 API/DB만. UI 수정 금지.
4) QA는 수정 금지. 재현/체크리스트/리스크만.
5) 출력 형식:
   - 변경 파일 경로
   - 변경 이유
   - 전체 코드(부분 수정 금지)
   - 테스트 방법(명령 포함)
6) 민감정보(키/비번/토큰)는 절대 출력 금지(마스킹).

## 현재 작업(Work Items)
- (자동으로 STATE.json과 patches/에 기록)
