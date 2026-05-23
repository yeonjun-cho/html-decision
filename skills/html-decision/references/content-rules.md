# Content Rules

결정점 / 옵션 / 권장 / Pros/Cons / 💡 왜 / 배경 / 영향 의 **편집적 content 룰**. 구조 / CSS / JS = `scripts/template.html` + `scripts/render.py` 가 담당.

★ 모든 case (N=0, 1, 2+) 동일 layout. 결정점 N=0 도 가능 (설명용 문서).

---

## 목차
- §1 결정점 분해 룰
- §2 옵션 작성 룰 + 권장 옵션 mark
- §3 Pros / Cons / 예시 작성 가이드 (option detail 카드)
- §4 💡 왜 이 결정 필요 (`question.why`) — 모든 Q 의무
- §5 배경 카드 (`background`) — 본문 위 영역
- §6 영향 영역 (`impact`) — Q 안 collapse
- §7 confidence indicator (`option.confidence`)
- §8 matrix_summary — 옵션 비교 표 데이터
- §9 option.status — 1단어 + icon 상태
- §10 vague 고민 처리

---

## 1. 결정점 분해 룰

- **독립 분해**: A 와 B 가 독립이면 별도 Q 분리
- **의존 sequence 인식**: A 결정이 B 의 input 이면 A 가 선행 (순서 의미)
- **옵션 수**: max 5 + 기타 (1). 사용자 인지 부담 최소화
- **N=0 허용**: 결정점 없이 *설명용 문서* 도 가능. 동일 layout 박제

---

## 2. 옵션 작성 룰

| 필드 | 내용 |
|---|---|
| `value` | slug (kebab-case). 예: `"single"`, `"hitl-response"` |
| `label` | 사용자에게 보이는 옵션 설명. HTML 허용 (`<code>`, `<strong>` 등) |
| `recommended` | `true` 1건만. Claude 가 권장 가능한 경우 한정 |
| `reason` | 1줄 이유 (권장 옵션 의무) |
| `confidence` | 1-5 (●●●●○). 권장 옵션 의무 |
| `matrix_summary` | `{cost_level, risk_level}` — 옵션 비교 표 활용 |
| `status` | 1단어 + icon ("✓ 정합" / "⚠️ violation" / "⚡ boundary") — 옵션 비교 표 안 박제 |
| `detail` | `{pros, cons, example?}` — option detail 카드 |

★ "기타 (직접 입력)" 옵션 = render.py 자동 박제. JSON 안 명시 X.

---

## 3. Pros / Cons / 예시 작성 가이드 (option detail 카드)

`detail: { pros, cons, example? }` — 옵션 detail collapse 안 카드 형식으로 박제.

### 3.1 형식

- `pros` / `cons` = **list of strings** (각 항목 = 카드 안 한 bullet 으로 박제) 또는 단일 string
- `example` = 구체 예시 (수치 / file / code / 결과). 가능 시 박제
- 카드 안 visual = ✅ (Pros) / ⚠️ (Cons) / 📌 (예시) icon + bullet 형식
- 권장 옵션 카드 = 녹색 강조

### 3.2 작성 가이드

| 영역 | 의도 |
|---|---|
| `pros` 항목 수 | 3-5 권장. 1건이 핵심이라면 1건도 OK |
| `cons` 항목 수 | 2-3 권장 |
| 항목 길이 | 1줄 (60-80 char) 권장. 너무 길면 chunking |
| `example` | 1 항목 (멀티라인 OK) |

### 3.3 생략 허용

- 단순 binary / 명확한 차이 시 detail 생략 가능 (옵션 비교 표 만으로 충분)
- 단 권장 옵션 = `detail.pros + cons` 의무 (사용자가 *왜 권장* 인지 알기 위해)

---

## 4. 💡 왜 이 결정 필요 (`question.why`) — 모든 Q 의무

각 결정점의 *근거 + 맥락* 1-3 문장. highlight box 안 prominent 박제.

### 4.1 의도

- 사용자가 *Q 만 보고* 결정 가능하도록 *근거 명시*
- *왜 이 결정이 필요한지* + *어떤 frame 으로 옵션 평가하는지* 박제
- 형식 = string 또는 list of strings (multi-paragraph)

