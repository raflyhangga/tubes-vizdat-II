import pandas as pd

PODIUM_STYLES = {
    1: ("🥇", "#FFD700", "linear-gradient(135deg, #FFD700, #FFA500)", 200, "#1"),
    2: ("🥈", "#C0C0C0", "linear-gradient(135deg, #C0C0C0, #A8A8A8)", 160, "#2"),
    3: ("🥉", "#CD7F32", "linear-gradient(135deg, #CD7F32, #A0522D)", 130, "#3"),
}


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

        # Center (rank 1) gets larger text
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
