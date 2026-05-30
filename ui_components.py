import pandas as pd


PODIUM_STYLES = {
    1: ("🥇", "#FFD700", "linear-gradient(135deg, #FFD700, #FFA500)", 200, "#1"),
    2: ("🥈", "#C0C0C0", "linear-gradient(135deg, #C0C0C0, #A8A8A8)", 160, "#2"),
    3: ("🥉", "#CD7F32", "linear-gradient(135deg, #CD7F32, #A0522D)", 130, "#3"),
}


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
        <div style="font-size:1rem;color:#666">Penumpang merekomendasikan maskapai ini</div>
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


def build_podium(top3_df: pd.DataFrame) -> str:
    """
    Returns an HTML string for the podium visualization.
    Visual order: Silver(2nd) | Gold(1st) | Bronze(3rd)
    """
    visual_order = []
    for target_rank in [2, 1, 3]:
        row = top3_df[top3_df["rank"] == target_rank]
        if not row.empty:
            visual_order.append(row.iloc[0])
        else:
            visual_order.append(None)

    cards = []
    for row in visual_order:
        if row is None:
            cards.append('<div style="flex:1"></div>')
            continue

        rank = int(row["rank"])
        medal, border_color, bg_grad, height, rank_label = PODIUM_STYLES[rank]
        name = row["display_name"]
        score = row["composite_score"]
        pct = row["pct_recommended"]

        name_size = "1.1rem" if rank == 1 else "0.95rem"
        score_size = "1.3rem" if rank == 1 else "1.1rem"

        card_html = (
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;margin:0 8px;">'
            f'<div style="font-size:2rem;margin-bottom:0.5rem">{medal}</div>'
            f'<div style="background:{bg_grad};border:2px solid {border_color};border-radius:12px 12px 0 0;'
            f'padding:1.5rem 1rem;width:100%;height:{height}px;display:flex;flex-direction:column;'
            f'align-items:center;justify-content:center;box-shadow:0 4px 15px rgba(0,0,0,0.1);text-align:center;">'
            f'<div style="font-size:2rem;font-weight:800;color:rgba(0,0,0,0.3);line-height:1;">{rank_label}</div>'
            f'<div style="font-size:{name_size};font-weight:700;color:#1a1a1a;margin-top:0.5rem;line-height:1.2;">{name}</div>'
            f'<div style="font-size:{score_size};font-weight:800;color:#1a1a1a;margin-top:0.3rem;">{score:.3f}</div>'
            f'<div style="font-size:0.75rem;color:rgba(0,0,0,0.6);margin-top:0.2rem;">{pct:.0f}% direkomendasikan</div>'
            f'</div></div>'
        )
        cards.append(card_html)

    podium_html = (
        '<div style="display:flex;align-items:flex-end;justify-content:center;width:100%;padding:1rem 0;min-height:280px;">'
        f"{''.join(cards)}"
        '</div>'
    )
    return podium_html