### 4.2 좋은 예시

```json
"why": "ADR-04 = 5축 모두 yes (도메인 + NFR + Dependencies + Interfaces + Construction). Workflow 패턴 채택 = 임의 판단 영역 X. framework §5.1 Axis 1 = HITL-in-flight 의무."
```

### 4.3 나쁜 예시

```json
"why": "결정 필요."     // 너무 짧음
"why": ""               // 빈 박제 (의무 위반)
```

---

## 5. 배경 카드 (`background`) — 본문 위 영역

본문 상단 *항상 visible* 박제. 분석 요약 + (선택) "자세히" collapse.

### 5.1 형식

```json
"background": {
  "title": "📋 배경 — 분석 요약",   // 선택. default = "📋 배경 — 분석 요약"
  "bullets": [
    "context bullet 1",
    "<strong>강조</strong> 영역",
    "기타 ..."
  ],
  "detail": "자세히 안 펼침 콘텐츠 (선택)"
}
```

### 5.2 가이드

- `bullets` 항목 수 = 3-6 권장
- 각 bullet 짧게 (1줄 권장, 멀티라인 X)
- HTML 허용 (`<strong>`, `<code>` 등)
- `detail` = 긴 보조 정보 (사용자 *필요 시* 펼침)

---

## 6. 영향 영역 (`impact`) — Q 안 collapse

각 결정점의 *영향 영역 시각화* — Q 카드 안 collapse `<details>`.

### 6.1 형식

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

### 6.2 가이드

- `areas` = list. 영향 file / 모듈 / 사람
- `mermaid` = 복잡한 의존 시각화. 단순 list 로 갈음 가능 시 생략
- 추상 영향 = areas 만 / 구체 의존 = Mermaid 추가

### 6.3 ⚠️ Mermaid syntax 주의

| 영역 | ❌ 깨짐 | ✅ 정합 |
|---|---|---|
| 노드 label 줄바꿈 | `A[Step 1\nrefs]` | `A[Step 1<br/>refs]` 또는 quoted `A["Step 1<br/>refs"]` |
| dotted arrow label | `A -.text.-> B` | `A -.-> B` (label 제거) |
| 한글 + 공백 label | `A[전 영역 gate]` | `A["전 영역 gate"]` (quoted) |

---

## 7. confidence indicator (`option.confidence`)

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

## 8. matrix_summary — 옵션 비교 표 데이터

각 옵션의 *비교용 등급* = `matrix_summary: {cost_level, risk_level}`. 옵션 비교 표 안 박제.

| 필드 | 값 |
|---|---|
| `cost_level` | `"낮"`, `"중"`, `"높"` 중 한 단어 |
| `risk_level` | `"낮"`, `"중"`, `"높"` 중 한 단어 |

★ 옵션 비교 표 박제 시 의무. 표 안 색상 badge (녹/주/빨) 자동 적용.

---

## 9. option.status — 1단어 + icon

각 옵션의 *상태* — 옵션 비교 표 안 우측 column.

| 값 | 의미 | CSS |
|---|---|---|
| `"✓ 정합"` | 권장 / framework 정합 / OK | 녹색 |
| `"⚠️ violation"` | 명시 위반 | 빨강 |
| `"⚠️ 비판 미충족"` | 사용자 비판 미해결 | 빨강 |
| `"⚡ boundary"` | boundary case / 미해결 영역 | 주황 |
| `"⚡ mismatch"` | 일부 mismatch / over-engineer | 주황 |
| `"⚡ 모호"` | enum / 정의 모호 | 주황 |

★ prefix icon (`✓` / `⚠️` / `⚡`) → render.py 가 CSS class 자동 매핑. 1단어 키워드 추가 (예: "✓ 정합", "⚡ boundary").

---

## 10. vague 고민 처리

- 명확치 않은 고민 = best-guess 다중 해석 옵션 + 기타 (자동 박제) 활용
- 한 cycle 안 자체 해결 — HTML 결과로 즉시 응답
- N=0 (설명용 문서) 도 가능 — 결정점 없이 배경 카드 만으로 공유 가능
