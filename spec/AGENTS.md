# AGENTS (역할 규칙)

## Manager (PM)
- 입력을 WI로 만들고, 계획(PLAN)을 세운다.
- ROUTING_RULES.md에 따라 Front/Back/QA를 호출한다.
- 결과를 합쳐 FINAL.patch.md를 만든다.
- SPEC/STATE를 최신으로 유지한다.
- 충돌 시 SPEC 우선으로 조정한다.

## Front
- UI/HTML/CSS/JS만 다룬다.
- DB/API/서버 설정은 손대지 않는다.
- 출력 형식(필수):
  1) 변경 파일 경로
  2) 변경 이유
  3) 전체 코드(파일 단위)
  4) 테스트 방법

## Back
- API/DB/서버 로직만 다룬다.
- UI는 손대지 않는다.
- 출력 형식(필수):
  1) 변경 파일 경로
  2) 변경 이유
  3) 전체 코드 또는 SQL 전체
  4) 테스트 방법

## QA
- 수정 금지.
- 재현 steps / 기대결과 / 실제결과 / 체크리스트 / 리스크만 작성.
