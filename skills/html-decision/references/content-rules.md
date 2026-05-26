# Content Rules

결정점 / 옵션 / 권장 / Pros/Cons / 💡 왜 / 배경 / 영향 / flow / chunk / action title 의 **편집적 content 룰**. 구조 / CSS / JS = `scripts/template.html` + `scripts/render.py` 가 담당.

★ 모든 case (N=0, 1, 2+) 동일 layout. 결정점 N=0 도 가능 (설명용 문서).

---

## 목차
- §1 **action title** 룰 (h1 / question.title 의무)
- §2 **chunk 룰** (paragraph / 문장 / bullet / list 길이)
- §3 결정점 분해 룰
- §4 옵션 작성 룰 + 권장 옵션 mark
- §5 Pros / Cons / 예시 작성 (split card + weighted bar)
- §6 💡 왜 이 결정 필요 (`question.why`) — 모든 Q 의무
- §7 배경 카드 (`background`) — 본문 위 영역
- §8 **flow** 작성 룰 — 전역 흐름 (옵션)
- §9 영향 영역 (`impact`) — Q 안 collapse
- §10 confidence indicator (`option.confidence`)
- §11 matrix_summary — 옵션 비교 matrix 데이터
- §12 option.status — 1단어 + icon
- §13 question.tags — framework / 분류 chip
- §14 callout 종류 분류 룰
- §15 vague 고민 처리

---

## 1. action title — 결론형 제목 의무

`h1` (문서 전체) + 각 `question.title` 모두 **결론형**. 토픽형 X.

### 1.1 룰

- **≤15 단어 / 2줄 이내** (한글 약 35-40자)
- **active voice**
- **결론 + 핵심 근거** 한 줄
- "고민 중", "검토", "선택해야" 같은 verb 금지
- "and" 가 들어가면 분해 검토 (한 Q 에 두 결정)

### 1.2 예시

| ❌ 토픽형 | ✅ 결론형 |
|---|---|
| `Q1. DB 인덱싱 방식은?` | `Q1. Composite index 채택 — 단일 컬럼 대비 90% 빠른 lookup` |
| `Q2. 캐시 전략?` | `Q2. Redis 도입 — 읽기 80% 비중에서 Hit ratio 70%+ 기대` |
| `Q3. API 인증 방법` | `Q3. JWT 채택 — stateless + 모바일 client 호환` |
| `H1: PoC 결과 분석` | `H1: PoC 결과: latency p99 350ms — SLA (200ms) 미달` |

### 1.3 N=0 (설명용 문서)

결정 없이 분석/공유용 — `h1` = **결론** 또는 **핵심 발견** 박제.

```
✅ "PoC 결과: latency p99 350ms — SLA 미달 (200ms)"
❌ "PoC 결과 분석"
```

---

## 2. chunk 룰 — 줄글 분해

JSON spec 안 모든 텍스트 (background.bullets / question.why / option.detail.pros 등) 에 적용.

### 2.1 길이 임계

| 단위 | 권장 |
|---|---|
| paragraph | **2-4 문장**, 한글 80-150자 |
| 한 문장 | 한글 **35-50자 이하** |
| bullet 한 줄 | **8 단어 이내** (한글 약 15-25자) |
| list 길이 | **3-7개**. 7개+ → sub-grouping |
| heading | h2 → h3 까지만. h4+ 자제 |

### 2.2 분해 트리거

| 신호 | 처리 |
|---|---|
| "그리고 / 또한" 2회+ | bullet 으로 분해 |
| 같은 추상 수준 항목 3+ | 무조건 list |
| 비교 / 대조 | 무조건 table (옵션 비교 matrix) |
| 시간 / 단계 / 순서 | numbered list 또는 flow Mermaid |
| 한 paragraph 가 4문장 초과 | 분해 |

### 2.3 한국어 가독성

template.html 안 CSS 가 처리 (Pretendard + line-height 1.7 + word-break keep-all + 자간 -0.01em). 작성자는 **문장 길이만 통제**.

---

## 3. 결정점 분해 룰

- **독립 분해**: A 와 B 가 독립이면 별도 Q 분리
- **의존 sequence 인식**: A 결정이 B 의 input 이면 A 가 선행 (순서 의미)
- **옵션 수**: max 5 + 기타 (1). 사용자 인지 부담 최소화
- **N=0 허용**: 결정점 없이 *설명용 문서* 도 가능. 동일 layout 박제

