# html-decision

> **Claude Code 용 결정 캔버스 플러그인.** Claude 대화 안 *결정 포인트의 터미널 표현 한계* 를 해소. 결정점 식별 → 옵션 도출 → Pros/Cons split → 비교 matrix → MD 결과 회수. 선택지 없는 *설명/공유* 문서 (N=0) 도 지원.

**`/html-decision <고민>` 으로 명시 호출**. ★ 자동 발동 X. ★ 추가 액션 0 (Claude 가 모든 시각 판단 자동).

[![Version](https://img.shields.io/badge/version-0.8.6-2563eb)](https://github.com/yeonjun-cho/html-decision)
[![License](https://img.shields.io/badge/license-MIT-10b981)](LICENSE)

---

## 🎯 컨셉

Claude 와 대화 중 *결정 포인트* (옵션 A/B/C 중 무엇?) 가 터미널 줄글로 표현하기 어렵다. HTML 캔버스로 시각화 → 한눈 비교 + 선택 + 결과 회수.

선택지 없이 *복잡 내용을 시각 공유* 도 가능 (N=0, 설명용 문서).

→ ADR (결정 *결과* 기록) 과 다름. **결정 *진행 중*** 의 동적 시각.

---

## 🎨 디자인 원칙 (v0.7.0)

### 1. Typography first (한국어 가독성)
Pretendard Variable + `line-height 1.7` + `word-break: keep-all` + 자간 `-0.01em` + max-width 640px (한글 약 40자/줄). 줄글 *난잡함* 의 근본 해결.

### 2. Action title (결론형 제목)
`h1` / `question.title` = **결론 + 핵심 근거** 한 줄. 토픽형 ("DB 선택?") X. McKinsey/Minto Pyramid 원칙.

### 3. Layering, not hiding
배경 / flow / 권장 / 영향 = 본문 안 *항상 visible*. 숨김 X. 정보 위계로 layered.

### 4. Visual metaphor over text
Pros/Cons = split card (좌 ✅ / 우 ⚠️) + 상단 weighted bar (자동 계산). 옵션 비교 = heatmap matrix. 빽빽 텍스트 X.

### 5. 모든 case 동일 layout
N=0 (설명용) / N=1 / N=N+ — 동일 sidebar + 본문 6 영역. 차이 = 컨텐츠 *값* 만.

### 6. Sidebar = 순수 목차
anchor only. 컨텐츠 박제 X.

### 7. 사용자 액션 0
호출 한 줄 + HTML 안 옵션 선택. mermaid 박제 / tag 박제 / flow 박제 = 모두 Claude 자율.

---

## 본문 6 영역 (모든 case 동일)

| 영역 | 역할 |
|---|---|
| 📋 **배경 카드** (info callout) | 분석 요약 bullet + "자세히" collapse |
| 🔄 **흐름** | 전역 sequence / 의존 Mermaid (옵션 박제, 미박제 시 empty state) |
| 🎯 **권장 요약 dashboard** | Q × 권장 옵션 × 신뢰도 × 이유 한눈 표 |
| **Q 카드 × N** | action title + tags + 권장 mini + 💡 왜 (tip callout) + 비교 matrix + 옵션 detail split + 영향 |
| ✏️ **결과 추출** | 생성 / 복사 / 초기화 버튼 |
| **Sidebar** | 진행 bar + 목차 (📋 / 🔄 / 🎯 / Q1~Qn / ✏️) |

### Q 카드 안 영역

| 영역 | 역할 |
|---|---|
| **action title h2** | 결론 + 핵심 근거 한 줄 |
| **tags** | framework / 분류 chip (옵션) |
| 🎯 **권장 mini-card** | 권장 옵션 + 신뢰도 + 1줄 이유 |
| 💡 **왜 이 결정** (callout-tip) | 결정 근거 / 맥락 / framework |
| **옵션 비교 matrix** | 옵션 / 비용 / 위험 / 신뢰도 / 상태 (heatmap 셀) |
| **옵션 detail split** | ✅ Pros / ⚠️ Cons + 상단 weighted bar (자동) — collapse default |
| 📊 **영향 영역** | 영향 file / 모듈 / Mermaid — collapse default |
| **선택** | radio + 기타 + 코멘트 |

---

## 📦 설치

Claude Code 안 슬래시 커맨드로 한 번에 끝.

```text
/plugin marketplace add https://github.com/yeonjun-cho/html-decision
/plugin install html-decision@html-decision
```

확인:

```text
/plugin
```

`html-decision` 이 `installed` 로 보이면 끝.

요구 사항: `python3` (macOS/Linux 기본 설치).

> ★ 향후 자동 갱신을 원하면 [🔄 업데이트](#-업데이트) 의 `autoUpdate` 박제 참조.

---

## 🚀 쓰는 법

**오직 명시 호출만 동작.** Claude 가 대화 문맥 보고 알아서 띄우는 일 X. 호출 후 *추가 액션 0* — Claude 가 모든 시각 판단 자율.

```text
/html-decision 새 프로젝트 프론트엔드 스택 결정
```

설명용 문서 (결정점 없이 배경만):

```text
/html-decision PoC 결과 분석 정리 (결정 없이 공유용)
```

### 결과 흐름

1. Claude 가 JSON spec 작성 (결정점 / 옵션 / Pros/Cons / mermaid 박제 *모두 자율 판단*)
2. `render.py` 가 HTML 렌더링 → `<CWD>/.claude-history/html-decision/<YYYY-MM-DD>-<topic>.html` 저장
3. `SendUserFile` 로 파일 전달 — 브라우저에서 열어 옵션 선택
4. `[생성]` → `[복사]` → 채팅에 다시 붙여넣기
5. Claude 가 `<!-- html-decision-result -->` 매직 코멘트로 결과 인식 → 다음 단계 진행

---

## ⏱ 케이스 별 예상 시간

| 결정점 N | Claude output | 예상 시간 |
|---|---|---|
| **N=0** (설명용) | ~700-1000 tokens | **25-45초** |
| **N=1-3** (단순) | ~900-1700 tokens | **35-65초** |
| **N=4-7** (표준) | ~2200-3800 tokens | **1-2.5분** |
| **N=8+** (헤비) | ~5500-9000 tokens | **2.5-4분** |

★ Claude 가 JSON spec 만 출력 (~5x 압축) — render.py 가 HTML 렌더링 (server-side, ~1초). bottleneck = JSON spec 작성 시간.

---

## 📂 구조

```
html-decision/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── README.md
├── LICENSE
└── skills/
    └── html-decision/
        ├── SKILL.md
        ├── scripts/
        │   ├── render.py        # JSON → HTML 렌더러 (Python 3.8+, stdlib only)
        │   └── template.html    # static scaffold (Pretendard + CSS + JS)
        └── references/
            ├── content-rules.md     # action title / chunk / Pros/Cons / 💡 왜 / 배경 / flow / 영향 / callout 룰
            ├── visual-patterns.md   # 시각 패턴 선택 가이드 (N별 권장 / flow / mermaid / tags)
            └── output-formats.md    # MD/JSON paste-back parse rule
```

---

## 🔄 업데이트

자동 (권장) + 수동 둘 다 지원. **권장 = 자동** — 한 번 박제하면 사용자 부담 0.

### 🟢 자동 갱신 (권장)

`~/.claude/settings.json` 의 `extraKnownMarketplaces.html-decision` entry 에 **`"autoUpdate": true` 한 줄 추가**:

```json
{
  "extraKnownMarketplaces": {
    "html-decision": {
      "source": {
        "source": "git",
        "url": "https://github.com/yeonjun-cho/html-decision.git"
      },
      "autoUpdate": true
    }
  }
}
```

- **신규 사용자** = `/plugin marketplace add ...` 후 위 entry 자동 생성 → `autoUpdate` 만 추가
- **기존 사용자** = 이미 있는 entry 에 `autoUpdate` 한 줄만 추가
- 다음 Claude Code restart 시 **marketplace + plugin 자동 갱신** 활성

### 🟡 수동 갱신

```text
/plugin marketplace update html-decision
/plugin update html-decision@html-decision
/reload-plugins
```

### 🔍 현재 버전 확인

```text
/plugin
```

→ `html-decision is already at the latest version (X.Y.Z).` 같이 출력.

---

## 🧠 설계 원칙 (Anthropic best practices + research 적용)

| 원칙 | 적용 |
|---|---|
| [Bundled scripts > generated code](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | `scripts/render.py` 가 결정성 boilerplate 담당. Claude 는 JSON spec 만 |
| [Progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | SKILL.md → references (content-rules / visual-patterns) → scripts |
| Process in SKILL.md, context in references | SKILL.md = process. content-rules / visual-patterns = 편집 룰. template.html = 구조 |
| Pyramid Principle (Minto) | Action title — 결론 우선. 본문 = "왜 그런가" |
| Dual coding theory | 텍스트 + 시각 병행 (heatmap / split card / flow Mermaid) |
| F-pattern scanning | sidebar (좌) + action title (상) + chunk 작은 단위 |
| 한국어 typography | Pretendard + line-height 1.7 + keep-all + 자간 |
| Self-contained HTML | 외부 의존 = Pretendard CDN + Mermaid CDN (옵션) |

---

## 📝 라이선스

MIT
