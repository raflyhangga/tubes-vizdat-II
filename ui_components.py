import pandas as pd


def score_bar_html(score: float, max_score: float = 5.0) -> str:
    pct = max(0.0, min((score / max_score) * 100.0, 100.0))
    return f"""
    <div style="display:flex;align-items:center;gap:0.55rem;min-width:140px;">
        <div style="flex:1;height:8px;border-radius:999px;background:rgba(255,255,255,0.08);overflow:hidden;">
            <div style="width:{pct:.1f}%;height:100%;border-radius:999px;background:linear-gradient(90deg,#2f86c5,#66b6ff);"></div>
        </div>
        <div style="min-width:42px;font-weight:700;color:#f3f3f3;">{score:.2f}</div>
    </div>
    """


def review_count_badge(count: int, min_reviews: int) -> str:
    if count >= 100:
        color = "#7ad36b"
    elif count >= min_reviews:
        color = "#f0a23a"
    else:
        color = "#8a8a8a"
    return f"<span style='display:inline-flex;align-items:center;gap:0.35rem;'><span style='width:7px;height:7px;border-radius:999px;background:{color};display:inline-block;'></span>{count:,}</span>"


def kpi_circle_html(label: str, value: float | None) -> str:
    if value is None or pd.isna(value):
        color = "#999999"
        display = "N/A"
    else:
        display = f"{value:.2f}"
        if value >= 4.0:
            color = "#27ae60"
        elif value >= 3.0:
            color = "#f39c12"
        elif value >= 2.0:
            color = "#e67e22"
        else:
            color = "#e74c3c"

    return f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 0.5rem;
    ">
        <div style="
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background-color: {color};
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.6rem;
            font-weight: 700;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">{display}</div>
        <div style="
            margin-top: 0.5rem;
            font-size: 0.8rem;
            text-align: center;
            color: #444;
            max-width: 100px;
        ">{label}</div>
    </div>
    """


def rating_gauge_html(label: str, value: float | None, color: str) -> str:
    if value is None or pd.isna(value):
        value = 0.0
    percent = max(0.0, min(float(value) / 5.0, 1.0))
    track_color = "rgba(255,255,255,0.08)"
    fill_angle = percent * 360.0
    value_text = f"{float(value):.1f}"
    pct_text = f"{percent * 100:.0f}%"

    return f"""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(255,255,255,0.04);border-radius:14px;padding:0.7rem 0.65rem;min-height:110px;'>
        <div style='position:relative;width:76px;height:76px;border-radius:50%;background:conic-gradient({color} 0deg {fill_angle:.1f}deg, {track_color} {fill_angle:.1f}deg 360deg);box-shadow:inset 0 0 0 1px rgba(255,255,255,0.06);'>
            <div style='position:absolute;inset:10px;border-radius:50%;background:rgba(22,22,22,0.96);display:flex;align-items:center;justify-content:center;flex-direction:column;border:1px solid rgba(255,255,255,0.08);'>
                <div style='font-size:1.0rem;font-weight:900;color:{color};line-height:1;text-shadow:0 0 0.5px {color};'>{value_text}</div>
                <div style='margin-top:0.08rem;font-size:0.68rem;font-weight:700;color:#d6d6d6;letter-spacing:0.02em;'>{pct_text}</div>
            </div>
        </div>
        <div style='margin-top:0.35rem;font-size:0.78rem;font-weight:700;color:#bdbdbd;text-align:center;'>{label}</div>
    </div>
    """


def detail_header_html(display_name: str, home_country: str, cabin_text: str, review_count: int, badge_text: str = "") -> str:
    badge_html = f"<div style='display:inline-flex;align-items:center;padding:0.25rem 0.55rem;border-radius:999px;background:rgba(26, 115, 21, 0.75);color:#b6ff9f;font-size:0.82rem;font-weight:800;'>{badge_text}</div>" if badge_text else ""
    avatar = ''.join([part[0] for part in display_name.split()[:2]]).upper()[:2]
    return f"""
    <div style='display:flex;align-items:center;justify-content:space-between;gap:0.8rem;padding:0.7rem 0.9rem;border:1px solid rgba(255,255,255,0.08);border-radius:15px;background:rgba(255,255,255,0.03);box-shadow:0 10px 22px rgba(0,0,0,0.16);'>
        <div style='display:flex;align-items:center;gap:0.75rem;min-width:0;'>
            <div style='width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#f0f5ff,#dce8ff);color:#233b73;display:flex;align-items:center;justify-content:center;font-size:0.98rem;font-weight:900;flex:0 0 auto;'>{avatar}</div>
            <div style='min-width:0;'>
                <div style='font-size:1.2rem;line-height:1.05;font-weight:900;color:#f5f5f5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{display_name}</div>
                <div style='margin-top:0.15rem;font-size:0.84rem;color:#bfc7d5;font-weight:600;'>{home_country} · {cabin_text} · {review_count:,} reviews</div>
            </div>
        </div>
        <div style='display:flex;align-items:center;gap:0.75rem;flex:0 0 auto;'>
            {badge_html}
        </div>
    </div>
    """


def section_banner_html(primary_text: str, secondary_text: str, accent_color: str = "#ff9f43", tertiary_text: str | None = None) -> str:
    tertiary_html = ""
    if tertiary_text:
        tertiary_html = f'<div style="color:#a9cfff;font-size:0.85rem;margin-top:0.45rem;">{tertiary_text}</div>'

    return f"""
    <div style="padding:0.85rem 1rem;border-left:4px solid {accent_color};background:rgba(255,159,67,0.10);border-radius:0.85rem;margin:0.25rem 0 1rem 0;">
        <div style="font-weight:800;color:#f2f2f2;font-size:1rem;">{primary_text}</div>
        <div style="color:#cfcfcf;font-size:0.92rem;line-height:1.45;margin-top:0.3rem;">
            {secondary_text}
        </div>
        {tertiary_html}
    </div>
    """


def section_hint_html(text: str) -> str:
    return f"<div style='color:#d0d0d0;margin-top:-0.15rem;margin-bottom:0.5rem;'>{text}</div>"


def section_description_html(text: str) -> str:
    return f"<div style='color:#d0d0d0;margin-top:-0.15rem;margin-bottom:0.8rem;'>{text}</div>"


def thin_divider_html() -> str:
    return "<div style='height:1px;background:rgba(255,255,255,0.06);margin:0.1rem 0 0.2rem 0;'></div>"


def rank_pill_html(rank: int) -> str:
    return f"<div style='padding-top:0.25rem;font-weight:700;color:#f0f0f0;'>{rank}</div>"


def recommendation_callout_html(pct_recommended: float) -> str:
    rec_color = "#27ae60" if pct_recommended >= 70 else "#e74c3c"
    return f"""
    <div style="text-align:center">
        <div style="font-size:3.5rem;font-weight:800;color:{rec_color}">{pct_recommended:.0f}%</div>
        <div style="font-size:1rem;color:#666">Passengers recommend this airline</div>
    </div>
    """


def score_pill_html(score: float, label: str = "Skor komposit dari ranking") -> str:
    return f"""
    <div style="display:inline-flex;align-items:center;gap:0.6rem;padding:0.5rem 0.8rem;border-radius:999px;background:rgba(47,134,197,0.16);color:#f5f5f5;font-weight:700;margin-bottom:0.5rem;">
        {label}: {score:.3f}
    </div>
    """


def table_header_cell_html(title: str) -> str:
    return f"<div style='font-size:0.85rem;font-weight:700;color:#bdbdbd;border-bottom:1px solid rgba(255,255,255,0.12);padding-bottom:0.45rem;margin-bottom:0.4rem;'>{title}</div>"


def table_text_cell_html(text: str, color: str = "#d4d4d4", bold: bool = False, pad_top: str = "0.25rem", line_height: str = "1.25") -> str:
    weight = "700" if bold else "400"
    return f"<div style='padding-top:{pad_top};color:{color};font-weight:{weight};line-height:{line_height};'>{text}</div>"