---

## 4. 옵션 작성 룰

| 필드 | 내용 |
|---|---|
| `value` | slug (kebab-case). 예: `"composite"`, `"covering"` |
| `label` | 사용자에게 보이는 옵션 설명. HTML 허용 (`<code>`, `<strong>` 등) |
| `recommended` | `true` 1건만. Claude 가 권장 가능한 경우 한정 |
| `reason` | 1줄 이유 (권장 옵션 의무) |
| `confidence` | 1-5 (●●●●○). 권장 옵션 의무 |
| `matrix_summary` | `{cost_level, risk_level}` — 옵션 비교 matrix 활용 |
| `status` | 1단어 + icon ("✓ 정합" / "⚠️ violation" / "⚡ boundary") |
| `detail` | `{pros, cons, example?}` — split card + weighted bar |

★ "기타 (직접 입력)" 옵션 = render.py 자동 박제. JSON 안 명시 X.

---

## 5. Pros / Cons / 예시 (split card + weighted bar)

`detail: { pros, cons, example? }` — **list of strings 우선**. weighted bar 자동 계산용.

### 5.1 형식

- `pros` / `cons` = **list of strings** (각 항목 = bullet) 또는 단일 string
- `example` = 구체 예시 (수치 / file / code / 결과). 가능 시 박제
- 카드 안 visual = ✅ (Pros) / ⚠️ (Cons) / 📌 (예시) icon
- 좌=Pros (녹색) / 우=Cons (빨강) split

### 5.2 weighted bar (자동 계산)

`detail.pros` 항목 수 vs `detail.cons` 항목 수 비율 → render.py 가 상단 막대 자동 박제. 예: pros 4건 / cons 2건 → `Pros 67% / Cons 33%`.

→ 즉 **list 의 항목 수 = 가중치**. 핵심 pros 1건 + 부수 cons 3건 박제 시 의도와 반대 인상 줄 수 있음. **항목 수 = 가중치** 의식 작성.

### 5.3 작성 가이드

| 영역 | 의도 |
|---|---|
| `pros` 항목 수 | 3-5 권장. 1건이 핵심이라면 1건도 OK |
| `cons` 항목 수 | 2-3 권장 |
| 항목 길이 | 1줄 (한글 35-50자) 권장. 너무 길면 chunking (§2) |
| `example` | 1 항목 (멀티라인 OK) |

### 5.4 생략 허용

- 단순 binary / 명확한 차이 시 detail 생략 가능 (옵션 비교 matrix 만으로 충분)
- 단 권장 옵션 = `detail.pros + cons` 의무 (사용자가 *왜 권장* 인지 알기 위해)

---

## 6. 💡 왜 이 결정 필요 (`question.why`) — 모든 Q 의무

각 결정점의 *근거 + 맥락* 1-3 문장. callout-tip 박스 안 박제.

### 6.1 의도

- 사용자가 *Q 만 보고* 결정 가능하도록 *근거 명시*
- *왜 이 결정이 필요한지* + *어떤 frame 으로 옵션 평가하는지*
- 형식 = string 또는 list of strings (multi-paragraph)

### 6.2 좋은 예시

```json
"why": "ADR-04 = 5축 모두 yes. Workflow 패턴 채택 = 임의 판단 영역 X. framework §5.1 Axis 1 = HITL-in-flight 의무."
```

### 6.3 나쁜 예시

```json
"why": "결정 필요."     // 너무 짧음
"why": ""               // 빈 박제 (의무 위반)
```

---

## 7. 배경 카드 (`background`) — 본문 위 영역

본문 상단 `id="bg"` *항상 박제*. **bg-card-stack 구조** (v0.8.0) — TL;DR + KPI stat-tile + 카테고리 callout + chip + 자세히 collapse.

### 7.1 구조 (모두 optional — Claude 자율 박제)

