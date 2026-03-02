# WI-0026 PLAN
- Request: AUTO-DIAG: send.html 버튼 클릭 안됨. send.html/send.js/send_patch.js에서 클릭 이벤트/버튼 요소/스크립트 로딩 상태를 자동 추출해서 DIAG.md로 저장해.
- Route: {'qa': True, 'front': True, 'back': False}
- Output folder: patches/WI-0026/
- Rule: Full-file outputs only (no partial snippets)

## Steps
1) QA: reproduce steps + checklist
2) Workers: Front/Back produce full-file patch proposals
3) Manager: merge + finalize FINAL.patch.md
