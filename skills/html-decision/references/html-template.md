# HTML Template

모든 Tier 공통 — HTML 구조 + base CSS + base JS.

---

## 1. 구조 (strict)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>{고민 주제}</title>
  <style>{§2 CSS}</style>
</head>
<body>
  <header>
    <h1>{고민 주제}</h1>
    <div class="meta">{날짜} · {브랜치 / context summary}</div>
  </header>

  <!-- 결정점 카드 (per Q) -->
  <section class="question" id="q1" data-qid="q1">
    <h2 class="q-title">Q1. {질문}</h2>
    <p class="q-desc">{한 줄 설명}</p>

    <!-- q-context block (모든 Tier 의무) — 왜 이 결정 필요한지 1-2 문장 -->
    <div class="q-context">
      {배경 / 의존성 / 결정 영향 — 1-2 문장}
    </div>

    <!-- 옵션 -->
    <label class="option recommended">
      <input type="radio" name="q1" value="opt1">
      <span class="opt-label">옵션 1 <span class="recommended-tag">권장</span></span>
      <span class="opt-reason">{1줄 이유}</span>
      <!-- option-detail (default 박제 — strategy 결정 시 의무) -->
      <details class="option-detail">
        <summary>자세히</summary>
        <div class="detail-body">
          <p class="pros"><strong>Pros</strong>: {장점}</p>
          <p class="cons"><strong>Cons</strong>: {단점}</p>
          <p class="example"><strong>예시</strong>: {구체 예시 / 결과}</p>
        </div>
      </details>
    </label>
    <label class="option">
      <input type="radio" name="q1" value="opt2">
      <span class="opt-label">옵션 2</span>
      <!-- option-detail 동일 구조 박제 (Pros / Cons / 예시) -->
    </label>
    <!-- ... 옵션 3~5 동일 구조 ... -->
    <label class="option other-option">
      <input type="radio" name="q1" value="other">
      <span class="opt-label">기타 (직접 입력)</span>
    </label>
    <textarea class="other-input" data-for="q1" rows="3" placeholder="직접 입력..."></textarea>

    <!-- (T2+) 코멘트 — 옵션 1·2·… 선택 시 reveal / 기타 선택 시 hide -->
    <div class="comment-wrap" data-for-comment="q1">
      <label class="comment-label">코멘트 (선택, 부연/조건/맥락)</label>
      <textarea class="comment-input" rows="2" placeholder="선택 이유 / 추가 조건 / 부연 설명"></textarea>
    </div>
  </section>

  <!-- ... 추가 결정점 ... -->

  <!-- 출력 영역 — outline card -->
  <section class="output-section" id="submit">
    <h3>📋 결정 결과 → format 선택 → 복사</h3>
    <p class="submit-help">[생성] 클릭 → 결과 확인 → [복사] 클릭 → Claude 에 붙여넣기.</p>
    <div class="output-buttons">
      <button class="gen active" onclick="generate('md')" id="btn-md">📄 MD 생성</button>
      <!-- T2+ 추가: <button class="gen" onclick="generate('json')" id="btn-json">📦 JSON 생성</button> -->
      <!-- T3 추가: <button class="gen" onclick="generate('prompt')" id="btn-prompt">💬 prompt 생성</button> -->
      <span class="button-divider"></span>
      <button class="action" onclick="copyOutput()">📋 복사</button>
      <span class="button-divider"></span>
      <button class="reset" onclick="resetAnswers()">🔄 초기화</button>
    </div>
    <div class="output-wrap">
      <button class="hover-copy" onclick="copyOutput()" title="복사">📋 복사</button>
      <pre id="output">format 생성 후 표시</pre>
    </div>
  </section>

  <!-- toast (복사 / 초기화 feedback) -->
  <div class="toast" id="toast">✅ 복사 완료</div>

  <script>{§3 JS}</script>