```json
"background": {
  "tldr": "<1줄 thesis>",
  "kpis": [{"num": "20", "lbl": "decisions", "sub": "confirmed"}, ...],
  "findings": {"title": "🔍 발견", "bullets": [...]},
  "root_causes": {"title": "🚨 root cause", "items": [...]},
  "solution": {"title": "💡 해결 방향", "body": "..."},
  "risk": {"title": "⚠️ risk", "body": "..."},
  "principles": {"groups": [{"label": "...", "chips": [...]}]},
  "detail": "<자세히 collapse 안 HTML>"
}
```

★ 7 영역 모두 *optional*. 정보량 따라 Claude 가 자율 박제. 미박제 영역 = 안 보임.

### 7.2 영역별 가이드

#### 7.2.1 `tldr` — TL;DR hero
- **1-2 문장**, 한글 80-120자
- **결론 + 핵심 근거** (Action title 룰 §1 와 동일)
- HTML 허용 (`<strong>` 으로 핵심 단어 강조)
- 예: `"<strong>consolidation paradigm</strong> 채택 — root cause 3종 동시 fix. incremental 만으로 누덕누덕 패치 영구화 risk."`

#### 7.2.2 `kpis` — KPI stat-tile strip
- **3-5 tile 권장** (auto-fit grid, 모바일 stack)
- 줄글 안 *묻힌 숫자* 추출 → tile 격상 (Few/Vercel 패턴)
- `num` = 큰 숫자 (1.85em, accent 색), `lbl` = label (UPPERCASE), `sub` = 1줄 부연
- 예: `{"num": "75%", "lbl": "agent autonomous", "sub": "over-reach signal"}`

#### 7.2.3 `findings` — 🔍 발견 (callout-info)
- 분석 / 조사 결과 / 관찰 bullets
- `bullets` = 2-5 항목. nested `<ul>` 안 sub-bullet 허용
- 핵심 키워드 `<strong>` 강조

#### 7.2.4 `root_causes` — 🚨 root cause (callout-warning, numbered)
- 원인 분석 결과 (3종 ultrathink 패턴)
- `items` = 2-5 항목. **string** 또는 **{label, sub}** 둘 다 가능
- `{label, sub}` = `<strong>label</strong> — sub` 박제

#### 7.2.5 `solution` — 💡 해결 방향 (callout-tip)
- 권장 해결안 1-2 문장
- `body` (string) 또는 `bullets` (list)

#### 7.2.6 `risk` — ⚠️ risk (callout-danger)
- 회피 가능 / 비가역 / 부정적 영향
- `body` (string) 또는 `bullets`

#### 7.2.7 `principles` — 🔒 frozen 원칙 (callout-note + chip)
- 결정 frozen 사항 / 사용자 메타 원칙
- `groups` = list of `{label?, chips}`. 다수 그룹 분리 (label 별 chip 묶음)
- 예: `[{"label": "사용자 요구", "chips": ["원칙1", "원칙2"]}, {"label": "메타", "chips": [...]}]`

### 7.3 박제 판단 (Claude 자율)

| 정보량 | 박제 권장 |
|---|---|
| 결정 thesis 명확 | `tldr` 박제 (가장 prominent) |
| 숫자/KPI 2+ 있음 | `kpis` 박제 (줄글 안 묻힘 방지) |
| 분석 / 관찰 결과 | `findings` |
| 원인 분석 (ultrathink) | `root_causes` |
| 권장 해결안 명확 | `solution` |
| risk 명시 필요 | `risk` |
| 사용자 frozen 원칙 | `principles` |
| 긴 보조 정보 | `detail` (자세히 collapse) |

### 7.4 `detail` (자세히 collapse) — **줄글 wall 절대 금지**

> ⚠️ **Claude 가 가장 자주 위반하는 영역**. *분량 무관* — 200자 이하 detail 도 정보 unit 2+ 면 *반드시* 분해. §7.5 예시 패턴 강제 박제.

긴 보조 정보. **HTML 박제 시 다음 룰 엄격 적용** (위반 시 가독성 심각 저하):

| 트리거 | 처리 |
|---|---|
| 한 paragraph 안 `/` `+` `;` 구분자 3+ | `<ul><li>` 분해 |
| 한 paragraph 안 `→` `=` `vs` 다중 인과 | `<ol>` step 분해 |
| 한 paragraph 안 `(1)(2)(3)` 번호 압축 | `<ol>` 분해 |
| paragraph 3문장 이상 | `</p><p>` 분리 |
| 항목 3+ parallel | `<ul><li>` 분해 |
| 시간 / 단계 순서 | `<ol>` numbered list |
| 같은 카테고리 정보 다수 | `<h4>` sub-heading 분리 |
| 핵심 키워드 | `<strong>` 강조 |

