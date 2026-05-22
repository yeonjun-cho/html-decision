#!/usr/bin/env python3
"""html-decision 캔버스 렌더러.

사용법:
    python3 render.py --output <path> < spec.json
    python3 render.py --input <spec.json> --output <path>

JSON spec → HTML 결정 캔버스. template.html (같은 디렉토리) 박제 후 placeholders 치환.

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
CHART_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>'
)

# Tier 별 자동 차등 widget 박제 영역.
WIDGETS_BY_TIER = {
    "T1": set(),
    "T2": {"dashboard", "matrix"},
    "T3": {"dashboard", "matrix", "radar", "impact", "confidence"},
}

# axis label 한국어 → level 표기 (matrix 의 axis 셀에 사용).
AXIS_LEVEL_LABELS = {
    1: "低", 2: "低", 3: "中", 4: "高", 5: "高",
}


def esc(s):
    """HTML escape. None → 빈 문자열."""
    if s is None:
        return ""
    return html_escape(str(s), quote=True)


def esc_attr(s):
    """attribute escape (quote=True 의 별칭)."""
    return esc(s)


def maybe(s):
    """None / 빈 문자열 → 빈 출력."""
    return s if s else ""


# ---------- per-section renderers ----------


def render_option(opt, q_id, idx):
    """단일 옵션 카드 HTML 생성."""
    is_other = opt.get("value") == "other"
    classes = ["option"]
    if opt.get("recommended"):
        classes.append("recommended")
    if is_other:
        classes.append("other-option")
    class_attr = " ".join(classes)

    rec_tag = (
        ' <span class="recommended-tag">권장</span>' if opt.get("recommended") else ""
    )
    label = opt.get("label", "")
    reason = opt.get("reason")
    detail = opt.get("detail") or {}

    parts = [
        f'  <label class="{class_attr}">',
        f'    <input type="radio" name="{q_id}" value="{esc_attr(opt["value"])}">',
        f'    <span class="opt-label">{label}{rec_tag}</span>',
    ]
    if reason:
        parts.append(f'    <span class="opt-reason">{reason}</span>')

    if detail and not is_other:
        pros = detail.get("pros")
        cons = detail.get("cons")
        example = detail.get("example")
        if pros or cons or example:
            parts.append('    <details class="option-detail">')
            parts.append("      <summary>자세히</summary>")
            parts.append('      <div class="detail-body">')
            if pros:
                parts.append(f'        <p class="pros"><strong>Pros</strong>: {pros}</p>')
            if cons:
                parts.append(f'        <p class="cons"><strong>Cons</strong>: {cons}</p>')
            if example:
                parts.append(
                    f'        <p class="example"><strong>예시</strong>: {example}</p>'
                )
            parts.append("      </div>")
            parts.append("    </details>")

    parts.append("  </label>")
    return "\n".join(parts)


def render_question(q, tier):
    """단일 결정점 카드 HTML 생성."""
    q_id = q["id"]
    title = q.get("title", "")
    desc = q.get("desc")
    context = q.get("context")
    options = q.get("options", [])
    preview = q.get("preview")

    parts = [
        f'<section class="question" id="{q_id}" data-qid="{q_id}">',
        f'  <h2 class="q-title">{title}</h2>',
    ]
    if desc:
        parts.append(f'  <p class="q-desc">{desc}</p>')
    if context:
        parts.append(f'  <div class="q-context">{context}</div>')

    # D. 영향 영역 (T3) — context 다음
    impact_html = render_impact_area(q, tier)
    if impact_html:
        parts.append(impact_html)

    # A. 옵션 비교 matrix (T2+) — 옵션 카드 위
    matrix_html = render_option_matrix(q, tier)
    if matrix_html:
        parts.append(matrix_html)

    # F. radar chart (T3) — matrix 옆/아래
    radar_html = render_radar_block(q, tier)
    if radar_html:
        parts.append(radar_html)

    parts.append("")

    for i, opt in enumerate(options):
        parts.append(render_option(opt, q_id, i))

    # 기타 옵션 (자동 박제 — 마지막 위치)
    other_in_options = any(o.get("value") == "other" for o in options)
    if not other_in_options:
        parts.append(
            f'  <label class="option other-option">\n'
            f'    <input type="radio" name="{q_id}" value="other">\n'
            f'    <span class="opt-label">기타 (직접 입력)</span>\n'
            f"  </label>"
        )
    parts.append(
        f'  <textarea class="other-input" data-for="{q_id}" rows="3" placeholder="직접 입력..."></textarea>'
    )

    # 코멘트 (T2+)
    if tier in ("T2", "T3"):
        parts.append("")
        parts.append(f'  <div class="comment-wrap" data-for-comment="{q_id}">')
        parts.append(
            '    <label class="comment-label">코멘트 (선택, 부연/조건/맥락)</label>'
        )
        parts.append(
            '    <textarea class="comment-input" rows="2" '
            'placeholder="선택 이유 / 추가 조건 / 부연 설명"></textarea>'
        )
        parts.append("  </div>")

    # preview-panel
    if preview:
        intro = preview.get("intro", "옵션 선택 시 영향 영역 view")
        parts.append("")
        parts.append(f'  <div class="preview-panel" data-for-preview="{q_id}">')
        parts.append(f'    <h5>{preview.get("title", "📋 선택 시 영향 (live)")}</h5>')
        parts.append(
            f'    <div class="preview-content"><p class="empty">{intro}</p></div>'
        )
        parts.append("  </div>")

    parts.append("</section>")
    return "\n".join(parts)


def render_sidebar(data, questions):
    """T3 sticky sidebar HTML 생성."""
    nav_items = []
    aux = data.get("sidebar_aux") or []
    for item in aux:
        href = item.get("href", "#")
        label = item.get("label", "")
        nav_items.append(f'      <li><a href="{href}" class="nav-q">{label}</a></li>')
    if aux and questions:
        nav_items.append('      <li style="margin-top: 8px;"></li>')

    for q in questions:
        q_id = q["id"]
        nav_label = q.get("nav_label") or q.get("title", q_id)
        nav_items.append(
            f'      <li><a href="#{q_id}" class="nav-q" data-q="{q_id}">{nav_label}</a></li>'
        )

    nav_items.append('      <li style="padding-top: 10px;">'
                     '<a href="#submit" class="nav-q" '
                     'style="color: var(--accent); font-weight: 600;">'
                     '✏️ 결과 추출</a></li>')

    return (
        '<aside class="sidebar">\n'
        "  <h3>진행</h3>\n"
        '  <div class="progress-wrap">\n'
        '    <div class="progress"><div class="progress-bar" id="prog-bar"></div></div>\n'
        f'    <span class="progress-text" id="prog-text">0/{len(questions)} 답함</span>\n'
        "  </div>\n"
        "  <h3>네비게이션</h3>\n"
        "  <nav>\n"
        '    <ul class="nav-list">\n'
        + "\n".join(nav_items)
        + "\n    </ul>\n"
        "  </nav>\n"
        "</aside>"
    )


def render_ack(ack):
    """ack-area 섹션 (선행 결정 박제)."""
    if not ack:
        return ""
    title = ack.get("title", "이전 결정 ack")
    paragraphs = ack.get("paragraphs") or []
    p_html = "\n".join(f"    <p>{p}</p>" for p in paragraphs)
    return (
        '<section id="ack">\n'
        '  <div class="ack-area">\n'
        f"    <h4>📥 {title}</h4>\n"
        f"{p_html}\n"
        "  </div>\n"
        "</section>"
    )


def render_flow(flow):
    """flow-area 섹션 (Mermaid timeline)."""
    if not flow:
        return ""
    title = flow.get("title", "흐름")
    mermaid = flow.get("mermaid", "")
    return (
        '<section id="flow">\n'
        '  <div class="flow-area">\n'
        f"    <h4>🔄 {title}</h4>\n"
        '    <div class="mermaid-wrap">\n'
        '      <div class="mermaid">\n'
        f"{mermaid}\n"
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>"
    )


def render_section_intro(intro):
    """section-intro highlight box."""
    if not intro:
        return ""
    return f'<div class="section-intro">{intro}</div>'


# ---------- v0.5.0 5 widget renderers ----------


def render_confidence(level, show_label=True):
    """E. confidence indicator — ●●●●○ + 라벨."""
    if level is None:
        return ""
    try:
        level = int(level)
    except (TypeError, ValueError):
        return ""
    level = max(0, min(5, level))
    filled = "●" * level
    empty = "○" * (5 - level)
    label = f'<span class="confidence-label">{level}/5</span>' if show_label else ""
    return (
        f'<span class="confidence">'
        f'<span class="filled">{filled}</span>'
        f'<span class="empty">{empty}</span>'
        f'</span>{label}'
    )


def render_recommendations_dashboard(questions, tier):
    """B. 권장 dashboard — 본문 위 한눈 표 (T2+ 의무)."""
    if "dashboard" not in WIDGETS_BY_TIER.get(tier, set()):
        return ""
    rows = []
    has_rec = False
    for q in questions:
        rec = next((o for o in (q.get("options") or []) if o.get("recommended")), None)
        qid = q.get("id", "")
        nav = q.get("nav_label") or q.get("title", qid)
        if not rec:
            rows.append(
                f'    <tr>'
                f'<td><a class="q-link" href="#{qid}">{nav}</a></td>'
                f'<td><span class="rec-reason">(권장 옵션 없음 — 사용자 영역)</span></td>'
                f'<td></td>'
                f'<td></td>'
                f'</tr>'
            )
            continue
        has_rec = True
        opt_label = rec.get("label", "")
        reason = rec.get("reason", "")
        conf_html = ""
        if "confidence" in WIDGETS_BY_TIER.get(tier, set()):
            conf_html = render_confidence(rec.get("confidence"))
        rows.append(
            f'    <tr>'
            f'<td><a class="q-link" href="#{qid}">{nav}</a></td>'
            f'<td class="rec-opt">{opt_label}</td>'
            f'<td>{conf_html}</td>'
            f'<td class="rec-reason">{reason}</td>'
            f'</tr>'
        )

    if not has_rec and not rows:
        return ""

    conf_th = (
        "<th>확신도</th>" if "confidence" in WIDGETS_BY_TIER.get(tier, set()) else "<th></th>"
    )
    return (
        '<div class="recommendations-dashboard">\n'
        f'  <h3>🎯 Claude 권장 요약 ({len(questions)} 영역)</h3>\n'
        '  <p class="dash-help">권장 옵션만 먼저 검토하고 sanity check → 아래 결정점 본문에서 detail 확인.</p>\n'
        '  <table class="dash-table">\n'
        '    <thead><tr>'
        '<th>Q</th>'
        '<th>권장 옵션</th>'
        f'{conf_th}'
        '<th>1줄 이유</th>'
        '</tr></thead>\n'
        '    <tbody>\n'
        + "\n".join(rows)
        + "\n    </tbody>\n"
        "  </table>\n"
        "</div>"
    )


def render_option_matrix(q, tier):
    """A. 옵션 비교 matrix — 각 Q 안 첫머리 (T2+ 의무)."""
    if "matrix" not in WIDGETS_BY_TIER.get(tier, set()):
        return ""
    options = [o for o in (q.get("options") or []) if o.get("value") != "other"]
    if not options:
        return ""

    # Pros/Cons/예시/cost/risk 요약 — matrix_summary 우선, 없으면 detail 에서 도출.
    rows = []
    for o in options:
        rec_class = ' class="rec-row"' if o.get("recommended") else ""
        rec_mark = "★" if o.get("recommended") else ""
        ms = o.get("matrix_summary") or {}
        detail = o.get("detail") or {}
        pros = ms.get("pros_core") or detail.get("pros", "")
        cons = ms.get("cons_core") or detail.get("cons", "")
        # 본문에 들어갈 핵심만 — 너무 길면 자름.
        pros_short = (pros[:60] + "…") if len(pros) > 65 else pros
        cons_short = (cons[:60] + "…") if len(cons) > 65 else cons

        # cost/risk level — matrix_summary 또는 axes 에서.
        axes = o.get("axes") or {}
        cost_level = ms.get("cost_level")
        if not cost_level and axes.get("cost"):
            cost_level = AXIS_LEVEL_LABELS.get(int(axes["cost"]), "")
        risk_level = ms.get("risk_level")
        if not risk_level and axes.get("risk"):
            risk_level = AXIS_LEVEL_LABELS.get(int(axes["risk"]), "")

        rows.append(
            f'    <tr{rec_class}>'
            f'<td class="opt-name">{rec_mark} {o.get("label", "")}</td>'
            f'<td>{pros_short}</td>'
            f'<td>{cons_short}</td>'
            f'<td class="axis-cell axis-{esc(cost_level)}">{cost_level or "—"}</td>'
            f'<td class="axis-cell axis-{esc(risk_level)}">{risk_level or "—"}</td>'
            f'</tr>'
        )

    return (
        '  <table class="option-matrix">\n'
        '    <thead><tr>'
        '<th>옵션</th>'
        '<th>Pros 핵심</th>'
        '<th>Cons 핵심</th>'
        '<th>비용</th>'
        '<th>risk</th>'
        '</tr></thead>\n'
        '    <tbody>\n'
        + "\n".join(rows)
        + "\n    </tbody>\n"
        "  </table>"
    )


def render_radar_block(q, tier):
    """F. radar chart HTML container — 각 Q 안 (T3 한정)."""
    if "radar" not in WIDGETS_BY_TIER.get(tier, set()):
        return ""
    qid = q.get("id", "")
    # axes 데이터가 1개 옵션이라도 있어야 의미 있음.
    options = [o for o in (q.get("options") or []) if o.get("value") != "other"]
    has_axes = any(o.get("axes") for o in options)
    if not has_axes:
        return ""
    return (
        f'  <div class="radar-wrap">\n'
        f'    <h5>🎯 옵션 비교 (5축 visual)</h5>\n'
        f'    <canvas class="radar-canvas" data-qid="{qid}"></canvas>\n'
        f'  </div>'
    )


def render_impact_area(q, tier):
    """D. 영향 영역 시각화 — 각 Q context block 옆 (T3 한정)."""
    if "impact" not in WIDGETS_BY_TIER.get(tier, set()):
        return ""
    impact = q.get("impact") or {}
    if not impact:
        return ""
    mermaid_code = impact.get("mermaid")
    areas = impact.get("areas") or []
    if not mermaid_code and not areas:
        return ""

    title = impact.get("title", "📊 영향 영역")
    parts = [f'  <div class="impact-area">', f'    <h5>{title}</h5>']
    if areas:
        items = "".join(f"<li>{a}</li>" for a in areas)
        parts.append(f'    <ul>{items}</ul>')
    if mermaid_code:
        parts.append(
            f'    <div class="impact-mermaid"><div class="mermaid">{mermaid_code}</div></div>'
        )
    parts.append("  </div>")
    return "\n".join(parts)


def collect_radar_data(questions, tier):
    """F. radar chart 용 JS data — 모든 Q 의 axes data 통합."""
    if "radar" not in WIDGETS_BY_TIER.get(tier, set()):
        return {}
    out = {}
    for q in questions:
        options = [o for o in (q.get("options") or []) if o.get("value") != "other"]
        opts_with_axes = [o for o in options if o.get("axes")]
        if len(opts_with_axes) < 2:
            continue  # 비교 의미 X
        # axis 순서 정합 — 첫 옵션의 axes 키 순서 사용.
        axes_keys = list(opts_with_axes[0]["axes"].keys())
        out[q["id"]] = {
            "axes": axes_keys,
            "options": [
                {
                    "label": o.get("label", ""),
                    "values": [int(o["axes"].get(k, 0)) for k in axes_keys],
                    "recommended": bool(o.get("recommended")),
                }
                for o in opts_with_axes
            ],
        }
    return out


def render_output_buttons(tier):
    """Tier 별 format 버튼."""
    btns = [
        '    <button class="gen active" onclick="generate(\'md\')" id="btn-md">📄 MD 생성</button>'
    ]
    if tier in ("T2", "T3"):
        btns.append(
            '    <button class="gen" onclick="generate(\'json\')" id="btn-json">📦 JSON 생성</button>'
        )
    if tier == "T3":
        btns.append(
            '    <button class="gen" onclick="generate(\'prompt\')" id="btn-prompt">💬 prompt 생성</button>'
        )
    return "\n".join(btns)


def render_preview_data_js(questions):
    """Q*_PREVIEWS const 박제 (JS data)."""
    preview_data = {}
    for q in questions:
        preview = q.get("preview")
        if not preview:
            continue
        options = preview.get("options") or {}
        if options:
            preview_data[q["id"]] = options
    if not preview_data:
        return "const PREVIEW_DATA = {}; window.PREVIEW_DATA = PREVIEW_DATA;"
    js = "const PREVIEW_DATA = " + json.dumps(preview_data, ensure_ascii=False, indent=2) + ";"
    js += "\nwindow.PREVIEW_DATA = PREVIEW_DATA;"
    return js


# ---------- main ----------


def build(data):
    """spec dict → 완성된 HTML 문자열."""
    topic = data.get("topic", "결정 캔버스")
    date = data.get("date", "")
    branch = data.get("branch")
    meta_extra = data.get("meta")
    source_html = data.get("source_html", "")
    # source_html = 절대경로 의무 (paste-back 식별 + 세션 끊김 대비).
    # 상대경로 박제 시 cwd 기준 절대경로 자동 변환 (safety net).
    if source_html and not Path(source_html).is_absolute():
        source_html = str(Path(source_html).resolve())
    tier = data.get("tier", "T1").upper()
    layout = data.get("layout") or ("with-sidebar" if tier == "T3" else "simple")
    use_mermaid = bool(data.get("use_mermaid") or data.get("flow"))
    use_localstorage = bool(data.get("use_localstorage", tier == "T3"))

    questions = data.get("questions") or []
    title = data.get("title") or topic

    meta_parts = []
    if date:
        meta_parts.append(date)
    if branch:
        meta_parts.append(branch)
    if meta_extra:
        meta_parts.append(meta_extra)
    meta_line = " · ".join(meta_parts) if meta_parts else ""

    h1 = data.get("h1") or topic

    # body 조립
    sidebar_block = render_sidebar(data, questions) if layout == "with-sidebar" else ""
    ack_section = render_ack(data.get("ack"))
    flow_section = render_flow(data.get("flow"))
    section_intro = render_section_intro(data.get("section_intro"))
    recommendations_dashboard = render_recommendations_dashboard(questions, tier)

    questions_block = "\n\n".join(render_question(q, tier) for q in questions)

    output_buttons = render_output_buttons(tier)
    preview_data_js = render_preview_data_js(questions)

    # F. radar chart 데이터 (T3 only) + Chart.js CDN
    radar_data = collect_radar_data(questions, tier)
    radar_data_js = (
        f"const RADAR_DATA = {json.dumps(radar_data, ensure_ascii=False, indent=2)};\n"
        "window.RADAR_DATA = RADAR_DATA;"
    ) if radar_data else "const RADAR_DATA = {}; window.RADAR_DATA = RADAR_DATA;"
    use_chart = bool(radar_data)

    # D. impact-area Mermaid 박제 시 mermaid 도 켜짐
    has_impact_mermaid = any(
        (q.get("impact") or {}).get("mermaid") for q in questions
    )
    if has_impact_mermaid:
        use_mermaid = True

    mermaid_script = MERMAID_CDN if use_mermaid else ""
    chart_script = CHART_CDN if use_chart else ""

    # template 로드 + 치환
    template_path = Path(__file__).parent / TEMPLATE_NAME
    template = template_path.read_text(encoding="utf-8")

    substitutions = {
        "{{TITLE}}": esc(title),
        "{{MERMAID_SCRIPT}}": mermaid_script,
        "{{CHART_SCRIPT}}": chart_script,
        "{{LAYOUT_CLASS}}": layout,
        "{{SIDEBAR_BLOCK}}": sidebar_block,
        "{{H1}}": h1,
        "{{META}}": meta_line,
        "{{ACK_SECTION}}": ack_section,
        "{{FLOW_SECTION}}": flow_section,
        "{{RECOMMENDATIONS_DASHBOARD}}": recommendations_dashboard,
        "{{SECTION_INTRO}}": section_intro,
        "{{QUESTIONS_BLOCK}}": questions_block,
        "{{OUTPUT_BUTTONS}}": output_buttons,
        "{{SOURCE_HTML}}": source_html,
        "{{TOPIC}}": topic.replace('"', '\\"'),
        "{{DATE}}": date,
        "{{TOTAL_Q}}": str(len(questions)),
        "{{USE_LOCALSTORAGE}}": "true" if use_localstorage else "false",
        "{{PREVIEW_DATA_JS}}": preview_data_js + "\n\n" + radar_data_js,
    }

    result = template
    for key, val in substitutions.items():
        result = result.replace(key, val)

    # 잔존 placeholder 검출 (디버그용)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", result)
    if leftover:
        sys.stderr.write(f"warning: unresolved placeholders: {set(leftover)}\n")

    return result


def parse_args():
    p = argparse.ArgumentParser(description="html-decision 캔버스 렌더러")
    p.add_argument("--output", "-o", required=True, help="출력 HTML 경로")
    p.add_argument(
        "--input",
        "-i",
        help="JSON spec 파일 경로 (생략 시 stdin 에서 읽음)",
    )
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
