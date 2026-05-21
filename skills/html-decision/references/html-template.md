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
  <section class="question" data-qid="q1">
    <h2 class="q-title">Q1. {질문}</h2>
    <p class="q-desc">{한 줄 설명}</p>

    <!-- 옵션 -->
    <label class="option recommended">
      <input type="radio" name="q1" value="opt1">
      <span class="opt-label">옵션 1 <span class="recommended-tag">권장</span></span>
      <span class="opt-reason">{1줄 이유}</span>
    </label>
    <label class="option">
      <input type="radio" name="q1" value="opt2">
      <span class="opt-label">옵션 2</span>
    </label>
    <!-- ... -->
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

  <!-- 출력 영역 -->
  <section class="output-section">
    <div class="output-buttons">
      <button onclick="generate('md')">📄 MD 생성</button>
      <!-- T2+ 추가: <button onclick="generate('json')">📦 JSON 생성</button> -->
      <!-- T3 추가: <button onclick="generate('prompt')">💬 prompt 생성</button> -->
      <button onclick="copyOutput()">📋 복사</button>
      <button onclick="resetAnswers()">🔄 초기화</button>
    </div>
    <div class="output-wrap">
      <button class="hover-copy" onclick="copyOutput()" title="복사">📋</button>
      <pre id="output">생성 후 표시</pre>
    </div>
  </section>

  <script>{§3 JS}</script>
</body>
</html>
```

### Tier 차이 요약

| 영역 | T1 | T2 | T3 |
|---|---|---|---|
| 코멘트 textarea | ❌ | ✅ | ✅ |
| 권장 옵션 강조 | ✅ (단순) | ✅ | ✅ |
| 생성 버튼 | MD 만 | MD/JSON | MD/JSON/prompt |
| phase grouping (`<h2 class="phase">`) | ❌ | ❌ | ✅ |
| sticky sidebar + scroll spy | ❌ | ❌ | ✅ |
| localStorage 보존 | ❌ | ❌ | ✅ |
| Mermaid / Chart.js / Sortable | ❌ | ❌ | 필요 시 (`widgets.md` 참조) |

---

## 2. Base CSS

```css
:root {
  --bg: #f9fafb; --card: #fff; --border: #e5e7eb; --text: #1f2937;
  --muted: #6b7280; --accent: #2563eb; --rec: #10b981; --rec-bg: #ecfdf5;
}
* { box-sizing: border-box; }
body { font-family: system-ui, "Noto Sans KR", sans-serif; max-width: 920px;
       margin: 40px auto; padding: 0 16px; background: var(--bg); color: var(--text);
       line-height: 1.55; }
header h1 { margin: 0 0 6px; font-size: 1.6em; }
.meta { color: var(--muted); font-size: 0.88em; margin-bottom: 24px; }

.question { background: var(--card); border: 1px solid var(--border);
            border-radius: 8px; padding: 18px 22px; margin-bottom: 18px;
            position: relative; }
.q-title { margin: 0 0 4px; font-size: 1.1em; }
.q-desc { margin: 0 0 12px; color: var(--muted); font-size: 0.92em; }

.option { display: flex; align-items: flex-start; gap: 8px;
          padding: 10px 12px; border-radius: 5px; cursor: pointer;
          flex-wrap: wrap; }
.option:hover { background: #f3f4f6; }
.option input { margin-top: 4px; }
.opt-label { font-weight: 500; }
.opt-reason { width: 100%; padding-left: 24px; color: var(--muted);
              font-size: 0.85em; margin-top: 2px; }
.recommended { background: var(--rec-bg); border-left: 3px solid var(--rec);
               padding-left: 9px; }
.recommended-tag { background: var(--rec); color: white; padding: 2px 8px;
                   border-radius: 10px; font-size: 0.7em; margin-left: 6px; }

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

.output-section { margin-top: 28px; }
.output-buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.output-buttons button { padding: 9px 18px; background: var(--accent);
                         color: white; border: none; border-radius: 5px;
                         cursor: pointer; font-size: 0.92em; }
.output-buttons button:hover { background: #1d4ed8; }
.output-buttons button:last-child { background: #6b7280; }
.output-wrap { position: relative; }
#output { background: #1f2937; color: #f9fafb; padding: 16px;
          border-radius: 6px; white-space: pre-wrap; font-size: 0.88em;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
          max-height: 500px; overflow: auto; }
.hover-copy { position: absolute; top: 8px; right: 8px; opacity: 0;
              transition: opacity 0.2s; background: rgba(255,255,255,0.1);
              color: white; border: 1px solid rgba(255,255,255,0.3);
              padding: 4px 10px; font-size: 0.85em; border-radius: 4px;
              cursor: pointer; }
.output-wrap:hover .hover-copy { opacity: 1; }
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

// 5. 복사 / 초기화
function copyOutput() {
  const text = document.getElementById('output').textContent;
  if (!text || text === '생성 후 표시') return;
  navigator.clipboard?.writeText(text).then(
    () => flash('복사 완료'),
    () => fallbackCopy(text)
  );
}
function fallbackCopy(text) {
  const ta = document.createElement('textarea');
  ta.value = text; document.body.appendChild(ta); ta.select();
  try { document.execCommand('copy'); flash('복사 완료'); } catch {}
  document.body.removeChild(ta);
}
function flash(msg) {
  const el = document.createElement('div');
  el.textContent = msg;
  el.style.cssText = 'position:fixed;bottom:24px;right:24px;background:#10b981;color:white;padding:10px 18px;border-radius:6px;z-index:9999;';
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 1800);
}
function resetAnswers() {
  document.querySelectorAll('input[type="radio"], input[type="checkbox"]')
    .forEach(i => i.checked = false);
  document.querySelectorAll('textarea').forEach(t => t.value = '');
  document.querySelectorAll('.comment-wrap.visible')
    .forEach(w => w.classList.remove('visible'));
  document.getElementById('output').textContent = '생성 후 표시';
}
```

T2 / T3 추가 함수 (`toJSON`, `toPrompt`) 는 `output-formats.md` 참조.

---

## 4. 출력 file 의 자신 path 박제

JS 안 `const SOURCE_HTML = "..."` 에 생성 시점에 결정된 file path 박제. MD 출력 header 의 `**출처 HTML**: \`${SOURCE_HTML}\`` 에서 활용.