### 7.5 좋은 예시 (detail) — 사용자 case 기반

```json
"detail": "<h4>framework 현재 구성 (16 file)</h4><ul><li><strong>skill body 2</strong> — bdd-to-lld + refine-lld</li><li><strong>reference 5</strong> — architecture / adr-classification / decision-loop / distribution / examples</li><li><strong>agent 4</strong> — drafter + 3 reviewer</li><li><strong>template 4</strong> — lld + task-plan + decisions + backlog</li><li><strong>lld-checklist.json 1</strong></li></ul><h4>consolidation 후 예상 구조</h4><ul><li><strong>skill 2</strong> 그대로</li><li><strong>reference 5 → 3</strong> — architecture-rules / decision-rules 통합 / examples</li><li><strong>agent 4</strong> 그대로 — 단 §1 input contract strict + §N algorithm pseudocode 추가</li><li><strong>template 4</strong> 그대로</li></ul><p><strong>결과:</strong> 14 → 12 file. body line ~50% 감소.</p><h4>5 결정 의존 sequence</h4><ol><li><strong>Q1</strong> — paradigm anchor</li><li><strong>Q2</strong> (input contract) <strong>+ Q3</strong> (body consolidation) — root cause direct fix</li><li><strong>Q4</strong> — PoC violation 처리</li><li><strong>Q5</strong> — commit + work lifecycle</li></ol>"
```

→ ✅ `<h4>` 3개 sub-section 분리 / `<ul>` 5+4 bullet / `<ol>` 4 step / `<strong>` 키워드 강조 / `<p>` 결론 분리

### 7.6 나쁜 예시 (detail) — ❌ 줄글 wall

```json
"detail": "framework 16 file 구성 — skill body 2 (bdd-to-lld + refine-lld) / reference 5 (...) / agent 4 (drafter + 3 reviewer) / template 4 (...) / lld-checklist.json 1.\n\nconsolidation 후 예상 구조 — skill 2 그대로 / reference 5 → 3 (...) / agent 4 그대로 / template 4 그대로. 총 14 → 12 file, body line ~50% 감소.\n\n5 결정 의존 sequence — Q1 paradigm anchor → Q2 (input contract) + Q3 (body consolidation) root cause direct fix → Q4 (PoC violation 처리) → Q5 (commit + work lifecycle)."
```

→ ❌ **금지**. paragraph 안 `/` 4+ inline 압축 / `→` 인과 chain / 시각 분해 X. 사용자가 "가독성 쓰레기" 평가.

### 7.7 다른 영역의 줄글 분해 룰 (§2 chunk 룰 적용)

`background.findings.bullets` / `background.root_causes.items` / `background.detail` 등 **모든 텍스트 영역** 동일:

| 안티패턴 | 변환 |
|---|---|
| `(1)X (2)Y (3)Z` 번호 압축 | `<ol>` 분해 |
| `A / B / C / D` 슬래시 압축 ≥ 3 | `<ul>` 분해 |
| `A + B + C` 더하기 압축 ≥ 3 | `<ul>` 분해 |
| `A → B → C → D` 인과 chain | `<ol>` step 분해 또는 flow Mermaid |
| `A; B; C` 세미콜론 압축 ≥ 3 | `<ul>` 분해 |

### 7.8 v0.7.x 호환 (fallback)

`tldr` / `kpis` / `findings` 등 모두 미박제 + `background.bullets` 만 박제 시 → 단일 callout-info 박제 (v0.7.x 동작). Claude 가 *간단한 배경* 일 때 활용 가능.

---

## 8. flow — 전역 흐름 (옵션)

`flow.mermaid` 박제 시 본문 위 (배경 ↓ 권장 ↑) Mermaid flowchart 박제. 미박제 시 empty state 박제 (sidebar anchor 는 항상).

### 8.1 의도

- **전체 결정 sequence** (Q1 → Q2 → Q3 분기 / 의존)
- **before / after** 상태 흐름
- **데이터 / 시스템 전역 흐름**

