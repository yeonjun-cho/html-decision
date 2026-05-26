---
name: html-decision
description: 사용자가 `/html-decision` 슬래시 명령으로 명시 호출 시 동작. Claude 대화 안 결정 포인트를 HTML 결정 캔버스로 시각화 (결정점 → 옵션 → Pros/Cons split → 옵션 비교 matrix → MD 결과 회수). JSON spec 작성 → `scripts/render.py` 가 HTML 렌더링. HTML file 응답 (채팅 = file 경로 + 3-5줄 안내 한정). 결과 = `.claude-history/html-decision/` 안 저장 + SendUserFile 전달. ★ 자동 발동 X — 명시 슬래시 호출만.
argument-hint: <고민 설명>
---

# /html-decision

Claude 대화 안 *결정 포인트* 의 터미널 표현 한계 해소 + 복잡 내용의 시각 공유.

**JSON spec 생성 → render.py 가 HTML 렌더링** (Claude 는 HTML 직접 생성 X — output 토큰 절감).

호출 인자: `$ARGUMENTS` (비어있으면 종료)

★ 결정점 N=0 (설명용 문서) 도 가능 — 동일 layout, 컨텐츠만 다름.

---

## 1. 동작 (5 step)

1. `<고민>` + 현재 세션 context 흡수
2. **결정점 N개 식별** + 각 결정점 구성 (제목 = **결론형 action title**, 왜 필요, 옵션 + 권장 + Pros/Cons + 상태). N=0 가능
3. JSON spec 작성 (§3) — `references/content-rules.md` 참조 (chunk 룰 / action title / callout)
4. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/html-decision/scripts/render.py --output <path>` 호출 (JSON = stdin heredoc)
5. SendUserFile + 짧은 채팅 응답 (§5)

★ ultrathink = 결정점 ≥ 5 또는 strategy 결정 시.

---

## 2. 일관 layout (모든 case 동일 — 본문 6 영역)

모든 N (0, 1, 2+) 에 동일 구조. 차이 = 컨텐츠의 *값* 만.

| 영역 | 위치 | 동작 |
|---|---|---|
| **sidebar** | 좌측 240px | 진행 bar + 목차 (📋 배경 / 🔄 흐름 / 🎯 권장 요약 / Q1~Qn / ✏️ 결과 추출 anchor only) |
| **header** | 본문 상단 | h1 (action title) + meta (날짜·브랜치) |
| **📋 배경 카드** | 본문 (id="bg") | callout-info 스타일. 분석 요약 bullet + "자세히" collapse |
| **🔄 흐름** | 본문 (id="flow") | 전역 sequence / 의존 Mermaid. 미박제 시 empty state ("흐름 시각 없음") |
| **🎯 권장 요약 dashboard** | 본문 (id="rec") | Q × 권장 옵션 × 신뢰도 × 이유 표. N=0 시 empty state |
| **Q 카드 × N** | 본문 | h2 (action title) + tags + 권장 mini + 💡 왜 (callout-tip) + 옵션 비교 matrix + 옵션 detail (split card + weighted bar) + 영향 + 선택 |
| **✏️ 결과 추출** | 본문 하단 (id="submit") | 생성 / 복사 / 초기화 버튼. N=0 시 disabled |

★ Tier 분기 X. 모든 case 동일. 차등 = 컨텐츠 풍부도만 (Pros/Cons 깊이, 영향 영역 명시 등).

---

## 3. JSON spec 구조

```json
{
  "topic": "<주제>",
  "h1": "<action title — 결론형 H1>",
  "date": "YYYY-MM-DD",
  "branch": "<git 브랜치>",
  "meta": "<context 부연>",
  "source_html": "<CWD>/.claude-history/html-decision/<filename>.html",
  "background": {
    "tldr": "<1줄 thesis (큰 폰트 hero, 결론 + 핵심 근거). HTML 허용>",
    "kpis": [
      {"num": "20", "lbl": "decisions", "sub": "confirmed"},
      {"num": "75%", "lbl": "autonomous", "sub": "over-reach"}
    ],
    "findings": {
      "title": "🔍 발견",
      "bullets": ["<bullet 1>", "<bullet 2>"]
    },
    "root_causes": {
      "title": "🚨 root cause",
      "items": [
        {"label": "body 비대화", "sub": "16 file ≈ 3000 line"},
        "agent algorithm 명시 부족"
      ]
    },
    "solution": {
      "title": "💡 해결 방향",
      "body": "<1-2 문장 해결 방향>"
    },
    "risk": {
      "title": "⚠️ risk",
      "body": "<위험 / 회피 가능 / 비가역 risk>"
    },
    "principles": {
      "title": "🔒 frozen 원칙",
      "groups": [
        {"label": "사용자 요구", "chips": ["원칙1", "원칙2"]},
        {"label": "메타 원칙", "chips": ["원칙A", "원칙B"]}
      ]
    },
    "detail": "<h4>section 제목 1</h4><ul><li><strong>키워드</strong> — 부연</li><li><strong>키워드</strong> — 부연</li></ul><h4>section 제목 2</h4><ul><li>...</li></ul><p><strong>결론:</strong> ...</p>"
  },
  "flow": {
    "title": "🔄 전체 흐름",
    "mermaid": "<선택. flowchart code — 전역 sequence / 의존>"
  },
  "questions": [
    {
      "id": "q1",
      "title": "Q1. <결론형 action title> — <핵심 근거 한 줄>",
      "nav_label": "Q1. <짧은 키워드>",
      "desc": "<한 줄 부연>",
      "why": "<💡 왜 이 결정 필요 — 1-3 문장. 결정의 근거·맥락 명시>",
      "tags": ["<프레임워크 / 분류 / 태그 — 한글 우선>", "..."],
      "impact": {
        "areas": ["<file/모듈/사람>", "..."],
        "mermaid": "<선택. Q 별 의존 flowchart>"
      },
      "options": [
        {
          "value": "<slug>",
          "label": "<옵션 label>",
          "recommended": true,
          "reason": "<1줄 이유>",
          "confidence": 4,
          "matrix_summary": {
            "cost_level": "낮|중|높",
            "risk_level": "낮|중|높"
          },
          "status": "✓ 정합 | ⚠️ 위반 | ⚡ 경계",
          "detail": {
            "pros": ["bullet 1", "bullet 2", "..."],
            "cons": ["bullet 1", "..."],
            "example": "<구체 예시>"
          }
        }
      ]
    }
  ]
}
```

### 3.1 신설 / 변경 필드 (v0.8.0)

| 필드 | 위치 | 의미 |
|---|---|---|
| `background.tldr` | background | **1줄 thesis** (gradient hero 박제). 결론 + 핵심 근거 |
| `background.kpis` | background | KPI stat-tile-strip (큰 숫자 + label + sub). 줄글 안 묻힌 숫자 격상 |
| `background.findings` | background | 🔍 발견 callout-info (bullets) |
| `background.root_causes` | background | 🚨 root cause callout-warning (numbered items) |
| `background.solution` | background | 💡 해결 방향 callout-tip |
| `background.risk` | background | ⚠️ risk callout-danger |
| `background.principles` | background | 🔒 frozen 원칙 callout-note + chip groups |
| `background.detail` | background | (기존) 자세히 collapse |
| `flow` | top-level | (v0.7.0) 🔄 전역 흐름 Mermaid |
| `question.title` | question | (v0.7.0) **결론형 action title 의무** |
| `question.tags` | question | (v0.7.0, 옵션) tag chip |
| `option.detail.pros` / `cons` | option | (v0.7.0) **list of strings** — weighted bar 자동 계산 |

★ `background.tldr` / `kpis` / `findings` / `root_causes` / `solution` / `risk` / `principles` = **모두 optional**. Claude 가 정보량 따라 자율 박제. 모두 미박제 시 → 기존 `background.bullets` fallback (v0.7.x 호환).

### 3.2 v0.7.0 design 변경 (스펙 외 영역)

| 영역 | 변경 |
|---|---|
| typography | Pretendard Variable CDN + line-height 1.7 + max-width 640px + word-break keep-all + 자간 -0.01em |
| 옵션 비교 표 | matrix + heatmap 셀 (비용·위험·상태 색 강조) |
| 옵션 detail | split card (Pros/Cons 좌우) + 상단 weighted bar (Pros% / Cons% 자동 계산) |
| callout | 6종 토큰 (info/tip/important/warning/danger/note). 배경 카드 = info, 💡 왜 = tip 통일 |

★ "기타 (직접 입력)" 옵션 = render.py 자동 박제. JSON 안 명시 X.

---

## 4. render.py 호출 패턴

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/html-decision/scripts/render.py" \
  --output "<CWD>/.claude-history/html-decision/<YYYY-MM-DD>-<topic-slug>.html" \
  <<'HTML_DECISION_SPEC_EOF'
{...JSON spec...}
HTML_DECISION_SPEC_EOF
```

