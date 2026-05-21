# Widgets & Visualizations

**T3 전용** (SKILL.md §2.1 trigger 충족 시). T1/T2 는 `html-template.md` (+ T2 는 `output-formats.md`) 만 읽기.

phase grouping + slider widget + 시각화 (Mermaid/Chart.js) + sticky sidebar + localStorage 복원 + ack/section-intro/preview-panel.

---

## 1. widget matrix (결정 성격 별)

| 결정 성격 | widget | MD 출력 |
|---|---|---|
| 단일 답 | radio + 기타 + 코멘트 | `**답**: {단일}` |
| 다중 답 | checkbox + 기타 + 코멘트 | `**답**:\n- ...` list |
| 정량 평가 (확신도/위험도) | slider (range) + 코멘트 | `**답**: 7/10` |
| binary on/off | radio (`yes`/`no`) + 코멘트 | `**답**: yes` |
| 순서 / 우선순위 | checkbox 다중 + 코멘트에 순서 기재 | `**답**:\n- ...` (코멘트에 순서) |
| 조건부 follow-up | multi-step reveal | 답 + 후속 결정 |
| 자유 텍스트 | textarea only | `**답**: {자유}` |

코멘트 = 옵션/값 선택 시 reveal. "기타" 또는 미선택 = 숨김.

---

## 2. slider widget

```html
<div class="slider-wrap">
  <input type="range" name="q1" min="0" max="10" value="5" oninput="this.nextElementSibling.textContent=this.value">
  <span class="slider-value">5</span> / 10
</div>
```

```javascript
// collectAnswers 안 slider 처리 추가
if (input.type === 'range') {
  answers[qid] = { ...answers[qid], value: `${input.value}/${input.max}`, type: 'slider' };
}
// 코멘트 reveal — slider 는 항상 값 있음 → input event 에서 항상 reveal
input.addEventListener('input', () => updateCommentVisibilityForSlider(qid));
```

```javascript
function updateCommentVisibilityForSlider(qid) {
  const wrap = document.querySelector(`.comment-wrap[data-for-comment="${qid}"]`);
  if (wrap) wrap.classList.add('visible');
}
```

---

## 5. phase grouping

결정점 8+ 시 영역별 그룹핑 — `<h2 class="phase">` heading + `<section class="phase-section">`.

```html
<h2 class="phase">Phase A. 설계 합의</h2>
<section class="phase-section">
  <!-- 결정점 카드들 -->
</section>

<h2 class="phase">Phase B. 적용 우선순위</h2>
<section class="phase-section">
  <!-- 결정점 카드들 -->
</section>
```

MD 출력 시 `## {Phase 명}` 헤딩 박제. `data-phase` attribute 활용:
```html
<section class="question" data-qid="q1" data-phase="Phase A. 설계 합의">
```

`toMarkdown` 안 phase 별 grouping:
```javascript
function toMarkdown(answers) {
  // ... header ...
  const byPhase = {};
  document.querySelectorAll('.question').forEach(q => {
    const phase = q.dataset.phase || '_default';
    (byPhase[phase] ||= []).push(q.dataset.qid);
  });
  for (const [phase, qids] of Object.entries(byPhase)) {
    if (phase !== '_default') md += `## ${phase}\n\n`;
    for (const qid of qids) {
      // ... Q block ...
    }
  }
}
```

---

## 6. sticky sidebar + scroll spy (N ≥ 5 시 의무)

★ 발동 시 body layout = **full-width flex** (base CSS 의 `max-width: 920px` override). 260px 흰 sidebar + flex main.

### 6.1 HTML 구조

```html
<body>
  <aside class="sidebar">
    <h3>진행</h3>
    <div class="progress-wrap">
      <div class="progress"><div class="progress-bar" id="prog-bar"></div></div>
      <span class="progress-text" id="prog-text">0/{N} 답함</span>
    </div>

    <h3>네비게이션</h3>
    <nav>
      <ul class="nav-list">
        <!-- (선택) ack / flow section anchor -->
        <li><a href="#ack" class="nav-q">📥 이전 결정 ack</a></li>
        <li><a href="#flow" class="nav-q">🔄 timeline</a></li>
        <!-- 결정점 anchor -->
        <li style="margin-top: 8px;"><a href="#q1" class="nav-q" data-q="q1">Q1. {짧은 제목}</a></li>
        <li><a href="#q2" class="nav-q" data-q="q2">Q2. ...</a></li>
        <!-- ... -->
        <!-- 결과 추출 anchor -->
        <li style="padding-top: 10px;"><a href="#submit" class="nav-q" style="color: var(--accent); font-weight: 600;">✏️ 결과 추출</a></li>
      </ul>
    </nav>
  </aside>

  <main class="main">
    <!-- header / ack / flow / questions / output-section -->
  </main>
</body>
```

### 6.2 CSS — v1-grade sidebar (★ base CSS override)

```css
/* sidebar 박제 시 body layout override — base CSS 의 max-width:920px / margin:40px auto 무효 */
body { display: flex; min-height: 100vh; max-width: none; margin: 0; padding: 0;
       background: var(--bg); }

.sidebar { position: sticky; top: 0; height: 100vh; width: 260px;
           flex-shrink: 0; padding: 24px 20px; background: var(--card);
           border-right: 1px solid var(--border); overflow-y: auto;
           font-size: 0.88em; }
.sidebar h3 { font-size: 0.95em; color: #4b5563; margin: 18px 0 8px;
              text-transform: uppercase; letter-spacing: 0.05em; }
.sidebar h3:first-child { margin-top: 0; }

.progress-wrap { margin-bottom: 20px; }
.progress { background: var(--border); height: 8px; border-radius: 4px;
            overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, var(--rec), #059669);
                width: 0%; transition: width 0.3s; }
.progress-text { font-size: 0.85em; color: var(--muted);
                 margin-top: 4px; display: block; }

.nav-list { list-style: none; padding: 0; margin: 0; }
.nav-q { display: block; padding: 5px 12px; color: #4b5563;
         text-decoration: none; font-size: 0.85em;
         border-left: 3px solid transparent; transition: all 0.15s; }
.nav-q:hover { background: #f3f4f6; color: var(--text); }
.nav-q.active { background: var(--rec-bg); border-left-color: var(--rec);
                color: #065f46; font-weight: 500; }
.nav-q.answered::before { content: "✓ "; color: var(--rec); font-weight: 600; }

.main { flex: 1; max-width: calc(100% - 260px); padding: 40px 50px 80px;
        overflow-x: hidden; }
.question { scroll-margin-top: 20px; }

@media (max-width: 900px) {
  body { flex-direction: column; }
  .sidebar { position: relative; width: 100%; height: auto;
             border-right: 0; border-bottom: 1px solid var(--border); }
  .main { max-width: 100%; padding: 24px; }
  .q-title { padding-right: 0; }
  .toggle-all-details { position: relative; top: auto; right: auto;
                        display: inline-block; margin-bottom: 8px; }
}
```

### 6.3 JS — scroll spy + visual progress + answered marker

```javascript
const TOTAL_Q = document.querySelectorAll('.question').length;

// scroll spy
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      document.querySelectorAll('.nav-q').forEach(a => a.classList.remove('active'));
      const navQ = document.querySelector(`.nav-q[data-q="${e.target.dataset.qid}"]`);
      if (navQ) navQ.classList.add('active');
    }
  });
}, { threshold: 0.4, rootMargin: '-100px 0px -50% 0px' });
document.querySelectorAll('.question').forEach(q => observer.observe(q));

// visual progress + answered marker
function updateProgress() {
  let answered = 0;
  document.querySelectorAll('.question').forEach(q => {
    const qid = q.dataset.qid;
    const checked = q.querySelector('input:checked');
    const otherText = (q.querySelector('textarea.other-input')?.value || '').trim();
    const ok = checked && (checked.value !== 'other' || otherText.length > 0);
    if (ok) answered++;

    const navQ = document.querySelector(`.nav-q[data-q="${qid}"]`);
    if (navQ) navQ.classList.toggle('answered', ok);
  });
  const pct = Math.round(answered / TOTAL_Q * 100);
  document.getElementById('prog-bar').style.width = pct + '%';
  document.getElementById('prog-text').textContent = `${answered}/${TOTAL_Q} 답함 (${pct}%)`;
}
document.addEventListener('change', updateProgress);
document.addEventListener('input', updateProgress);
window.addEventListener('load', updateProgress);
```

---

## 7. localStorage 복원 (결정점 8+)

```javascript
const STORAGE_KEY = `html-decision:${SOURCE_HTML}`;