→ Q 별 의존은 `question.impact.mermaid` 박제 (§9). flow = 전역.

### 8.2 형식

```json
"flow": {
  "title": "🔄 전체 흐름",
  "mermaid": "flowchart LR\n  A[배경] --> B[Q1] --> C[Q2] --> D[결정 결과]"
}
```

### 8.3 가이드

- 박제 의무 X — 단순 결정 / 단순 흐름은 생략 권장
- Mermaid `flowchart` 권장. 복잡 시 `sequenceDiagram` / `quadrantChart` / `mindmap` 도 가능
- 노드 수 7개 이하 권장 (chunk 룰 §2)
- Mermaid syntax 주의 = §9.3 와 동일

---

## 9. 영향 영역 (`impact`) — Q 안 collapse

각 결정점의 *영향 영역 시각화* — Q 카드 안 collapse `<details>`.

### 9.1 형식

```json
"impact": {
  "areas": [
    "decisions.md ADR-04 status",
    "lld §6.2.batch",
    "..."
  ],
  "mermaid": "<선택. flowchart code>"
}
```

### 9.2 가이드

- `areas` = list. 영향 file / 모듈 / 사람
- `mermaid` = 복잡한 의존 시각화. 단순 list 로 갈음 가능 시 생략
- 추상 영향 = areas 만 / 구체 의존 = Mermaid 추가

### 9.3 ⚠️ Mermaid syntax 주의 (flow / impact 공통)

| 영역 | ❌ 깨짐 | ✅ 정합 |
|---|---|---|
| 노드 label 줄바꿈 | `A[Step 1\nrefs]` | `A[Step 1<br/>refs]` 또는 quoted `A["Step 1<br/>refs"]` |
| dotted arrow label | `A -.text.-> B` | `A -.-> B` (label 제거) |
| 한글 + 공백 label | `A[전 영역 gate]` | `A["전 영역 gate"]` (quoted) |

★ 한글 라벨은 *항상* quote 권장.

---

## 10. confidence indicator (`option.confidence`)

각 옵션의 Claude 확신도 = `confidence: 1-5`. 시각 = `●●●●○`.

| 값 | 시각 | 의미 |
|---|---|---|
| 5 | ●●●●● | 매우 확신 — 강한 컨센서스 / 명확한 best practice |
| 4 | ●●●●○ | 권장 — 다른 옵션 대비 명확 우위 |
| 3 | ●●●○○ | 중립 — 옵션 간 trade-off 큼 |
| 2 | ●●○○○ | 약한 권장 — 다른 옵션 가능성 큼 |
| 1 | ●○○○○ | 권장 보류 — 사용자 영역 |

★ 권장 옵션 의무. 다른 옵션 박제는 선택.

---

## 11. matrix_summary — 옵션 비교 matrix 데이터

각 옵션의 *비교용 등급* = `matrix_summary: {cost_level, risk_level}`. matrix 안 heatmap 셀로 박제.

| 필드 | 값 |
|---|---|
| `cost_level` | `"낮"`, `"중"`, `"높"` 중 한 단어 |
| `risk_level` | `"낮"`, `"중"`, `"높"` 중 한 단어 |

★ 옵션 비교 matrix 박제 시 의무. 셀 = heat-low (녹) / heat-mid (주) / heat-high (빨) 자동.

---

## 12. option.status — 1단어 + icon

각 옵션의 *상태* — 옵션 비교 matrix 안 우측 column.

| 값 (한글 권장) | 의미 | CSS heat |
|---|---|---|
| `"✓ 정합"` | 권장 / 프레임워크 정합 / OK | heat-ok (녹) |
| `"⚠️ 위반"` | 명시 위반 | heat-danger (빨) |
| `"⚠️ 비판 미충족"` | 사용자 비판 미해결 | heat-danger (빨) |
| `"⚡ 경계"` | 경계 사례 / 미해결 영역 | heat-bndry (주) |
| `"⚡ 불일치"` | 일부 불일치 / 과한 설계 | heat-bndry (주) |
| `"⚡ 모호"` | enum / 정의 모호 | heat-bndry (주) |

★ prefix icon (`✓` / `⚠️` / `⚡`) → render.py 가 CSS class 자동 매핑 (텍스트는 영어/한글 무관 동작).
★ 영어 표현 (`violation` / `boundary` / `mismatch`) 도 동작 — 단 §16 한국어 우선 박제 룰에 따라 한글 권장.

