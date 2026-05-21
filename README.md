# html-decision

Claude Code 용 스킬 플러그인. 사용자의 고민·결정사항을 **HTML 결정 캔버스**로 변환한다.

> 결정점 식별 → 옵션 도출 → HTML 시각화 → MD 형태로 결과 회수.

"고민이다", "결정 도와줘", "어떻게 할지 모르겠어" 같은 발화가 나오거나 결정점이 2개 이상 보이면 자동 발동한다. `/html-decision <고민>` 으로 직접 부를 수도 있다.

---

## 설치

Claude Code 안에서 슬래시 커맨드로 한 번에 끝난다.

```text
/plugin marketplace add yeonjun-cho/html-decision
/plugin install html-decision@html-decision
```

확인:

```text
/plugin
```

`html-decision` 이 `installed` 로 보이면 끝.

---

## 쓰는 법

### 1) 자동 발동

대화 중에 결정 고민이 보이면 Claude 가 알아서 스킬을 띄운다.

```
사용자: 새 프로젝트 스택 고르는 거 고민이다. Next vs Remix vs Astro 어떻게 할지...
Claude: [/html-decision 자동 호출 → HTML 캔버스 생성 → 파일 전달]
```

### 2) 명시 호출

```
/html-decision 새 프로젝트 프론트엔드 스택 결정
```

### 3) 결과 흐름

1. Claude 가 `.claude-history/html-decision/<YYYY-MM-DD-HH>-<topic>.html` 로 캔버스 저장
2. `SendUserFile` 로 파일 전달 — 브라우저에서 열어 옵션 선택
3. `[생성]` → `[복사]` → 채팅에 다시 붙여넣기
4. Claude 가 `<!-- html-decision-result -->` 매직 코멘트로 결과를 인식해서 다음 단계로 진행

---

## Tier 분기

결정점 개수에 따라 자동으로 복잡도가 갈린다.

| Tier | 결정점 N | 기능 |
|---|---|---|
| **T1** | 1~3 | radio/checkbox + 기타 + MD 버튼 1개 |
| **T2** | 4~7 | T1 + 코멘트 + 권장 옵션 + MD/JSON 버튼 |
| **T3** | 8+ | T2 + phase grouping + sticky sidebar + 3-format + Mermaid/Chart.js |

자세한 동작은 [`skills/html-decision/SKILL.md`](skills/html-decision/SKILL.md).

---

## 구조

```
html-decision/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
└── skills/
    └── html-decision/
        ├── SKILL.md
        └── references/
            ├── html-template.md
            ├── output-formats.md
            └── widgets.md
```

---

## 업데이트

```text
/plugin marketplace update html-decision
/plugin update html-decision@html-decision
```

---

## 라이선스

MIT
