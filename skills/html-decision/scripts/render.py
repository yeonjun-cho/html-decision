#!/usr/bin/env python3
"""html-decision 캔버스 렌더러 (v0.6.0).

사용법:
    python3 render.py --output <path> < spec.json
    python3 render.py --input <spec.json> --output <path>

JSON spec → HTML 결정 캔버스. template.html 박제 후 placeholders 치환.

v0.6.0 design 원칙:
- 모든 case (N=0, 1, 2+) 동일 layout (sidebar + 본문 5 영역)
- sidebar = 순수 목차 (anchor only)
- 본문 = header / 📋 배경 / 🎯 권장 요약 / Q × N / ✏️ 결과 추출

Python 3.8+ stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape as html_escape
from pathlib import Path

TEMPLATE_NAME = "template.html"
MERMAID_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'
)


def esc(s):
    """HTML escape. None → 빈 문자열."""
    if s is None:
        return ""
    return html_escape(str(s), quote=True)


# ---------- per-section renderers ----------


def render_confidence(level, show_label=True):
    """confidence indicator — ●●●●○ + 라벨."""
    if level is None:
        return ""
    try:
        level = int(level)
    except (TypeError, ValueError):
        return ""
    level = max(0, min(5, level))
    filled = "●" * level
    empty = "○" * (5 - level)
    label_html = f'<span class="empty">{empty}</span>' if empty else ""
    return f'<span class="conf">{filled}{label_html}</span>'


def render_sidebar(data, questions):
    """sidebar 목차 — 진행 + anchor list (모든 case 동일 구조)."""
    nav_items = ['    <li><a href="#bg">📋 배경</a></li>']
    if questions:
        nav_items.append('    <li><a href="#rec">🎯 권장 요약</a></li>')
    else:
        # N=0 시 권장 요약 anchor 생략 (배경만)
        pass
    for q in questions:
        q_id = q["id"]
        nav_label = q.get("nav_label") or q.get("title", q_id)
        nav_items.append(
            f'    <li><a href="#{q_id}" data-q="{q_id}">{nav_label}</a></li>'
        )
    if questions:
        nav_items.append('    <li><a href="#submit">✏️ 결과 추출</a></li>')
    return "\n".join(nav_items)


def render_bg_card(data):
    """📋 배경 카드 (본문 위, 항상 박제 — id="bg")."""
    bg = data.get("background") or data.get("ack") or {}
    title = bg.get("title", "📋 배경 — 분석 요약")
    bullets = bg.get("bullets") or bg.get("paragraphs") or []
    detail = bg.get("detail")

    bullets_html = ""
    if bullets:
        items = "\n".join(f"    <li>{b}</li>" for b in bullets)
        bullets_html = f"  <ul>\n{items}\n  </ul>"
    else:
        bullets_html = '  <p style="color: var(--muted); font-style: italic; margin: 0;">배경 정보 없음.</p>'

    detail_html = ""
    if detail:
        detail_html = (
            "  <details>\n"
            "    <summary>자세히</summary>\n"
            f'    <div class="detail-text">{detail}</div>\n'
            "  </details>"
        )

    return (
        '<section class="bg-card" id="bg">\n'
        f'  <h3>{title}</h3>\n'
        f"{bullets_html}\n"
        f"{detail_html}\n"
        "</section>"
    )


def render_dashboard(questions):
    """🎯 권장 요약 dashboard (N=0 시 empty state)."""
    if not questions:
        return (
            '<section class="dashboard" id="rec">\n'
            '  <h3>🎯 Claude 권장 요약</h3>\n'
            '  <div class="empty-state">\n'
            '    <span class="emoji">📭</span>\n'
            "    결정 영역 없음 — 본 문서는 설명/공유 용도\n"
            "  </div>\n"
            "</section>"
        )

    rows = []
    for q in questions:
        rec = next((o for o in (q.get("options") or []) if o.get("recommended")), None)
        qid = q.get("id", "")
        nav = q.get("nav_label") or q.get("title", qid)
        if not rec:
            rows.append(
                f'    <tr>'
                f'<td><a class="q-link" href="#{qid}">{nav}</a></td>'
                f'<td><span class="reason">(권장 옵션 없음)</span></td>'
                f'<td></td>'
                f'<td></td>'
                f'</tr>'
            )
            continue
        opt_label = rec.get("label", "")
        reason = rec.get("reason", "")
        conf_html = render_confidence(rec.get("confidence"))
        rows.append(
            f'    <tr>'
            f'<td><a class="q-link" href="#{qid}">{nav}</a></td>'
            f'<td class="rec-opt">{opt_label}</td>'
            f'<td>{conf_html}</td>'
            f'<td class="reason">{reason}</td>'
            f"</tr>"
        )

    return (
        '<section class="dashboard" id="rec">\n'
        "  <h3>🎯 Claude 권장 요약</h3>\n"
        '  <p class="help">권장만 빠르게 확인 → 본문에서 자세한 내용</p>\n'
        "  <table>\n"
        "    <thead><tr>"
        "<th>Q</th>"
        "<th>권장</th>"
        "<th>신뢰도</th>"
        "<th>이유</th>"
        "</tr></thead>\n"
        "    <tbody>\n"
        + "\n".join(rows)
        + "\n    </tbody>\n"
        "  </table>\n"
        "</section>"
    )


# axis label 한국어 → level 표기.
AXIS_LEVEL_LABELS = {1: "낮", 2: "낮", 3: "중", 4: "높", 5: "높"}


def _level_class(label):
    """비용 / 위험도 등 한국어 등급 → CSS class."""
    if not label:
        return ""
    if label in ("낮", "低", "low"):
        return "low"
    if label in ("중", "中", "mid"):
        return "mid"
    if label in ("높", "高", "high"):
        return "high"
    return ""


def _status_class(status):
    """option.status 텍스트 → CSS class. ✓ / ⚠️ / ⚡ prefix 기반."""
    if not status:
        return ""
    s = str(status).strip()
    if s.startswith("✓") or "정합" in s or "ok" in s.lower():
        return "ok"
    if s.startswith("⚠"):
        return "warn"
    if s.startswith("⚡"):
        return "bndry"
    return ""


def render_option_row(opt, recommended_in_table=False):
    """옵션 비교 표 row."""
    is_rec = opt.get("recommended", False)
    rec_class = ' class="rec"' if is_rec else ""
    star = "★" if is_rec else ""
    ms = opt.get("matrix_summary") or {}
    cost = ms.get("cost_level", "")
    risk = ms.get("risk_level", "")
    cost_cls = _level_class(cost)
    risk_cls = _level_class(risk)
    conf_html = render_confidence(opt.get("confidence"))
    status = opt.get("status", "")
    status_cls = _status_class(status)

    label = opt.get("label", "")
    return (
        f"    <tr{rec_class}>"
        f'<td class="star">{star}</td>'
        f'<td class="opt-name">{label}</td>'
        f'<td><span class="level {cost_cls}">{cost}</span></td>'
        f'<td><span class="level {risk_cls}">{risk}</span></td>'
        f"<td>{conf_html}</td>"
        f'<td><span class="status {status_cls}">{status}</span></td>'
        f"</tr>"
    )


def render_options_table(options):
    """옵션 비교 표 — 옵션 / 비용 / 위험도 / 신뢰도 / 상태 5 column."""
    options = [o for o in options if o.get("value") != "other"]
    if not options:
        return ""
    # 권장 옵션을 첫 row 로
    rec = [o for o in options if o.get("recommended")]
    non_rec = [o for o in options if not o.get("recommended")]
    ordered = rec + non_rec
    rows = "\n".join(render_option_row(o) for o in ordered)
    return (
        '  <table class="options-table">\n'
        '    <thead><tr><th></th><th>옵션</th><th>비용</th><th>위험도</th><th>신뢰도</th><th>상태</th></tr></thead>\n'
        "    <tbody>\n"
        + rows
        + "\n    </tbody>\n"
        "  </table>"
    )


def render_option_card(opt):
    """옵션 detail 카드 (✅ Pros / ⚠️ Cons / 📌 예시)."""
    is_rec = opt.get("recommended", False)
    rec_cls = " rec" if is_rec else ""
    star = "★ " if is_rec else ""
    label = opt.get("label", "")
    conf_html = render_confidence(opt.get("confidence"))

    detail = opt.get("detail") or {}
    pros = detail.get("pros", "")
    cons = detail.get("cons", "")
    example = detail.get("example", "")

    rows = []
    if pros:
        # pros 가 list 또는 string 둘 다 허용
        items = pros if isinstance(pros, list) else [pros]
        first = True
        for item in items:
            prefix = "<strong>Pros</strong> · " if first else ""
            rows.append(
                f'        <div class="row pros"><span class="row-icon">✅</span>'
                f'<span class="row-text">{prefix}{item}</span></div>'
            )
            first = False
    if cons:
        items = cons if isinstance(cons, list) else [cons]
        first = True
        for item in items:
            prefix = "<strong>Cons</strong> · " if first else ""
            rows.append(
                f'        <div class="row cons"><span class="row-icon">⚠️</span>'
                f'<span class="row-text">{prefix}{item}</span></div>'
            )
            first = False
    if example:
        rows.append(
            f'        <div class="row example"><span class="row-icon">📌</span>'
            f'<span class="row-text"><strong>예시</strong> · {example}</span></div>'
        )

    rows_html = "\n".join(rows) if rows else ""

    return (
        f'      <div class="opt-card{rec_cls}">\n'
        f'        <div class="opt-card-head">\n'
        f"          <h4>{star}{label}</h4>\n"
        f'          <span class="opt-conf">{conf_html}</span>\n'
        f"        </div>\n"
        f"{rows_html}\n"
        f"      </div>"
    )


def render_question(q):
    """단일 결정점 카드 — 권장 mini + 💡 왜 + 옵션 표 + 옵션 detail + 영향 + 선택."""
    q_id = q["id"]
    title = q.get("title", "")
    desc = q.get("desc", "")
    why = q.get("why", "")
    options = q.get("options") or []
    impact = q.get("impact") or {}

    # 권장 옵션 찾기
    rec_opt = next((o for o in options if o.get("recommended")), None)

    parts = [
        f'<section class="question" id="{q_id}" data-qid="{q_id}">',
        f"  <h2>{title}</h2>",
    ]
    if desc:
        parts.append(f'  <p class="q-desc">{desc}</p>')

    # 🎯 권장 mini-card
    if rec_opt:
        conf_html = render_confidence(rec_opt.get("confidence"))
        parts.append(
            f'  <div class="q-rec">\n'
            f"    {conf_html}\n"
            f'    <span class="label">🎯 권장</span>\n'
            f'    <div class="opt">{rec_opt.get("label", "")}</div>\n'
            f'    <p class="reason">{rec_opt.get("reason", "")}</p>\n'
            f"  </div>"
        )

    # 💡 왜 이 결정 필요
    if why:
        why_lines = why if isinstance(why, list) else [why]
        why_html = "\n".join(f"    <p>{line}</p>" for line in why_lines)
        parts.append(
            f'  <div class="q-why">\n'
            f'    <p class="why-title">💡 왜 이 결정 필요?</p>\n'
            f"{why_html}\n"
            f"  </div>"
        )

    # 옵션 비교 표
    options_table = render_options_table(options)
    if options_table:
        parts.append(options_table)

    # 옵션 detail 카드 (collapse)
    non_other_opts = [o for o in options if o.get("value") != "other"]
    if non_other_opts:
        rec_opts = [o for o in non_other_opts if o.get("recommended")]
        non_rec_opts = [o for o in non_other_opts if not o.get("recommended")]
        ordered = rec_opts + non_rec_opts
        cards = "\n".join(render_option_card(o) for o in ordered)
        parts.append(
            f'  <details class="option-details">\n'
            f"    <summary>각 옵션 자세히 (카드 형식)</summary>\n"
            f'    <div class="detail-body">\n'
            f"{cards}\n"
            f"    </div>\n"
            f"  </details>"
        )

    # 영향 영역 (collapse)
    areas = impact.get("areas") or []
    mermaid_code = impact.get("mermaid")
    if areas or mermaid_code:
        impact_parts = ['  <details class="q-impact">', "    <summary>📊 영향 영역</summary>", '    <div class="impact-body">']
        if areas:
            items = "\n".join(f"        <li>{a}</li>" for a in areas)
            impact_parts.append(f"      <ul>\n{items}\n      </ul>")
        if mermaid_code:
            impact_parts.append(
                f'      <div class="impact-mermaid"><div class="mermaid">{mermaid_code}</div></div>'
            )
        impact_parts.append("    </div>")
        impact_parts.append("  </details>")
        parts.append("\n".join(impact_parts))

    # 선택 영역
    select_parts = ['  <div class="q-select">', "    <h3>선택</h3>"]
    for opt in options:
        if opt.get("value") == "other":
            continue
        rec_cls = ' class="rec"' if opt.get("recommended") else ""
        value = esc(opt.get("value", ""))
        label = opt.get("label", "")
        select_parts.append(
            f'    <label{rec_cls}><input type="radio" name="{q_id}" value="{value}"> {label}</label>'
        )
    select_parts.append(
        f'    <label><input type="radio" name="{q_id}" value="other"> 기타 (직접 입력)</label>'
    )
    select_parts.append(
        f'    <textarea class="other-input" data-for="{q_id}" placeholder="직접 입력..."></textarea>'
    )
    select_parts.append(
        f'    <textarea class="comment-input" data-for="{q_id}" placeholder="선택 이유 / 부연 / 조건 (선택)"></textarea>'
    )
    select_parts.append("  </div>")
    parts.append("\n".join(select_parts))

    parts.append("</section>")
    return "\n".join(parts)


# ---------- main ----------


def build(data):
    """spec dict → 완성된 HTML 문자열."""
    topic = data.get("topic", "결정 캔버스")
    date = data.get("date", "")
    branch = data.get("branch")
    meta_extra = data.get("meta")
    source_html = data.get("source_html", "")
    if source_html and not Path(source_html).is_absolute():
        source_html = str(Path(source_html).resolve())

    questions = data.get("questions") or []
    title = data.get("title") or topic
    h1 = data.get("h1") or topic

    meta_parts = []
    if date:
        meta_parts.append(date)
    if branch:
        meta_parts.append(branch)
    if meta_extra:
        meta_parts.append(meta_extra)
    meta_line = " · ".join(meta_parts) if meta_parts else ""

    # body 영역
    sidebar_nav = render_sidebar(data, questions)
    bg_card = render_bg_card(data)
    dashboard = render_dashboard(questions)
    questions_block = "\n\n".join(render_question(q) for q in questions)

    # Mermaid CDN — impact mermaid 또는 데이터 안 명시 시 활성
    has_impact_mermaid = any(
        (q.get("impact") or {}).get("mermaid") for q in questions
    )
    use_mermaid = bool(data.get("use_mermaid")) or has_impact_mermaid
    mermaid_script = MERMAID_CDN if use_mermaid else ""

    # template 로드 + 치환
    template_path = Path(__file__).parent / TEMPLATE_NAME
    template = template_path.read_text(encoding="utf-8")

    substitutions = {
        "{{TITLE}}": esc(title),
        "{{MERMAID_SCRIPT}}": mermaid_script,
        "{{H1}}": h1,
        "{{META}}": meta_line,
        "{{SIDEBAR_NAV}}": sidebar_nav,
        "{{BG_CARD}}": bg_card,
        "{{DASHBOARD}}": dashboard,
        "{{QUESTIONS_BLOCK}}": questions_block,
        "{{SOURCE_HTML}}": source_html,
        "{{TOPIC}}": topic.replace('"', '\\"'),
        "{{DATE}}": date,
        "{{TOTAL_Q}}": str(len(questions)),
    }

    result = template
    for key, val in substitutions.items():
        result = result.replace(key, val)

    leftover = re.findall(r"\{\{[A-Z_]+\}\}", result)
    if leftover:
        sys.stderr.write(f"warning: unresolved placeholders: {set(leftover)}\n")

    return result


def parse_args():
    p = argparse.ArgumentParser(description="html-decision 캔버스 렌더러 v0.6.0")
    p.add_argument("--output", "-o", required=True, help="출력 HTML 경로")
    p.add_argument("--input", "-i", help="JSON spec 파일 (생략 시 stdin)")
    return p.parse_args()


def main():
    args = parse_args()
    if args.input:
        spec_text = Path(args.input).read_text(encoding="utf-8")
    else:
        spec_text = sys.stdin.read()

    try:
        data = json.loads(spec_text)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"JSON parse 실패: {e}\n")
        sys.exit(1)

    html = build(data)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ {output_path} ({len(html.splitlines())} 줄)")


if __name__ == "__main__":
    main()
