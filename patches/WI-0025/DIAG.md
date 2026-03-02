# WI-0025 AUTO DIAG

## 1) send.html script includes
196:<script src="/assets/js/sections.js"></script>
197:<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
198:<script src="/assets/js/send.js"></script>
199:<script src="/assets/js/clickprobe.js"></script>
200:<script src="/assets/js/send_patch.js"></script>
201:<script src="/assets/js/send_2x2.js?v=20260227_094116"></script>

## 2) send.html buttons
12:<header class="site-header">
13:  <div class="container header-inner">
14:    <a class="brand" href="/">888</a>
16:    <nav class="nav">
29:    <div class="header-actions">
30:      <a class="btn btn-primary" href="/login.html">로그인</a>
35:<main class="site-main">
39:    <div class="container">
40:      <div class="grid2">
43:        <div class="panel" style="padding:26px">
48:              붙여넣기 최대 <b id="maxPaste">-</b>건 · 엑셀 최대 <b id="maxExcel">-</b>건
52:          <div class="tabs" style="margin-top:12px">
53:            <button class="tab on" data-tab="manual">직접작성</button>
54:            <button class="tab" data-tab="paste">붙여넣기</button>
55:            <button class="tab" data-tab="excel">엑셀 업로드</button>
58:          <div class="tabpane on" id="tab-manual" style="margin-top:12px">
61:                <div class="lbl">번호 입력</div>
62:                <input id="manualInput" class="inp" type="text" placeholder="예) 01012345678" />
64:              <button id="manualAdd" class="btn" type="button">추가</button>
69:          <div class="tabpane" id="tab-paste" style="margin-top:12px">
70:            <div class="lbl">여러 건 붙여넣기</div>
71:            <textarea id="pasteArea" class="txt" style="min-height:130px" placeholder="01011112222&#10;01033334444&#10;(줄바꿈/쉼표/공백 가능)"></textarea>
73:              <div style="opacity:.65;font-size:13px">현재 추출 <b id="pasteCount">0</b>건</div>
74:              <button id="pasteApply" class="btn" type="button">적용</button>
78:          <div class="tabpane" id="tab-excel" style="margin-top:12px">
79:            <div class="lbl">엑셀 업로드 (.xlsx)</div>
80:            <input id="excelFile" class="inp" type="file" accept=".xlsx" />
83:              <div style="opacity:.65;font-size:13px">현재 추출 <b id="excelCount">0</b>건</div>
84:              <button id="excelApply" class="btn" type="button" disabled style="opacity:.55;cursor:not-allowed">적용(준비중)</button>
91:              <div style="opacity:.65;font-size:13px">총 <b id="toCount">0</b>건</div>
94:            <div class="panel" style="margin-top:10px;padding:14px;border-radius:18px;background:rgba(255,255,255,.03)">
95:              <div id="toList" style="display:flex;flex-wrap:wrap;gap:8px"></div>
96:              <div id="toEmpty" style="opacity:.55">수신번호를 추가하세요.</div>
98:                <a class="btn" href="/addr.html">주소록에서 선택</a>
99:                <button id="clearTo" class="btn" type="button">전체삭제</button>
108:                바이트 <b id="byteNow">0</b> / <b id="byteLimit">문서확정필요</b> (초과 시 분할발송)
112:            <textarea id="msg" class="txt" style="min-height:180px;margin-top:10px" placeholder="메시지 내용을 입력"></textarea>
117:                <button id="btnTest" class="btn" type="button">테스트 발송</button>
118:                <button id="btnSend" class="btn btn-primary" type="button">문자 발송</button>
122:            <div class="panel" style="margin-top:14px;padding:14px;border-radius:18px;background:rgba(255,255,255,.03)">
125:                <div id="testTimer" style="opacity:.7">대기</div>
128:                <div class="rowline"><span class="badge">T1</span> <span id="t1">-</span></div>
129:                <div class="rowline"><span class="badge">T2</span> <span id="t2">-</span></div>
130:                <div class="rowline"><span class="badge">T3</span> <span id="t3">-</span></div>
134:            <div class="panel" style="margin-top:14px;padding:14px;border-radius:18px;background:rgba(255,255,255,.03)">
136:              <div id="testHistory" style="display:grid;gap:10px;opacity:.85"></div>
137:              <div id="testHistoryEmpty" style="opacity:.55">기록 없음</div>
145:          <div class="panel grid" style="padding:22px">
147:            <div class="phone">
148:              <div class="phone-top"><div class="phone-notch"></div></div>
149:              <div class="phone-screen">
150:                <div class="phone-title">Message</div>
151:                <div class="bubble" id="previewBubble">내용을 입력하면 미리보기가 표시됩니다.</div>
153:              <div class="phone-bottom"></div>
158:          <div class="panel" style="padding:22px">
169:          <div class="panel" style="padding:22px">
171:            <a class="btn btn-primary" href="https://t.me/Dr_simpson_99" target="_blank" rel="noopener noreferrer" style="width:100%">텔레그램 상담 연결</a>
178:<section><div class="container"><div class="panel" style="padding:18px;display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap">
179:<button id="btnTest" class="btn" type="button" onclick="alert("CLICK OK: TEST")">테스트 발송</button>
180:<button id="btnSend" class="btn btn-primary" type="button" onclick="alert("CLICK OK: SEND")">문자 발송</button>
184:<footer class="site-footer">
185:  <div class="container footer-inner">
186:    <div class="footer-left">
187:      <div class="footer-brand">888</div>
188:      <div class="footer-meta"><span>© 888 All rights reserved.</span></div>
190:    <div class="footer-right">
191:      <a class="btn btn-primary" href="https://t.me/Dr_simpson_99" target="_blank" rel="noopener noreferrer">텔레그램 상담</a>

