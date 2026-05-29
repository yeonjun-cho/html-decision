#!/usr/bin/env python3
"""html-decision 캔버스 렌더러 (v0.7.0).

사용법:
    python3 render.py --output <path> < spec.json
    python3 render.py --input <spec.json> --output <path>

JSON spec → HTML 결정 캔버스. template.html 박제 후 placeholders 치환.

v0.7.0 design 원칙:
- Pretendard typography (line-height 1.7 / 한글 keep-all / 자간 -0.01em)
- Action title (결론형 Q 제목 의무)
- 본문 6 영역: header / 📋 배경 / 🔄 흐름 / 🎯 권장 / Q × N / ✏️ 결과 추출
- 옵션 비교 matrix (heatmap 셀)
- Pros/Cons split card + weighted bar (자동 계산)
- 모든 case (N=0, 1, 2+) 동일 layout. flow 미박제 시 empty state

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


# ---------- helpers ----------


def render_confidence(level, show_label=True):
    """confidence indicator — ●●●●○."""
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


def _level_class(label):
    """비용 / 위험도 등 한국어 등급 → heat CSS class."""
    if not label:
        return ""
    if label in ("낮", "低", "low"):
        return "heat-low"
    if label in ("중", "中", "mid"):
        return "heat-mid"
    if label in ("높", "高", "high"):
        return "heat-high"
    return ""


def _status_class(status):
    """option.status 텍스트 → heat CSS class. ✓ / ⚠️ / ⚡ prefix 기반."""
    if not status:
        return ""
    s = str(status).strip()
    if s.startswith("✓") or "정합" in s:
        return "heat-ok"
    if s.startswith("⚠"):
        return "heat-danger"
    if s.startswith("⚡"):
        return "heat-bndry"
    return ""


def _to_list(val):
    """단일 string 또는 list of strings → 항상 list."""
    if val is None:
        return []
    if isinstance(val, list):
        return [x for x in val if x]
    return [val] if val else []


# ---------- per-section renderers ----------


def render_sidebar(data, questions):
    """sidebar 목차 — 모든 case 동일 (📋 배경 / 🔄 흐름 / 🎯 권장 / Q anchors / ✏️ 결과 추출)."""
    nav_items = ['    <li><a href="#bg">📋 배경</a></li>']
    nav_items.append('    <li><a href="#flow">🔄 흐름</a></li>')
    if questions:
        nav_items.append('    <li><a href="#rec">🎯 권장 요약</a></li>')
    for q in questions:
        q_id = q["id"]
        nav_label = q.get("nav_label") or q.get("title", q_id)
        nav_items.append(
            f'    <li><a href="#{q_id}" data-q="{q_id}">{nav_label}</a></li>'
        )
    if questions:
        nav_items.append('    <li><a href="#submit">✏️ 결과 추출</a></li>')
    return "\n".join(nav_items)


def _render_callout_block(cls, icon_title, body_html):
    """카테고리 callout 한 블록 — title + body. body 는 미리 렌더된 HTML."""
    return (
        f'  <section class="callout {cls}">\n'
        f'    <p class="callout-title">{icon_title}</p>\n'
        f"{body_html}\n"
        "  </section>"
    )


def _render_bullet_list(items, ordered=False):
    """list of strings (또는 list of {label, sub}) → <ul>/<ol>."""
    if not items:
        return ""
    tag = "ol" if ordered else "ul"
    rows = []
    for it in items:
        if isinstance(it, dict):
            label = it.get("label", "")
            sub = it.get("sub") or it.get("desc")
            if sub:
                rows.append(f"      <li><strong>{label}</strong> — {sub}</li>")
            else:
                rows.append(f"      <li>{label}</li>")
        else:
            rows.append(f"      <li>{it}</li>")
    return f"    <{tag}>\n" + "\n".join(rows) + f"\n    </{tag}>"


def _render_chip_group(chips):
    """list of strings → chip-group div."""
    if not chips:
        return ""
    items = " ".join(f'<span class="chip">{esc(c)}</span>' for c in chips)
    return f'    <div class="chip-group">{items}</div>'


def render_bg_card(data):
    """📋 배경 카드 — bg-card-stack (TL;DR + KPI strip + 카테고리 callout + chip + detail).

    background 안 신설 필드 (v0.8.0):
    - tldr: string — 1줄 thesis (gradient hero 박제)
    - kpis: list of {num, lbl, sub?} — stat-tile-strip
    - findings: {title?, bullets} — 🔍 발견 callout-info
    - root_causes: {title?, items} — 🚨 root cause callout-warning (numbered)
    - solution: {title?, body} — 💡 해결 방향 callout-tip
    - risk: {title?, body} — ⚠️ risk callout-danger
    - principles: {title?, groups: [{label, chips}]} — 🔒 frozen 원칙 callout-note + chip
    - detail: string — 자세히 collapse (HTML 허용)

    기존 형식 fallback:
    - background.bullets / background.title → 단일 callout-info 박제 (v0.7.x 호환)
    """
    bg = data.get("background") or data.get("ack") or {}

    parts = []

    # 1. TL;DR hero
    tldr = bg.get("tldr")
    if tldr:
        label = bg.get("tldr_label", "📋 배경 — TL;DR")
        parts.append(
            '  <div class="bg-tldr">\n'
            f'    <p class="tldr-label">{label}</p>\n'
            f'    <p class="tldr-text">{tldr}</p>\n'
            "  </div>"
        )

    # 2. KPI stat-tile strip
    kpis = bg.get("kpis") or []
    if kpis:
        tiles = []
        for k in kpis:
            num = k.get("num", "")
            lbl = k.get("lbl", "")
            sub = k.get("sub", "")
            sub_html = f'\n      <span class="sub">{sub}</span>' if sub else ""
            tiles.append(
                '    <div class="stat-tile">\n'
                f'      <span class="num">{num}</span>\n'
                f'      <span class="lbl">{lbl}</span>{sub_html}\n'
                "    </div>"
            )
        parts.append(
            '  <div class="stat-tile-strip">\n'
            + "\n".join(tiles)
            + "\n  </div>"
        )

    # 3. 🔍 findings (callout-info)
    findings = bg.get("findings")
    if findings:
        title = findings.get("title", "🔍 발견")
        bullets = findings.get("bullets") or []
        body = _render_bullet_list(bullets)
        parts.append(_render_callout_block("callout-info", title, body))

    # 4. 🚨 root_causes (callout-warning, numbered)
    rc = bg.get("root_causes")
    if rc:
        title = rc.get("title", "🚨 root cause")
        items = rc.get("items") or rc.get("bullets") or []
        body = _render_bullet_list(items, ordered=True)
        parts.append(_render_callout_block("callout-warning", title, body))

    # 5. 💡 solution (callout-tip)
    sol = bg.get("solution")
    if sol:
        title = sol.get("title", "💡 해결 방향")
        body_text = sol.get("body") or sol.get("text") or ""
        bullets = sol.get("bullets") or []
        body = (
            f"    <p>{body_text}</p>" if body_text and not bullets
            else _render_bullet_list(bullets) if bullets
            else ""
        )
        parts.append(_render_callout_block("callout-tip", title, body))

    # 6. ⚠️ risk (callout-danger)
    risk = bg.get("risk")
    if risk:
        title = risk.get("title", "⚠️ risk")
        body_text = risk.get("body") or risk.get("text") or ""
        bullets = risk.get("bullets") or []
        body = (
            f"    <p>{body_text}</p>" if body_text and not bullets
            else _render_bullet_list(bullets) if bullets
            else ""
        )
        parts.append(_render_callout_block("callout-danger", title, body))

    # 7. 🔒 principles (callout-note + chip groups)
    pr = bg.get("principles")
    if pr:
        title = pr.get("title", "🔒 frozen 원칙")
        groups = pr.get("groups") or []
        # groups = [{label, chips: [...]}] 또는 단순 chips
        body_lines = []
        if not groups and pr.get("chips"):
            groups = [{"chips": pr["chips"]}]
        for i, g in enumerate(groups):
            label = g.get("label")
            chips = g.get("chips") or []
            margin = ' style="margin-top: 12px"' if i > 0 else ""
            if label:
                body_lines.append(f'    <p{margin}><strong>{label}</strong></p>')
            elif i == 0:
                pass
            body_lines.append(_render_chip_group(chips))
        body = "\n".join(body_lines)
        parts.append(_render_callout_block("callout-note", title, body))

    # 8. 자세히 collapse
    detail = bg.get("detail")
    if detail:
        parts.append(
            "  <details>\n"
            "    <summary>자세히</summary>\n"
            f'    <div class="detail-text">{detail}</div>\n'
            "  </details>"
        )

    # === fallback: 기존 background.bullets / title (v0.7.x 호환) ===
    has_new = any([tldr, kpis, findings, rc, sol, risk, pr])
    if not has_new:
        title = bg.get("title", "📋 배경 — 분석 요약")
        bullets = bg.get("bullets") or bg.get("paragraphs") or []
        body_html = ""
        if bullets:
            items = "\n".join(f"    <li>{b}</li>" for b in bullets)
            body_html = f"  <ul>\n{items}\n  </ul>"
        else:
            body_html = '  <p><em>배경 정보 없음.</em></p>'
        detail_html = ""
        if detail:
            detail_html = (
                "  <details>\n"
                "    <summary>자세히</summary>\n"
                f'    <div class="detail-text">{detail}</div>\n'
                "  </details>"
            )
        return (
            '<section class="callout callout-info bg-card" id="bg">\n'
            f'  <p class="callout-title">{title}</p>\n'
            f"{body_html}\n"
            f"{detail_html}\n"
            "</section>"
        )

    # 새 형식 — bg-card-stack
    return (
        '<section class="bg-card-stack" id="bg">\n'
        + "\n\n".join(parts)
        + "\n</section>"
    )


def render_flow(data):
    """🔄 flow 영역 (id="flow"). 박제 시 mermaid, 미박제 시 empty state — 모든 case 동일 layout."""
    flow = data.get("flow") or {}
    title = flow.get("title", "🔄 흐름")
    mermaid_code = flow.get("mermaid")

    if mermaid_code:
        return (
            '<section class="flow-area" id="flow">\n'
            f'  <h3>{esc(title)}</h3>\n'
            '  <div class="mermaid-wrap">\n'
            f'    <div class="mermaid">{mermaid_code}</div>\n'
            "  </div>\n"
            "</section>"
        )
    # empty state — 동일 layout 박제
    return (
        '<section class="flow-area" id="flow">\n'
        f'  <h3>{esc(title)}</h3>\n'
        '  <div class="empty-state">\n'
        '    <span class="emoji">📭</span>\n'
        "    흐름 시각 없음 — 결정 sequence / 의존이 단순한 경우\n"
        "  </div>\n"
        "</section>"
    )


def render_dashboard(questions):
    """🎯 권장 요약 dashboard (id="rec"). N=0 시 empty state."""
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


def render_options_matrix(options):
    """옵션 비교 matrix — 옵션 / 비용 / 위험도 / 신뢰도 / 상태 (heatmap 셀)."""
    options = [o for o in options if o.get("value") != "other"]
    if not options:
        return ""
    rec_opts = [o for o in options if o.get("recommended")]
    non_rec = [o for o in options if not o.get("recommended")]
    ordered = rec_opts + non_rec

    rows = []
    for opt in ordered:
        is_rec = opt.get("recommended", False)
        rec_class = ' class="rec"' if is_rec else ""
        star = "★ " if is_rec else ""
        label = opt.get("label", "")
        ms = opt.get("matrix_summary") or {}
        cost = ms.get("cost_level", "")
        risk = ms.get("risk_level", "")
        cost_cls = _level_class(cost)
        risk_cls = _level_class(risk)
        conf_html = render_confidence(opt.get("confidence"))
        status = opt.get("status", "")
        status_cls = _status_class(status)
        cost_cell = f'<span class="heat {cost_cls}">{cost}</span>' if cost else ""
        risk_cell = f'<span class="heat {risk_cls}">{risk}</span>' if risk else ""
        status_cell = f'<span class="heat {status_cls}">{status}</span>' if status else ""
        rows.append(
            f"    <tr{rec_class}>"
            f'<td class="star-cell">{star}</td>'
            f'<td class="opt-name">{label}</td>'
            f"<td>{cost_cell}</td>"
            f"<td>{risk_cell}</td>"
            f"<td>{conf_html}</td>"
            f"<td>{status_cell}</td>"
            f"</tr>"
        )
    return (
        '  <table class="options-matrix">\n'
        '    <thead><tr><th></th><th>옵션</th><th>비용</th><th>위험도</th><th>신뢰도</th><th>상태</th></tr></thead>\n'
        "    <tbody>\n"
        + "\n".join(rows)
        + "\n    </tbody>\n"
        "  </table>"
    )


def render_pros_cons_split(detail):
    """Pros/Cons split card + weighted bar (자동 계산). detail = {pros, cons, example?}."""
    if not detail:
        return ""
    pros = _to_list(detail.get("pros"))
    cons = _to_list(detail.get("cons"))
    example = detail.get("example", "")

    # weighted bar — pros/cons 항목 수 비율 (자동 계산)
    p_count = len(pros)
    c_count = len(cons)
    total = p_count + c_count
    if total > 0:
        p_pct = round(p_count / total * 100)
        c_pct = 100 - p_pct
    else:
        p_pct = c_pct = 0

    bar_html = ""
    if total > 0:
        bar_html = (
            '<div class="weighted-bar-wrap">\n'
            '  <div class="weighted-bar">\n'
            f'    <div class="weighted-bar-pros" style="width: {p_pct}%"></div>\n'
            f'    <div class="weighted-bar-cons" style="width: {c_pct}%"></div>\n'
            "  </div>\n"
            '  <div class="weighted-bar-label">\n'
            f'    <span class="pros">✅ Pros {p_pct}% · {p_count}건</span>\n'
            f'    <span class="cons">⚠️ Cons {c_pct}% · {c_count}건</span>\n'
            "  </div>\n"
            "</div>"
        )

    pros_items = (
        "\n".join(f"      <li>{p}</li>" for p in pros)
        if pros
        else '      <li><em>해당 없음</em></li>'
    )
    cons_items = (
        "\n".join(f"      <li>{c}</li>" for c in cons)
        if cons
        else '      <li><em>해당 없음</em></li>'
    )

    split_html = (
        '<div class="pros-cons-split">\n'
        '  <div class="pros-col">\n'
        '    <h5>✅ Pros</h5>\n'
        "    <ul>\n"
        f"{pros_items}\n"
        "    </ul>\n"
        "  </div>\n"
        '  <div class="cons-col">\n'
        '    <h5>⚠️ Cons</h5>\n'
        "    <ul>\n"
        f"{cons_items}\n"
        "    </ul>\n"
        "  </div>\n"
        "</div>"
    )

    example_html = ""
    if example:
        example_html = f'<div class="opt-example"><strong>📌 예시:</strong> {example}</div>'

    parts = [bar_html, split_html, example_html]
    return "\n".join(p for p in parts if p)


def render_option_card(opt):
    """옵션 detail 카드 — head + weighted bar + split + example."""
    is_rec = opt.get("recommended", False)
    rec_cls = " rec" if is_rec else ""
    star = "★ " if is_rec else ""
    label = opt.get("label", "")
    conf_html = render_confidence(opt.get("confidence"))
    detail = opt.get("detail") or {}

    body = render_pros_cons_split(detail)

    return (
        f'      <div class="opt-card{rec_cls}">\n'
        f'        <div class="opt-card-head">\n'
        f"          <h4>{star}{label}</h4>\n"
        f'          <span class="opt-conf">{conf_html}</span>\n'
        f"        </div>\n"
        f"        {body}\n"
        f"      </div>"
    )


def render_question(q):
    """Q 카드 — h2 + meta(tags) + 권장 mini + 💡 왜 + 옵션 matrix + 옵션 detail + 영향 + 선택."""
    q_id = q["id"]
    title = q.get("title", "")
    desc = q.get("desc", "")
    why = q.get("why", "")
    options = q.get("options") or []
    impact = q.get("impact") or {}
    tags = q.get("tags") or []

    rec_opt = next((o for o in options if o.get("recommended")), None)

    parts = [
        f'<section class="question" id="{q_id}" data-qid="{q_id}">',
        f"  <h2>{title}</h2>",
    ]
    if desc:
        parts.append(f'  <p class="q-desc">{desc}</p>')

    # q-meta (tag list — frameworks / 분류)
    if tags:
        tag_html = " ".join(f'<span class="tag">{esc(t)}</span>' for t in tags)
        parts.append(f'  <div class="q-meta">{tag_html}</div>')

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
        why_lines = _to_list(why)
        why_html = "\n".join(f"    <p>{line}</p>" for line in why_lines)
        parts.append(
            f'  <div class="q-why">\n'
            f'    <p class="why-title">💡 왜 이 결정 필요?</p>\n'
            f"{why_html}\n"
            f"  </div>"
        )

    # 옵션 비교 matrix
    matrix_html = render_options_matrix(options)
    if matrix_html:
        parts.append(matrix_html)

    # 옵션 detail 카드 (collapse)
    non_other_opts = [o for o in options if o.get("value") != "other"]
    if non_other_opts:
        rec_opts = [o for o in non_other_opts if o.get("recommended")]
        non_rec_opts = [o for o in non_other_opts if not o.get("recommended")]
        ordered = rec_opts + non_rec_opts
        cards = "\n".join(render_option_card(o) for o in ordered)
        parts.append(
            f'  <details class="option-details">\n'
            f"    <summary>각 옵션 자세히 (Pros/Cons split)</summary>\n"
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
    flow_section = render_flow(data)
    dashboard = render_dashboard(questions)
    questions_block = "\n\n".join(render_question(q) for q in questions)

    # Mermaid CDN — flow.mermaid / impact.mermaid 박제 시 자동 활성
    has_flow_mermaid = bool((data.get("flow") or {}).get("mermaid"))
    has_impact_mermaid = any(
        (q.get("impact") or {}).get("mermaid") for q in questions
    )
    use_mermaid = bool(data.get("use_mermaid")) or has_flow_mermaid or has_impact_mermaid
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
        "{{FLOW}}": flow_section,
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


def ensure_gitignore(output_path):
    """프로젝트의 .gitignore 에 `.claude-history/` 가 없으면 추가.

    - output_path 에서 `.claude-history` 의 부모를 프로젝트 root 후보로 잡고
    - 거기서 위로 올라가며 `.git` 디렉토리(=git root)를 찾는다.
    - git repo 가 아니면 아무것도 안 함 (불필요한 .gitignore 생성 방지).
    - 이미 `.claude-history` 를 무시하는 라인이 있으면 그대로 둔다.
    """
    try:
        output_path = Path(output_path).resolve()

        # `.claude-history` 부모 = 프로젝트 root 후보
        root = None
        for parent in output_path.parents:
            if parent.name == ".claude-history":
                root = parent.parent
                break
        if root is None:
            root = output_path.parent

        # 위로 올라가며 git root 탐색
        git_root = None
        for cand in [root, *root.parents]:
            if (cand / ".git").exists():
                git_root = cand
                break
        if git_root is None:
            return  # git repo 아님 — skip

        gitignore = git_root / ".gitignore"
        covered = {".claude-history", ".claude-history/", "/.claude-history", "/.claude-history/"}

        if gitignore.exists():
            lines = gitignore.read_text(encoding="utf-8").splitlines()
            for ln in lines:
                s = ln.strip()
                if s in covered or s.startswith(".claude-history"):
                    return  # 이미 무시됨
            # 없으면 append (끝 줄바꿈 보장)
            existing = gitignore.read_text(encoding="utf-8")
            sep = "" if existing.endswith("\n") or existing == "" else "\n"
            with gitignore.open("a", encoding="utf-8") as f:
                f.write(f"{sep}.claude-history/\n")
            sys.stderr.write(f"ℹ️  .gitignore 에 .claude-history/ 추가 ({gitignore})\n")
        else:
            gitignore.write_text(".claude-history/\n", encoding="utf-8")
            sys.stderr.write(f"ℹ️  .gitignore 생성 + .claude-history/ 추가 ({gitignore})\n")
    except Exception as e:
        # gitignore 처리 실패는 렌더 자체를 막지 않는다
        sys.stderr.write(f"warning: .gitignore 처리 실패: {e}\n")


def parse_args():
    p = argparse.ArgumentParser(description="html-decision 캔버스 렌더러 v0.7.0")
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
    ensure_gitignore(output_path)
    print(f"✅ {output_path} ({len(html.splitlines())} 줄)")


if __name__ == "__main__":
    main()
