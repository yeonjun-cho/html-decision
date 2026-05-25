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

본문 상단 callout-info 박스 (id="bg") *항상 박제*. 분석 요약 + (선택) "자세히" collapse.

### 7.1 형식

```json
"background": {
  "title": "📋 배경 — 분석 요약",
  "bullets": [
    "context bullet 1",
    "<strong>강조</strong> 영역",
    "기타 ..."
  ],
  "detail": "자세히 안 펼침 콘텐츠 (선택)"
}
```

### 7.2 가이드

- `bullets` 항목 수 = **3-6 권장** (§2 list 길이)
- 각 bullet 짧게 (한글 35자 이하 권장)
- HTML 허용 (`<strong>`, `<code>` 등)
- `detail` = 긴 보조 정보 (사용자 *필요 시* 펼침)

### 7.3 background.detail 작성 룰 — 줄글 wall 금지

`detail` 안 줄글 wall 박제 시 가독성 심각 저하. **chunk 룰 (§2) 엄격 적용**:

- 줄글 paragraph ≥ 3문장 = `<br>` 두 번 또는 paragraph 분리 (`</p><p>`)
- 항목 3+ = `<ul><li>...</li></ul>` bullet 으로 분해
- 핵심 키워드 = `<strong>` 강조
- 모든 정보 한 paragraph 박제 X — *호흡 단위* 분해

### 7.4 좋은 예시

```json
"detail": "<p><strong>현재 상태:</strong> latency p99 350ms, SLA 200ms 미달.</p><ul><li>읽기 80% (multi-column where)</li><li>쓰기 20% (단일 row insert)</li></ul><p><strong>제약:</strong> downtime 1분 이내, rollback 가능.</p>"
```

### 7.5 나쁜 예시

```json
"detail": "현재 상태는 latency p99 가 350ms 로 SLA 200ms 를 미달하고 있고 읽기 비율이 80% 이며 multi-column where 절을 사용하고 쓰기는 20% 이고 단일 row insert 이며 제약은 downtime 1분 이내 rollback 가능 등이 있습니다."
```
→ 줄글 wall. *읽기 힘듦*.

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

| 값 | 의미 | CSS heat |
|---|---|---|
| `"✓ 정합"` | 권장 / framework 정합 / OK | heat-ok (녹) |
| `"⚠️ violation"` | 명시 위반 | heat-danger (빨) |
| `"⚠️ 비판 미충족"` | 사용자 비판 미해결 | heat-danger (빨) |
| `"⚡ boundary"` | boundary case / 미해결 영역 | heat-bndry (주) |
| `"⚡ mismatch"` | 일부 mismatch / over-engineer | heat-bndry (주) |
| `"⚡ 모호"` | enum / 정의 모호 | heat-bndry (주) |

★ prefix icon (`✓` / `⚠️` / `⚡`) → render.py 가 CSS class 자동 매핑.

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