</body>
</html>
```

### Tier 차이 요약

| 영역 | T1 | T2 | T3 |
|---|---|---|---|
| **q-context block** | ✅ default | ✅ | ✅ |
| **option-detail (Pros/Cons/예시 `<details>`)** | ✅ default (단순 binary 시 생략 허용) | ✅ default | ✅ 의무 (strategy 결정 시) |
| **toggle-all-details JS** | ✅ default (`<details>` ≥ 1 자동 inject) | ✅ | ✅ |
| 코멘트 textarea | ❌ | ✅ | ✅ |
| 권장 옵션 강조 | ✅ (단순) | ✅ | ✅ |
| 생성 버튼 | MD 만 | MD/JSON | MD/JSON/prompt |
| phase grouping (`<h2 class="phase">`) | ❌ | ❌ | ✅ (N ≥ 8) |
| sticky sidebar + scroll spy | ❌ | ❌ | ✅ (N ≥ 5) |
| localStorage 보존 | ❌ | ❌ | ✅ (N ≥ 5) |
| ack-area / section-intro / preview-panel | ❌ | ❌ | situational (`widgets.md` §12-14) |
| Mermaid / Chart.js / Sortable | ❌ | ❌ | 필요 시 (`widgets.md` 참조) |

---

## 2. Base CSS

```css
:root {
  --bg: #f9fafb; --card: #fff; --border: #e5e7eb; --text: #1f2937;
  --muted: #6b7280; --accent: #2563eb; --rec: #10b981; --rec-bg: #ecfdf5;
}
* { box-sizing: border-box; }
body { font-family: system-ui, -apple-system, "Noto Sans KR", "Segoe UI", sans-serif;
       max-width: 920px; margin: 40px auto; padding: 0 16px;
       background: var(--bg); color: var(--text); line-height: 1.6; }
/* T3 sticky sidebar 박제 시 body layout 은 widgets.md §6 override */
h1 { margin: 0 0 6px; font-size: 1.7em; border-bottom: 3px solid var(--accent);
     padding-bottom: 10px; }
h2.phase { font-size: 1.3em; margin-top: 2.4em; color: #1e40af;
           padding-top: 12px; border-top: 1px solid var(--border); }