- `CLAUDE_PLUGIN_ROOT` = Claude Code 가 export 한 env. 없으면 `~/.claude/plugins/cache/html-decision/html-decision/<version>/` 사용
- `<CWD>` = 현재 작업 디렉토리 절대경로
- `<topic-slug>` = 핵심 키워드 2-3 (kebab-case). 같은 시간 충돌 시 `-v2`, `-v3` suffix
- output path 와 JSON 안 `source_html` = **일치 의무 + 둘 다 절대경로**. 상대경로 박제 시 render.py 자동 변환

---

## 5. 짧은 채팅 응답 template

```
HTML 결정 캔버스 생성 완료.

| | |
|---|---|
| 파일 | `<output path>` |
| 결정점 | <N>개 |

브라우저 → 선택 → [생성] → [복사] → 채팅 붙여넣기.
```

★ N=0 시 "결정점 0개 (설명용 문서)" 박제.

---

## 6. 의무 invariant

| 영역 | 의무 |
|---|---|
| 응답 형식 | HTML file 응답. 채팅 = file 경로 + 안내 3-5줄 |
| render.py 호출 | Claude 가 HTML 직접 생성 X — render.py 만 사용 |
| 모든 case 동일 layout | N=0/1/2+ 무관 — sidebar + 6 영역 동일 박제 |
| **결론형 action title** | `h1` + `question.title` 모두 결론형. content-rules.md §1 |
| **💡 왜 이 결정 필요** | 모든 Q `question.why` 의무 |
| 권장 옵션 | `recommended: true` + `reason` 1줄 + `confidence` 박제 (가능 시) |
| matrix_summary | `cost_level` + `risk_level` 의무 (옵션 비교 matrix 활용) |
| Pros/Cons | 권장 옵션 의무. `detail.pros` / `cons` = **list of strings** (weighted bar 자동 계산) |
| **chunk 룰** | content-rules.md §2 — paragraph / 문장 / bullet / list 길이 |
| **`background.detail` chunk 의무** | content-rules.md §7.4-7.6. 줄글 wall 절대 금지 — `<h4>` + `<ul>/<ol>` 분해 + `<strong>` 강조. 분량 무관, 정보 unit 2+ 면 분해 |
| **한국어 우선 박제** | content-rules.md §16. 영어 보존 카테고리 (약어/고유명사/패턴명/코드 entity/신조 기술) 외 한글. 결정 어휘 (chosen/rejected/valid/invalid 등) 100% 한글. 영어 비율 ≤ 20% 목표. ❌ 금지 표현 `consolidation paradigm`, `incremental fix`, `root cause 3종`, `boundary case` 등 — §16.4 참조 |
| MD 파싱 | paste-back parse rule = `references/output-formats.md` |
| 저장 경로 | `<CWD>/.claude-history/html-decision/<YYYY-MM-DD>-<topic-slug>.html` 절대경로 |

---

## 7. paste-back 인식

사용자가 `<!-- html-decision-result -->` 포함 MD 붙여넣기 = 결정 결과 인식. 각 `### Q<N>` 의 **답** 파싱 → 다음 step 진행.

parse 상세 = `references/output-formats.md`.

---

## 8. reference 인덱스

| 파일 | 언제 읽나 |
|---|---|
| `references/content-rules.md` | 결정점 분해 + **action title** + chunk 룰 + Pros/Cons + 💡 왜 + 배경/영향 + callout 종류 |
| `references/visual-patterns.md` | 시각 패턴 (split / matrix / heatmap / flow / quadrant) 선택 가이드 — N별 권장 |
| `references/output-formats.md` | paste-back 처리 시 (MD/JSON/prompt parse rule) |

★ `scripts/template.html` 과 `scripts/render.py` = 구조 SSOT. Claude 가 직접 읽을 필요 X (render.py 가 처리).
