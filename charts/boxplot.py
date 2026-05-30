import plotly.graph_objects as go
import pandas as pd

from utils import slug_to_display

AIRLINE_COLORS = [
    "#2ecc71",
    "#3498db",
    "#e74c3c",
    "#9b59b6",
    "#f39c12",
    "#1abc9c",
]


def build_boxplot(df: pd.DataFrame, airline_slugs: list) -> go.Figure:
    """
    Box plot of overall_rating for multiple airlines.
    One box per airline, sorted by median descending.
    """
    # Sort by median
    medians = {
        slug: df[df["airline_name"] == slug]["overall_rating"].median()
        for slug in airline_slugs
    }
    sorted_slugs = sorted(airline_slugs, key=lambda s: -medians.get(s, 0))

    fig = go.Figure()
    for i, slug in enumerate(sorted_slugs):
        airline_data = df[df["airline_name"] == slug]["overall_rating"].dropna()
        color = AIRLINE_COLORS[i % len(AIRLINE_COLORS)]
        fig.add_trace(
            go.Box(
                y=airline_data,
                name=slug_to_display(slug),
                marker_color=color,
                boxmean="sd",
                hovertemplate=(
                    "<b>" + slug_to_display(slug) + "</b><br>"
                    "Median: %{median:.1f}<br>"
                    "Q1–Q3: %{q1:.1f}–%{q3:.1f}<br>"
                    "Min–Max: %{lowerfence:.1f}–%{upperfence:.1f}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        yaxis=dict(title="Rating Keseluruhan (1–10)", range=[0, 11]),
        xaxis=dict(title="Maskapai"),
        showlegend=False,
        margin=dict(l=40, r=20, t=30, b=60),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig
