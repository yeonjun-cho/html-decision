# Widgets & Visualizations

**T3 (결정점 8+) 전용**. T1/T2 는 읽지 말 것.

phase grouping + advanced widget (slider/sortable/toggle) + 시각화 (Mermaid/Chart.js) + sticky sidebar + localStorage 복원.

---

## 1. widget matrix (결정 성격 별)

| 결정 성격 | widget | MD 출력 |
|---|---|---|
| 단일 답 | radio + 기타 + 코멘트 | `**답**: {단일}` |
| 다중 답 | checkbox + 기타 + 코멘트 | `**답**:\n- ...` list |
| 정량 평가 (확신도/위험도) | slider (range) + 코멘트 | `**답**: 7/10` |
| binary on/off | toggle + 코멘트 | `**답**: on` |
| 순서 / 우선순위 | drag (Sortable.js) | `**답**:\n1. ...\n2. ...` |
| 조건부 follow-up | multi-step reveal | 답 + 후속 결정 |
| 자유 텍스트 | textarea only | `**답**: {자유}` |

코멘트 = 옵션/값 선택 시 reveal. "기타" 또는 미선택 = hide.

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

## 3. toggle (binary)

```html
<label class="toggle">
  <input type="checkbox" name="q1" data-toggle>
  <span class="toggle-track"><span class="toggle-thumb"></span></span>
  <span class="toggle-label">on / off</span>
</label>
```

CSS:
```css
.toggle { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; }
.toggle input { display: none; }
.toggle-track { width: 38px; height: 22px; background: #d1d5db; border-radius: 11px;
                position: relative; transition: background 0.2s; }
.toggle-thumb { width: 18px; height: 18px; background: white; border-radius: 50%;
                position: absolute; top: 2px; left: 2px; transition: left 0.2s; }
.toggle input:checked + .toggle-track { background: var(--accent); }
.toggle input:checked + .toggle-track .toggle-thumb { left: 18px; }
```

---

## 4. priority (Sortable.js)

CDN: `https://cdn.jsdelivr.net/npm/sortablejs@1.15/Sortable.min.js`

```html
<ul class="priority-list" data-qid="q1">
  <li data-value="a">옵션 A</li>
  <li data-value="b">옵션 B</li>
  <li data-value="c">옵션 C</li>
</ul>
```

```javascript
document.querySelectorAll('.priority-list').forEach(list => {
  Sortable.create(list, { animation: 150 });
});
// collectAnswers 안 priority 처리
const priorityList = q.querySelector('.priority-list');
if (priorityList) {
  const order = Array.from(priorityList.children).map(li => li.dataset.value);
  answers[qid] = { ...answers[qid], values: order, type: 'priority' };
}
```

MD 출력:
```markdown
**답** (우선순위):
1. 옵션 A
2. 옵션 B
3. 옵션 C
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

## 6. sticky sidebar + scroll spy (결정점 8+)

```html
<aside class="sidebar">
  <div class="progress">진행: <span id="progress-count">0</span> / <span id="progress-total">N</span></div>
  <nav class="toc">
    <a href="#q1" data-qid="q1">Q1. {짧은 제목}</a>
    <a href="#q2" data-qid="q2">Q2. ...</a>
    <!-- ... -->
  </nav>
</aside>
```

```css
body { display: grid; grid-template-columns: 220px 1fr; gap: 32px;
       max-width: 1180px; }
.sidebar { position: sticky; top: 20px; align-self: start;
           max-height: calc(100vh - 40px); overflow: auto; }
.toc a { display: block; padding: 6px 10px; color: var(--muted);
         text-decoration: none; border-left: 2px solid transparent;
         font-size: 0.88em; }
.toc a.active { color: var(--accent); border-left-color: var(--accent);
                background: #eff6ff; }
@media (max-width: 900px) { body { grid-template-columns: 1fr; }
                            .sidebar { display: none; } }
```

```javascript
// scroll spy
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      document.querySelectorAll('.toc a').forEach(a => a.classList.remove('active'));
      document.querySelector(`.toc a[data-qid="${e.target.dataset.qid}"]`)?.classList.add('active');
    }
  });
}, { rootMargin: '-30% 0px -60% 0px' });
document.querySelectorAll('.question').forEach(q => observer.observe(q));

// progress
function updateProgress() {
  const total = document.querySelectorAll('.question').length;
  const answered = Array.from(document.querySelectorAll('.question')).filter(q => {
    return q.querySelector('input:checked') ||
           (q.querySelector('textarea.other-input')?.value || '').trim();
  }).length;
  document.getElementById('progress-count').textContent = answered;
  document.getElementById('progress-total').textContent = total;
}
document.addEventListener('change', updateProgress);
document.addEventListener('input', updateProgress);
updateProgress();
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

## 8. 시각화 (선택 — 영향 명확 시)

| 영역 | rule |
|---|---|
| 옵션 비교 | `<table>` — 3+ 옵션 시 권장 |
| 흐름 / 결정 cascading | **Mermaid flowchart** (CDN) — 결정 의존 명확 시 |
| 결정 분포 | **Chart.js doughnut/bar** (CDN) — 결정점 5+ 시 |
| 영향 file / scope | inline SVG file tree 또는 list — 3+ file 영향 시 |
| before / after | side-by-side panel |
| 코드 예시 | `<pre><code>` |
| 긴 context | `<details><summary>` 접기 (CSS § html-template) |

CDN:
- Mermaid: `https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js`
- Chart.js: `https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js`

grace degradation: CDN load 실패 시 기본 form 동작 보존 의무.

---

## 9. toggle-all-details 버튼 (details 다중 시)

```javascript
window.addEventListener('load', () => {
  document.querySelectorAll('.question').forEach(q => {
    if (q.querySelectorAll('details').length === 0) return;
    const btn = document.createElement('button');
    btn.className = 'toggle-all-details';
    btn.textContent = '모두 펴기';
    btn.onclick = () => {
      const list = q.querySelectorAll('details');
      const allOpen = Array.from(list).every(d => d.open);
      list.forEach(d => d.open = !allOpen);
      btn.textContent = allOpen ? '모두 펴기' : '모두 접기';
    };
    q.appendChild(btn);
  });
});
```

CSS:
```css
.toggle-all-details { position: absolute; top: 16px; right: 18px;
                      background: transparent; border: 1px solid #d1d5db;
                      color: #4b5563; padding: 4px 10px; font-size: 0.78em;
                      border-radius: 4px; cursor: pointer; font-weight: 500; }
.toggle-all-details:hover { background: #f3f4f6; color: #1f2937; }
```