---

## 13. question.tags — framework / 분류 chip (옵션)

각 결정점 위 *분류 라벨* — tag chip 박제.

### 13.1 형식

```json
"tags": ["DB", "performance", "MoSCoW: Must", "ADR-04"]
```

### 13.2 의도

- framework 명 (SWOT / MoSCoW / RICE / DACI / ADR 등)
- 분류 (DB / API / UX / infra 등)
- 우선순위 (Must / Should / Could / Won't)
- 참고 ADR 번호

### 13.3 가이드

- 박제 의무 X — 결정점 분류가 *모호* 하면 생략
- 항목 수 **3-5 이내**. 너무 많으면 시각 noise

---

## 14. callout 종류 분류 룰

template.html 안 callout 6종 토큰 박제. content-rules 에서 *어떤 의미를 어떤 callout 으로* 박을지.

| 종류 | 색 | 의미 | 박제 위치 |
|---|---|---|---|
| **info** (파랑) | 부연 / 맥락 보강 | 📋 배경 카드 (자동) |
| **tip** (녹색) | 권장 / 더 나은 방법 / 근거 | 💡 왜 이 결정 (자동) |
| **important** (보라) | 필수 전제 / 빠뜨리면 큰일 | (수동 박제 가능 — bullets 안 strong) |
| **warning** (노랑) | 주의 / 회피 가능한 문제 | (수동 박제 가능) |
| **danger** (빨강) | 위반 / 비가역 위험 | option.status = "⚠️ violation" (자동) |
| **note** (회색) | 단순 메모 / 분류 없음 | example 박스 (자동) |

★ 직접 callout 추가는 v0.7.0 에서 *automated mapping* 만 지원. 향후 `callouts` 필드 박제 시 확장 가능.

---

## 15. vague 고민 처리

- 명확치 않은 고민 = best-guess 다중 해석 옵션 + 기타 (자동 박제) 활용
- 한 cycle 안 자체 해결 — HTML 결과로 즉시 응답
- N=0 (설명용 문서) 도 가능 — 결정점 없이 배경 카드 / flow 만으로 공유 가능

---

## 16. 한국어 우선 박제 — 영어 / 한글 혼용 룰

> ⚠️ **Claude 가 가장 자주 위반하는 영역 2**. 한국 IT 기업 실측 영어 비율 = **12-20%**. 30%+ = 부자연. Claude 가 `consolidation paradigm`, `incremental fix`, `root cause 3종` 같은 표현 박제 시 **반드시 한글로 변환**.

### 16.1 영어 보존 카테고리 (✅ 한글 변환 금지)

| 카테고리 | 예시 |
|---|---|
| **표준 약어** | `API` `SDK` `JWT` `JSON` `HTTP` `OAuth` `MSA` `DDD` `OCP` `KPI` `CTR` `URL` |
| **고유명사 / 제품** | `Claude` `GitHub` `Kafka` `Redis` `PostgreSQL` `Mermaid` `Notion` `Confluence` `JIRA` |
| **패턴명** | `Facade` `Hexagonal` `Strangler Fig` `Layered Architecture` `Clean Architecture` `Feature Toggle` |
| **코드 entity** | `drafter` `reviewer` `agent` `port` `adapter` `handler` (코드에 실제 존재) |
| **신조 기술 용어** | `LLM` `RAG` `MCP` `prompt caching` `tool use` |
| **수치 단위** | `ms` `KB` `MB` `p99` `QPS` `RPS` `%` |
| **언어 / 포맷** | `Java` `Python` `Go` `gRPC` `HTML` `Markdown` `YAML` |

### 16.2 한글 변환 카테고리 (🔄 영어로 박제 금지)

| 카테고리 | 예시 |
|---|---|
| **일반 동사** | fix → 수정, validate → 검증, deploy → 배포, choose/select → 선택/채택 |
| **추상 명사** | paradigm → 방식, consolidation → 통합, boundary → 경계, scope → 범위 |
| **결정 어휘 (의무)** | chosen → 채택, rejected → 기각, valid → 유효, invalid → 무효 |
| **원인-결과 어휘** | root cause → 근본 원인, mitigation → 완화, consequence → 결과 |
| **형용사** | incremental → 점진적, strict → 엄격, robust → 견고, stable → 안정 |

### 16.3 외래어 정착 한글 표기 (🔵 한글 외래어로 박제)

- **그대로 한글**: 커밋 / 머지 / 리팩토링 / 마이그레이션 / 디버깅 / 모니터링 / 캐시 / 프레임워크 / 스코프 / 엣지 케이스 / 폴백 / 피처 플래그 / 트레이드오프

### 16.4 ❌ Claude 자주 박는 부자연 표현 → 변환 의무

한국 IT 기업 블로그 18편 분석 결과 **0건** 발견되는 표현들. Claude 가 박으면 *반드시* 한글 변환:

| ❌ Claude 가 박는 형태 | ✅ 한글 변환 |
|---|---|
| `consolidation paradigm` | 통합 방식 |
| `incremental fix` | 점진적 수정 |
| `root cause 3종` | 근본 원인 3가지 |
| `boundary case` | 경계 사례 |
| `valid / invalid` 단독 | 유효 / 무효 |
| `chosen / rejected` 단독 | 채택 / 기각 |
| `input contract` | 입력 명세 |
| `strict whitelist` | 엄격한 허용 목록 |
| `validity` | 정합성 / 유효성 |
| `mismatch` | 불일치 |
| `trade-off analysis` | 장단점 분석 |
| `failure mode` | 실패 양상 |
| `single point of failure` | 단일 장애점 (SPOF) |
| `hypothesis fixation` | 가설 고착 |
| `local optimization` | 국소 최적화 |
| `breaking change` | 호환성 깨짐 |
| `dual writing` | 이중 쓰기 |

### 16.5 첫 등장 병기 룰

생소한 약어 / 영문 용어는 **첫 등장 시** 한글-영문 병기, **이후** 단일 표기.

| 형식 | 예시 |
|---|---|
| `한글(English)` | `근본 원인(root cause)`, `프레임워크(framework)` |
| `English(약어 풀이)` | `ADR(Architecture Decision Record)`, `SDK(Software Development Kit)` |
| 약어 단독 (정착) | `API`, `JWT`, `JSON` — 풀이 불필요 |

★ *두 번째* 등장부터는 *단일 표기*. 매번 병기 X.

### 16.6 변환 사전 (참조)

| English | 한글 |
|---|---|
| approach | 접근 / 접근법 |
| adopt | 도입 / 채택 |
| analysis | 분석 |
| assumption | 가정 / 전제 |
| breaking change | 호환성 깨짐 |
| chosen | 채택 |
| compatibility | 호환성 |
| complexity | 복잡도 |
| consequence | 결과 / 영향 |
| consider | 검토 / 고려 |
| consolidation | 통합 |
| context | 배경 / 맥락 |
| constraint | 제약 |
| cons | 단점 |
| criteria | 기준 |
| decision | 결정 |
| deferred | 보류 |
| deploy | 배포 |
| extensibility | 확장성 |
| fix | 수정 |
| flexibility | 유연성 |
| improvement | 개선 |
| input | 입력 |
| invalid | 무효 / 잘못된 |
| mitigation | 완화 |
| paradigm | 방식 / 접근법 |
| performance | 성능 |
| pros | 장점 |
| proposed | 제안 |
| rationale | 근거 |
| recovery | 복구 |
| rejected | 기각 / 제외 |
| reliability | 신뢰성 |
| review | 검토 / 리뷰 |
| risk | 위험 |
| root cause | 근본 원인 |
| scalability | 확장성 |
| scope | 범위 |
| solution | 해결안 / 해결책 |
| stability | 안정성 |
| strict | 엄격 |
| symptom | 증상 |
| trade-off | 트레이드오프 / 상충 관계 |
| validate | 검증 |
| validity | 정합성 / 유효성 |
| valid | 유효 |
| workaround | 우회 방안 |

### 16.7 영어 비율 목표

- **전체 단어 중 영어 비율 ≤ 20%** 목표 (한국 IT 기업 실측 평균)
- 결정 캔버스는 *공유 목적* 이므로 ≤ 15% 권장
- 코드 영역 (백틱 `<code>` 안) 은 비율 측정 제외
