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
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig


def build_single_airline_subrating_boxplot(df: pd.DataFrame, airline_slug: str, rating_columns: list[str]) -> go.Figure:
    """Build a subrating boxplot for a single airline across its review data."""
    fig = go.Figure()
    color = AIRLINE_COLORS[0]

    for col in rating_columns:
        values = df[col].dropna()
        fig.add_trace(
            go.Box(
                y=values,
                name=col.replace("_", " ").title(),
                marker_color=color,
                boxmean="sd",
                hovertemplate=(
                    f"<b>{slug_to_display(airline_slug)}</b><br>"
                    f"{col.replace('_', ' ').title()}: %{{median:.2f}}<br>"
                    "Q1–Q3: %{q1:.2f}–%{q3:.2f}<br>"
                    "Min–Max: %{lowerfence:.2f}–%{upperfence:.2f}" "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        yaxis=dict(title="Nilai Rating", range=[0, 5]),
        xaxis=dict(title="Subrating"),
        showlegend=False,
        margin=dict(l=40, r=20, t=40, b=60),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig


def build_comparison_subrating_boxplots(df: pd.DataFrame, airline_slugs: list[str], rating_columns: list[str]) -> list[go.Figure]:
    """Build a list of boxplots comparing airlines across each rating column."""
    figs = []
    for col in rating_columns:
        fig = go.Figure()
        for i, slug in enumerate(airline_slugs):
            values = df[df["airline_name"] == slug][col].dropna()
            color = AIRLINE_COLORS[i % len(AIRLINE_COLORS)]
            fig.add_trace(
                go.Box(
                    y=values,
                    name=slug_to_display(slug),
                    marker_color=color,
                    boxmean="sd",
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        f"{col.replace('_', ' ').title()}: %{{median:.2f}}<br>"
                        "Q1–Q3: %{q1:.2f}–%{q3:.2f}<br>"
                        "Min–Max: %{lowerfence:.2f}–%{upperfence:.2f}" "<extra></extra>"
                    ),
                )
            )

        fig.update_layout(
            yaxis=dict(title="Nilai Rating", range=[0, 5]),
            xaxis=dict(title="Maskapai"),
            showlegend=False,
            margin=dict(l=40, r=20, t=40, b=60),
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title_text=col.replace("_", " ").title(),
            title_x=0.5,
        )
        fig.update_yaxes(gridcolor="#e8e8e8")
        figs.append(fig)

    return figs