function saveState() {
  const state = {};
  document.querySelectorAll('input[type="radio"]:checked, input[type="checkbox"]:checked')
    .forEach(i => state[`${i.name}:${i.value}`] = true);
  document.querySelectorAll('textarea').forEach(t => {
    if (t.value) state[`text:${t.dataset.for || t.closest('.comment-wrap')?.dataset.forComment}`] = t.value;
  });
  document.querySelectorAll('input[type="range"]').forEach(r => state[`range:${r.name}`] = r.value);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadState() {
  try {
    const state = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    Object.entries(state).forEach(([key, val]) => {
      if (key.startsWith('text:')) {
        const id = key.slice(5);
        const t = document.querySelector(`textarea[data-for="${id}"], .comment-wrap[data-for-comment="${id}"] textarea`);
        if (t) t.value = val;
      } else if (key.startsWith('range:')) {
        const r = document.querySelector(`input[type="range"][name="${key.slice(6)}"]`);
        if (r) r.value = val;
      } else {
        const [name, value] = key.split(':');
        const i = document.querySelector(`input[name="${name}"][value="${value}"]`);
        if (i) { i.checked = true; updateCommentVisibility(name); }
      }
    });
  } catch {}
}
window.addEventListener('load', loadState);
document.addEventListener('change', saveState);
document.addEventListener('input', saveState);
```

resetAnswers 안 `localStorage.removeItem(STORAGE_KEY)` 추가.

---

## 8. 시각화 (영향 명확 시 한정 박제)

| 영역 | rule |
|---|---|
| 옵션 비교 | `<table>` — 3+ 옵션 시 박제 |
| 흐름 / 결정 cascading | Mermaid flowchart → **§15 사용 spec 참조** |
| 결정 분포 | **Chart.js doughnut/bar** (CDN) — 결정점 5+ 시 박제 |
| 영향 file / scope | inline SVG file tree 또는 list — 3+ file 영향 시 박제 |
| before / after | side-by-side panel |
| 코드 예시 | `<pre><code>` |
| 긴 context | `<details><summary>` 접기 (CSS § html-template) |

CDN:
- Mermaid: `https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js`
- Chart.js: `https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js`

grace degradation: CDN load 실패 시 기본 form 동작 보존 의무.

---

## 9. toggle-all-details 버튼 (details 다중 시)

→ **모든 Tier default 박제** — `html-template.md` §2 CSS + §3 JS 안에 이미 포함. T3 에서는 별도 처리 불필요.

---

## 10. option-detail (옵션 카드 안 Pros/Cons/예시)

→ **모든 Tier default** — HTML 구조 + CSS 는 `html-template.md` 안 박제 완료.

### 10.1 T3 strategy 결정 시 의무 영역

`<details class="option-detail">` 안 **3 필드** 박제:

```html
<details class="option-detail">
  <summary>자세히</summary>
  <div class="detail-body">
    <p class="pros"><strong>Pros</strong>: {장점 1-2 문장}</p>
    <p class="cons"><strong>Cons</strong>: {단점 1-2 문장}</p>
    <p class="example"><strong>예시</strong>: {구체 결과 / 수치 / 코드}</p>
  </div>
</details>
```

- **Pros / Cons** = 결정 영향 본질 (의무)
- **예시** = 결과 구체화 — code / 수치 / file 영향 영역 (가능 시)

### 10.2 단순 케이스 — 1줄 reason 으로 갈음

옵션 = 단순 binary 또는 명확한 차이 시 `.opt-reason` 1줄로 갈음 박제:

```html
<span class="opt-reason">{1줄 이유}</span>
```

판단 기준: Pros 와 Cons 가 *같은* 문장 안 자연히 담기면 1줄 reason 박제. *서로 다른* 영역이면 `<details>` 박제.

---

## 11. q-context block (왜 이 결정 필요)

→ **모든 Tier default** — HTML 구조 + CSS 는 `html-template.md` 안 박제 완료.

### 11.1 박제 구조

```html
<p class="q-desc">{한 줄 설명}</p>
<div class="q-context">
  {배경 / 의존성 / 결정 영향 — 1-2 문장}
</div>
```

### 11.2 q-desc vs q-context 차이

- **q-desc** = 질문 그 자체의 한 줄 부연 (예: "단일 PR vs phased")
- **q-context** = *왜* 이 결정 필요한지 (예: "Step 1-4 의 file 분포: references 5 / sub-agent 4 / skill body 2 / docs 5-6. 의존 sequence = Step 1 → 2 → 3 → 4.")

발동: context 가 *명시* 가능한 경우 한정 박제 (단순 선호도 = 생략).

---

## 12. ack-area (선행 결정 박제 — T3 trigger #4)

연속 cycle 안 *이전 결정* 정리 highlight. working memo / 이전 결정 cross-ref.

```html
<section id="ack">
  <div class="ack-area">
    <h4>📥 이전 N 결정 확정 ack — working memo 박제</h4>
    <p>working memo: <code>{working memo path}</code> §{section} 안 결정 통합 표 박제.</p>
    <p>{결정 요약 1-2 문장 — 영역 별 카운트 / 핵심 결과}</p>
    <p>★ 본 결정 = 위 결정 후 다음 step 진행 전 사전 확정 의무 영역.</p>
  </div>
</section>
```

CSS:

```css
.ack-area { background: #ecfdf5; border: 1px solid #6ee7b7;
            border-radius: 8px; padding: 16px 22px; margin-bottom: 22px;
            font-size: 0.92em; }
.ack-area h4 { margin: 0 0 8px; color: #065f46; }
.ack-area p { margin: 4px 0; color: #047857; }
.ack-area code { background: #d1fae5; color: #065f46; }
```

발동: T3 trigger #4 (선행 결정 ack 필요) 시 한정 박제.

---

## 13. section-intro (영역 소개 highlight box)

결정점 grouping / 영역 안내. 노란 highlight box.

```html
<div class="section-intro">
  Q1 = {영역 1} / Q2 = {영역 2} / Q3 = {영역 3} (★ {강조 메모}).
</div>
```

CSS:

```css
.section-intro { background: #fef3c7; border-left: 4px solid #f59e0b;
                 padding: 14px 18px; margin-bottom: 22px; border-radius: 4px;
                 font-size: 0.94em; }
```

발동: 결정점 grouping (phase 분리 또는 영역 별 묶음) 시 한정 박제.

---

## 14. preview-panel (옵션 영향 live preview)

옵션 선택 시 영향 영역 즉시 view — table / Mermaid highlight / file list.

### 14.1 HTML 구조

```html
<div class="preview-panel">
  <h5>📋 선택 시 영향 (live)</h5>
  <div id="q1-preview">
    <p class="empty">옵션 선택 시 영향 영역 view</p>
  </div>
</div>
```

CSS:

```css
.preview-panel { margin-top: 14px; padding: 14px 18px; background: #eff6ff;
                 border-left: 4px solid var(--accent); border-radius: 4px;
                 font-size: 0.9em; }
.preview-panel h5 { margin: 0 0 8px; color: #1e40af; }
.preview-panel .empty { color: var(--muted); font-style: italic; }
.preview-panel table { width: 100%; border-collapse: collapse; background: white;
                       font-size: 0.88em; }
.preview-panel th, .preview-panel td { padding: 6px 10px;
                                        border-bottom: 1px solid #dbeafe;
                                        text-align: left; }
.preview-panel th { background: #dbeafe; font-weight: 600; color: #1e40af; }
```

### 14.2 JS — 옵션 별 preview 데이터 + update 함수

```javascript
const Q1_PREVIEWS = {
  'opt1': { title: '{옵션 1 결과}',
            rows: [['{영역}', '{값}'], ['{영역}', '{값}']] },
  'opt2': { title: '{옵션 2 결과}',
            rows: [['{영역}', '{값}']] },
};

function updateQ1Preview() {
  const sel = document.querySelector('input[name="q1"]:checked');
  const panel = document.getElementById('q1-preview');
  if (!sel) {
    panel.innerHTML = '<p class="empty">옵션 선택 시 영향 영역 view</p>';
    return;
  }
  const data = Q1_PREVIEWS[sel.value];
  if (!data) { panel.innerHTML = '<p class="empty">preview 없음</p>'; return; }
  let html = '<strong>' + data.title + '</strong><table>';
  data.rows.forEach(r => {
    html += '<tr><th>' + r[0] + '</th><td>' + r[1] + '</td></tr>';
  });
  html += '</table>';
  panel.innerHTML = html;
}

document.querySelectorAll('input[name="q1"]')
  .forEach(i => i.addEventListener('change', updateQ1Preview));
window.addEventListener('load', updateQ1Preview);
```

발동: 옵션 영향 *예측 가능* + 영향 영역이 구체적일 때 (예: PR 분포 / file 영향 / 수치 변경) 한정 박제.

---

## 15. Mermaid flowchart usage

§8 CDN load 후 의존 sequence / timeline / cascading 시각화.

### 15.1 HTML 구조

```html
<section id="flow">
  <div class="flow-area">
    <h4>🔄 {Q 영역} timeline</h4>
    <div class="mermaid-wrap">
      <div class="mermaid">
flowchart LR
    A[Step 1<br/>{영역}<br/>{수치}] --> B[Step 2<br/>{영역}]
    B --> C[Step 3<br/>{영역}]
    style A fill:#dbeafe,stroke:#1e40af
    style B fill:#fef3c7,stroke:#f59e0b
    style C fill:#ecfdf5,stroke:#10b981
      </div>
    </div>
  </div>
</section>
```

CSS:

```css
.flow-area { background: var(--card); border: 1px solid var(--border);
             border-radius: 8px; padding: 20px; margin-bottom: 22px; }
.flow-area h4 { margin: 0 0 12px; color: #4b5563; font-size: 0.9em;
                text-transform: uppercase; letter-spacing: 0.04em; }
.mermaid-wrap { background: #f9fafb; padding: 12px; border-radius: 6px; }
```

JS init:

```javascript
if (typeof mermaid !== 'undefined') {
  try { mermaid.initialize({ startOnLoad: true, theme: 'default' }); }
  catch (e) { console.error('mermaid init failed', e); }
}
```

발동: 의존 sequence (A → B → C) 가 *명확* + 시각화 가치 있을 때 한정 박제. 단순 list 로 갈음 가능 시 list 만 박제 (grace degradation).