.meta { color: var(--muted); font-size: 0.9em; margin-bottom: 1.8em; }
code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px;
       font-family: ui-monospace, SF Mono, Menlo, monospace; font-size: 0.88em; }
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 0.9em; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--border); }
th { background: #f3f4f6; font-weight: 600; }

.question { background: var(--card); border: 1px solid var(--border);
            border-radius: 8px; padding: 20px 24px; margin-bottom: 18px;
            position: relative; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            scroll-margin-top: 20px; }
.q-title { margin: 0 0 4px; font-size: 1.08em; font-weight: 600;
           color: #111827; padding-right: 110px; }
.q-desc { margin: 0 0 6px; color: var(--muted); font-size: 0.92em; }
.q-context { margin: 0 0 14px; padding: 8px 12px; background: #f9fafb;
             border-left: 3px solid #d1d5db; border-radius: 3px;
             color: #4b5563; font-size: 0.9em; }

.option { display: flex; align-items: flex-start; gap: 8px;
          padding: 10px 14px; margin: 6px 0; border-radius: 6px;
          border: 1px solid transparent; cursor: pointer; flex-wrap: wrap;
          transition: background 0.1s, border-color 0.1s; }
.option:hover { background: #f3f4f6; border-color: var(--border); }
.option input { margin-top: 4px; flex-shrink: 0; }
.opt-label { font-weight: 500; flex: 1; }
.opt-reason { width: 100%; padding-left: 24px; color: var(--muted);
              font-size: 0.88em; margin-top: 4px; }
.recommended { background: var(--rec-bg); border-color: #6ee7b7; }
.recommended:hover { border-color: var(--rec); }
.recommended-tag { display: inline-block; background: var(--rec); color: white;
                   padding: 2px 9px; border-radius: 10px; font-size: 0.72em;
                   margin-left: 8px; font-weight: 500; vertical-align: middle; }

/* option-detail (Pros/Cons/예시) — default 박제 */
.option-detail { width: 100%; margin: 8px 0 0 28px; }
.option-detail summary { color: var(--accent); font-size: 0.85em;
                          margin-bottom: 4px; }
.option-detail summary:hover { text-decoration: underline; }
.option-detail .detail-body { margin: 6px 0 0 0; padding: 10px 14px;
                               background: #f9fafb; border: 1px solid var(--border);
                               border-radius: 5px; font-size: 0.88em; }
.option-detail .detail-body h5 { margin: 0 0 6px; font-size: 0.95em;
                                  color: #1e40af; }
.option-detail .detail-body p { margin: 6px 0; }
.option-detail .pros { color: #065f46; }
.option-detail .cons { color: #991b1b; }
.option-detail .example { color: var(--muted); font-style: italic; }
.option-detail code { background: #e0e7ff; color: #1e40af;
                      padding: 1px 5px; border-radius: 3px; }

/* toggle-all-details 버튼 (JS auto-inject — §3 base JS) */
.toggle-all-details { position: absolute; top: 14px; right: 18px;
                      background: transparent; border: 1px solid #d1d5db;
                      color: #4b5563; padding: 4px 10px; font-size: 0.76em;
                      border-radius: 4px; cursor: pointer; font-weight: 500;
                      margin: 0; }
.toggle-all-details:hover { background: #f3f4f6; color: #1f2937;
                            border-color: #9ca3af; }
.toggle-all-details.all-open { background: var(--rec-bg); color: #065f46;
                                border-color: #6ee7b7; }

textarea.other-input { width: 100%; min-height: 60px; padding: 8px 12px;
                       border: 1px solid #d1d5db; border-radius: 4px;
                       font-family: inherit; font-size: 0.95em;
                       resize: vertical; margin-top: 6px; }
textarea.other-input:focus { outline: none; border-color: var(--accent);
                             box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }

/* T2+ 코멘트 — default hidden, .visible 시 reveal */
.comment-wrap { display: none; margin-top: 10px; padding-top: 8px;
                border-top: 1px dashed var(--border); }
.comment-wrap.visible { display: block; }
.comment-label { font-size: 0.82em; color: var(--muted); margin-bottom: 4px;
                 display: block; }
textarea.comment-input { width: 100%; min-height: 48px; padding: 7px 11px;
                         border: 1px solid #d1d5db; border-radius: 4px;
                         font-family: inherit; font-size: 0.9em;
                         resize: vertical; background: #fafbfc; }
textarea.comment-input:focus { outline: none; border-color: var(--rec);
                               box-shadow: 0 0 0 3px rgba(16,185,129,0.1);
                               background: white; }

/* details/summary — disclosure arrow 통합 */
details summary { cursor: pointer; list-style: none; display: inline-flex;
                  align-items: center; gap: 6px; user-select: none; }
details summary::-webkit-details-marker { display: none; }
details summary::before { content: "▶"; display: inline-block;
                          font-size: 0.7em; transition: transform 0.15s; }
details[open] summary::before { transform: rotate(90deg); }

/* output-section = outline card (모든 Tier default) */
.output-section { margin-top: 2.5em; padding: 24px; background: var(--card);
                  border: 2px solid var(--accent); border-radius: 10px; }
.output-section h3 { margin-top: 0; color: #1e40af; }
.output-section .submit-help { color: var(--muted); margin: 0 0 14px;
                                font-size: 0.93em; }
.output-buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px;
                  align-items: center; }
.button-divider { width: 1px; height: 28px; background: var(--border);
                  margin: 0 4px; }
button { padding: 10px 20px; background: var(--accent); color: white;
         border: none; border-radius: 5px; font-size: 0.95em; cursor: pointer;
         font-weight: 500; transition: background 0.15s; }
button:hover { background: #1d4ed8; }
/* 다중 button 스타일 — .gen (outline) / .action (녹색) / .reset (회색) */
button.gen { background: white; color: var(--accent);
             border: 1px solid var(--accent); }
button.gen:hover { background: #eff6ff; }
button.gen.active { background: var(--accent); color: white; }
button.action { background: var(--rec); }
button.action:hover { background: #059669; }
button.reset { background: #6b7280; padding: 10px 16px; }
button.reset:hover { background: #4b5563; }

.output-wrap { position: relative; margin-top: 6px; }
#output { background: #1f2937; color: #f9fafb; padding: 16px;
          border-radius: 6px; white-space: pre-wrap; font-size: 0.85em;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
          line-height: 1.5; max-height: 500px; overflow: auto; margin: 0; }
.hover-copy { position: absolute; top: 8px; right: 8px; opacity: 0;
              transition: opacity 0.2s; background: rgba(255,255,255,0.12);
              color: white; border: 1px solid rgba(255,255,255,0.3);
              padding: 4px 10px; font-size: 0.85em; border-radius: 4px;
              cursor: pointer; font-weight: 500; }
.output-wrap:hover .hover-copy { opacity: 1; }
.hover-copy:hover { background: rgba(255,255,255,0.25); }

/* toast (CSS class 박제 — 복사 / 초기화 feedback) */
.toast { position: fixed; bottom: 20px; right: 20px; background: var(--rec);
         color: white; padding: 12px 20px; border-radius: 6px;
         font-size: 0.9em; font-weight: 500; opacity: 0;
         transition: opacity 0.3s; pointer-events: none;
         box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 9999; }
.toast.show { opacity: 1; }
```

---

## 3. Base JS

```javascript
const SOURCE_HTML = "{filepath 박제 — 출력 file 의 자신 path}";
const TOPIC = "{고민 주제}";
const DATE = "{YYYY-MM-DD}";

// 1. 기타 textarea input 시 자동 라디오 체크 + 코멘트 hide
document.querySelectorAll('textarea.other-input').forEach(input => {
  input.addEventListener('input', () => {
    const qId = input.getAttribute('data-for');
    const otherRadio = document.querySelector(`input[name="${qId}"][value="other"]`);
    if (otherRadio) otherRadio.checked = true;
    updateCommentVisibility(qId);
  });
});

// 2. 코멘트 reveal — T2+ 에서만 의미 있음. T1 = .comment-wrap 자체 없음
function updateCommentVisibility(qId) {
  const wrap = document.querySelector(`.comment-wrap[data-for-comment="${qId}"]`);
  if (!wrap) return;
  const checkedNonOther = Array.from(
    document.querySelectorAll(`input[name="${qId}"]:checked`)
  ).filter(i => i.value !== 'other');
  if (checkedNonOther.length > 0) {
    wrap.classList.add('visible');
  } else {
    wrap.classList.remove('visible');
    const t = wrap.querySelector('textarea.comment-input');
    if (t) t.value = '';
  }
}

document.querySelectorAll('input[type="radio"], input[type="checkbox"]')
  .forEach(i => i.addEventListener('change', () => updateCommentVisibility(i.name)));

// 3. 답 수집
function collectAnswers() {
  const answers = {};
  document.querySelectorAll('.question').forEach(q => {
    const qid = q.dataset.qid;
    const title = q.querySelector('.q-title').textContent;
    const checked = Array.from(q.querySelectorAll('input:checked'));
    const otherText = (q.querySelector('textarea.other-input')?.value || '').trim();
    const commentText = getComment(qid);
    let value = null;
    let isOther = false;
    if (checked.length > 0) {
      const vals = checked.map(c => {
        if (c.value === 'other') {
          isOther = true;
          return otherText ? `기타: ${otherText}` : '기타';
        }
        return c.parentElement.querySelector('.opt-label')?.textContent.trim() || c.value;
      });
      value = checked[0].type === 'checkbox' ? vals : vals[0];
    }
    answers[qid] = { title, value, isOther,
                     comment: isOther ? '' : commentText,
                     type: checked[0]?.type || 'radio' };
  });
  return answers;
}

function getComment(qid) {
  const wrap = document.querySelector(`.comment-wrap[data-for-comment="${qid}"]`);
  if (!wrap || !wrap.classList.contains('visible')) return '';
  return (wrap.querySelector('textarea.comment-input')?.value || '').trim();
}

// 4. generate — T1 = MD 만, T2 = MD/JSON, T3 = MD/JSON/prompt
function generate(format) {
  const answers = collectAnswers();
  let text = '';
  if (format === 'md') text = toMarkdown(answers);
  else if (format === 'json') text = toJSON(answers);
  else if (format === 'prompt') text = toPrompt(answers);
  document.getElementById('output').textContent = text;
  // 활성 format button 표시
  document.querySelectorAll('.output-buttons button.gen').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + format)?.classList.add('active');
}

function toMarkdown(answers) {
  let md = `<!-- html-decision-result -->\n# ${TOPIC} — 결정 결과\n\n`;
  md += `**출처 HTML**: \`${SOURCE_HTML}\`\n`;
  md += `**날짜**: ${DATE}\n\n---\n\n`;
  for (const [qid, a] of Object.entries(answers)) {
    md += `### ${a.title}\n`;
    if (Array.isArray(a.value)) {
      md += `**답**:\n${a.value.map(v => `- ${v}`).join('\n')}\n`;
    } else {
      md += `- **답**: ${a.value || '(미선택)'}\n`;
    }
    if (a.comment && !a.isOther) {
      md += `- **코멘트**:\n${a.comment.split('\n').map(l => `  ${l}`).join('\n')}\n`;
    }
    md += '\n';
  }
  return md;
}

// 5. 복사 / 초기화 — toast feedback (CSS class 박제)
function copyOutput() {
  const text = document.getElementById('output').textContent;
  if (!text || text === 'format 생성 후 표시' || text === '답안 초기화됨') {
    showToast('⚠️ 먼저 [생성] 클릭');
    return;
  }
  navigator.clipboard?.writeText(text).then(
    () => showToast('✅ 복사 완료'),
    () => fallbackCopy(text)
  );
}
function fallbackCopy(text) {
  const ta = document.createElement('textarea');
  ta.value = text; document.body.appendChild(ta); ta.select();
  try { document.execCommand('copy'); showToast('✅ 복사 완료'); }
  catch { showToast('❌ 복사 실패'); }
  document.body.removeChild(ta);
}
function showToast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1800);
}
function resetAnswers() {
  if (!confirm('모든 답안을 초기화할까요?')) return;
  document.querySelectorAll('input[type="radio"], input[type="checkbox"]')
    .forEach(i => i.checked = false);
  document.querySelectorAll('textarea').forEach(t => t.value = '');
  document.querySelectorAll('.comment-wrap.visible')
    .forEach(w => w.classList.remove('visible'));
  document.getElementById('output').textContent = '답안 초기화됨';
  showToast('🔄 초기화 완료');
}

// 6. toggle-all-details auto-inject (모든 Tier default — <details> ≥ 1 있는 Q 마다)
window.addEventListener('load', () => {
  document.querySelectorAll('.question').forEach(q => {
    if (q.querySelectorAll('details').length === 0) return;
    const btn = document.createElement('button');
    btn.className = 'toggle-all-details';
    btn.textContent = '모두 펴기';
    btn.type = 'button';
    btn.onclick = (e) => {
      e.stopPropagation();
      const list = q.querySelectorAll('details');
      const allOpen = Array.from(list).every(d => d.open);
      list.forEach(d => { d.open = !allOpen; });
      btn.textContent = allOpen ? '모두 펴기' : '모두 접기';
      btn.classList.toggle('all-open', !allOpen);
    };
    q.appendChild(btn);
  });
});
```

T2 / T3 추가 함수 (`toJSON`, `toPrompt`) 는 `output-formats.md` 참조.

---

## 4. 출력 file 의 자신 path 박제

JS 안 `const SOURCE_HTML = "..."` 에 생성 시점에 결정된 file path 박제. MD 출력 header 의 `**출처 HTML**: \`${SOURCE_HTML}\`` 에서 활용.
