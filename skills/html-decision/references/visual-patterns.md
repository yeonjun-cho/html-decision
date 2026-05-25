# Visual Patterns

언제 어떤 시각 패턴을 박제할지 — Claude 가 JSON spec 작성 시 *자율 판단* 기준. progressive disclosure: SKILL.md 흐름이 막힐 때만 참조.

★ 사용자 액션 0. Claude 가 spec 안 *값을 넣을지 말지* 자율 결정 → render.py 가 자동 박제.

---

## 1. N별 권장 시각 (옵션 비교)

| N | 1차 시각 | 보조 |
|---|---|---|
| **N=0 (설명용)** | 배경 카드 + flow Mermaid (전체 흐름) | dashboard empty state 자동 |
| **N=1** | 권장 mini + Pros/Cons split + weighted bar | 옵션 비교 matrix 1행 |
| **N=2 (A vs B)** | matrix (2행) + split card 양쪽 | flow Mermaid (선택) |
| **N=3-5 (표준)** | matrix + heatmap 셀 + split card | flow Mermaid (sequence 분기 있을 때) |
| **N=5+ (heavy)** | matrix (heatmap 강조) + 권장 dashboard | flow Mermaid (필수에 가까움) |

★ 옵션 비교 matrix + split card 는 render.py 가 자동. Claude = JSON spec 안 *값* 만 박제.

---

## 2. flow Mermaid — 박제 판단 기준

`flow.mermaid` 박제 = **본문 위 전역 flowchart**. 박제 의무 X.

### 박제 권장 (Claude 가 자율 판단)

| 신호 | 예시 |
|---|---|
| 결정점 간 *의존* | Q1 결과 가 Q2 의 input |
| 결정점 ≥ 3 | 사용자가 sequence 파악 필요 |
| before / after 변화 | 마이그레이션 / refactor |
| 데이터 / 시스템 전역 흐름 | API → service → DB pipeline |
| 분기 결정 (Y/N) | Decision tree |

### 박제 X 권장

| 신호 | 사유 |
|---|---|
| N=1 + 의존 X | 단일 결정 — flow 불필요 |
| 옵션 간 *trade-off* 만 | 비교 matrix 가 우월 |
| 추상 / 모호한 흐름 | 시각 noise |

### 형식 예시

```json
"flow": {
  "title": "🔄 전체 흐름",
  "mermaid": "flowchart LR\n  A[현재 상태] --> B{Q1. DB 선택}\n  B -->|composite| C[Q2. 캐시 전략]\n  B -->|covering| D[추가 검토]\n  C --> E[배포]"
}
```

---

## 3. impact.mermaid — Q 별 의존

`question.impact.mermaid` = **Q 카드 안** 영향 영역 collapse Mermaid. 박제 의무 X.

### 박제 권장

| 신호 | 예시 |
|---|---|
| 영향 file / 모듈 ≥ 4 | 의존 관계 시각 |
| 결정이 *연쇄* 영향 | A 결정 → B 모듈 변경 → C 인터페이스 변경 |
| 복잡 graph | swimlane / call graph |

### 박제 X 권장

| 신호 | 사유 |
|---|---|
| 영향 file 1-3 | `impact.areas` list 만으로 충분 |
| 추상 영향 (사람 / 정책) | list 형식 적합 |

### 형식 예시

```json
"impact": {
  "areas": ["orders 테이블", "checkout flow", "report 쿼리"],
  "mermaid": "flowchart TD\n  A[orders 테이블] --> B[checkout flow]\n  A --> C[report 쿼리]"
}
```

---

## 4. tags — chip 박제 판단

`question.tags` = 분류 chip. 박제 의무 X.

### 박제 권장

| 종류 | 예시 |
|---|---|
| framework | `"DACI"`, `"MoSCoW: Must"`, `"RICE"`, `"SWOT"` |
| 분류 | `"DB"`, `"API"`, `"UX"`, `"infra"`, `"performance"` |
| 우선순위 | `"P0"`, `"Must"`, `"Should"` |
| 참고 | `"ADR-04"`, `"RFC-2"` |

### 박제 X 권장

- 분류가 *모호* 한 단순 결정
- 한 결정에 tag 6+ 박제 → 시각 noise. 3-5 이내.

---

## 5. Pros/Cons weighted bar — 항목 수 = 가중치 인식

`detail.pros` / `detail.cons` 가 list 일 때 render.py 가 *항목 수* 기반 weighted bar 자동 박제. 즉 **항목 수 = 가중치**.

### 작성 시 주의

| 의도 | 박제 |
|---|---|
| pros 압도적 우위 | pros 4-5건 + cons 1-2건 |
| 균형 trade-off | pros 3건 + cons 3건 |
| cons 압도 (권장 보류 등) | pros 1건 + cons 3-5건 |

### 안티패턴

- pros 1건 (핵심) + cons 3건 (부수적) 박제 → weighted bar = "Pros 25% / Cons 75%" → 권장 옵션인데 의도와 반대 인상

→ **핵심 / 부수 무관, 항목 수 자체가 가중치 의미**. 핵심 pros 1건 + 부수 pros 2-3건 추가하여 정렬.

---

## 6. confidence 박제 기준

| 값 | 시각 | 의미 |
|---|---|---|
| 5 | ●●●●● | 매우 확신 — 명확한 best practice |
| 4 | ●●●●○ | 권장 — 명확 우위 |
| 3 | ●●●○○ | 중립 — trade-off 큼 |
| 2 | ●●○○○ | 약한 권장 |
| 1 | ●○○○○ | 권장 보류 — 사용자 영역 |

★ 권장 옵션 의무. 다른 옵션 박제는 선택.

---

## 7. callout 자동 매핑 (render.py 처리)

| 영역 | 자동 박제 callout |
|---|---|
| 📋 배경 카드 | callout-info (파랑) |
| 💡 왜 이 결정 | callout-tip (녹색) |
| 🎯 권장 mini-card | callout-tip 변종 (rec green) |
| 옵션 예시 | callout-note (회색) |
| 영향 영역 | callout-info 변종 (border-left) |

★ 직접 callout 박제는 v0.7.0 에서 미지원. 텍스트 안 `<strong>` 강조로 갈음.

---

## 8. 결정 *진행 중* vs 결정 *결과 기록*

`html-decision` 컨셉 = Claude 대화 안 결정 *진행 중* 시각화. ADR (결정 결과 기록) 과 다름:

| 영역 | html-decision | ADR / MADR |
|---|---|---|
| 시점 | 결정 *전* | 결정 *후* |
| 입력 | Claude 가 옵션 도출 | 사람이 결정 박제 |
| lifetime | 한 cycle (대화 → HTML → 결과) | 영구 (PR/docs commit) |
| 무게 | 가벼움 (한눈 비교) | 무거움 (정형 + 변경 이력) |
| 시각 우선순위 | 시각 = 70% | 텍스트 = 70% |

→ ADR 패턴 (Context / Decision / Status / Consequences 정형) 은 *참고만*. 직접 적용 X.

---

## 9. 시각 우선순위 — pre-attentive

| 위계 | 박제 방식 |
|---|---|
| 1순위 (즉시 인식) | action title h1/h2 + 권장 mini-card 색 강조 |
| 2순위 (스캔 시) | 옵션 비교 matrix heatmap 셀 + dashboard 표 |
| 3순위 (필요 시 펼침) | 옵션 detail collapse (split card) + 영향 영역 collapse |

★ Claude 가 spec 작성 시 *결론* 을 항상 1순위 위치 (h1 / question.title) 에 박제. content-rules.md §1 action title 룰.