## 3) send.js click handlers
56:      btn.addEventListener("click", ()=>{
95:      x.addEventListener("click", ()=>{ state.to.delete(num); renderTo(); });
255:    manualAdd.addEventListener("click", ()=>addPhone(manualInput.value));
256:    manualInput.addEventListener("keydown", (e)=>{ if(e.key==="Enter"){ e.preventDefault(); addPhone(manualInput.value); } });
258:    pasteArea.addEventListener("input", ()=>{ pasteCount.textContent = String(parsePhonesFromText(pasteArea.value).length); });
259:    pasteApply.addEventListener("click", ()=>{
270:    clearTo.addEventListener("click", ()=>{ state.to.clear(); renderTo(); });
272:    msg.addEventListener("input", updatePreview);
273:    btnTest.addEventListener("click", doTest);
274:    btnSend.addEventListener("click", doSend);
277:  document.addEventListener("DOMContentLoaded", init);
340:document.addEventListener("DOMContentLoaded", function(){
344:    excelInput.addEventListener("change", function(){
414:document.addEventListener("DOMContentLoaded", function(){
418:    excelInput.addEventListener("change", function(){
483:      x.addEventListener("click", ()=>{
557:  document.addEventListener("DOMContentLoaded", function(){
561:      excelFile.addEventListener("change", function(){
570:      clearTo.addEventListener("click", function(){
594:  document.addEventListener("DOMContentLoaded", function(){
604:      b.addEventListener("click", function(e){
666:      x.addEventListener("click", ()=>{
745:  document.addEventListener("DOMContentLoaded", function(){
748:      excelFile.addEventListener("change", function(){
757:      clearTo.addEventListener("click", function(){

## 4) send_patch.js click handlers
100:  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
104:  document.addEventListener("paste", function(ev){

## 5) file stat
-rw-r--r-- 1 www-data www-data 22163 Feb 26 13:19 /var/www/888.it.kr/assets/js/send.js
-rw-r--r-- 1 www-data www-data  3576 Feb 27 23:55 /var/www/888.it.kr/assets/js/send_patch.js
-rw-r--r-- 1 www-data www-data 10095 Feb 27 13:32 /var/www/888.it.kr/send.html
