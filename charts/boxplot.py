import plotly.graph_objects as go
import pandas as pd

from utils import slug_to_display

DEFAULT_AIRLINE_COLOR = "#86c7f3"
AIRLINE_COLORS = [
    "#b2e278",
    "#ffb2c0",
    "#fecd72",
]


def _get_airline_color(index: int) -> str:
    return DEFAULT_AIRLINE_COLOR if index == 0 else AIRLINE_COLORS[(index - 1) % len(AIRLINE_COLORS)]


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
        color = _get_airline_color(i)
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
        font=dict(color="#1f2234"),
        yaxis=dict(title=dict(text="Rating Keseluruhan (1–10)", font=dict(color="#1f2234")), range=[0, 11], tickfont=dict(color="#1f2234")),
        xaxis=dict(title=dict(text="Maskapai", font=dict(color="#1f2234")), tickfont=dict(color="#1f2234")),
        showlegend=False,
        margin=dict(l=40, r=20, t=30, b=60),
        height=300,
        paper_bgcolor="#f5f7fa",
        plot_bgcolor="#f5f7fa",
    )
    fig.update_yaxes(gridcolor="#d1d5db")
    return fig


def build_single_airline_subrating_boxplot(df: pd.DataFrame, airline_slug: str, rating_columns: list[str]) -> go.Figure:
    """Build a subrating boxplot for a single airline across its review data."""
    fig = go.Figure()
    color = DEFAULT_AIRLINE_COLOR

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
        font=dict(color="#1f2234"),
        yaxis=dict(title=dict(text="Nilai Rating", font=dict(color="#1f2234")), range=[0, 5], tickfont=dict(color="#1f2234")),
        xaxis=dict(title=dict(text="Subrating", font=dict(color="#1f2234")), tickfont=dict(color="#1f2234")),
        showlegend=False,
        margin=dict(l=40, r=20, t=40, b=60),
        height=300,
        paper_bgcolor="#f5f7fa",
        plot_bgcolor="#f5f7fa",
    )
    fig.update_yaxes(gridcolor="#d1d5db")
    return fig


def _pretty_boxplot_title(column_name: str) -> str:
    title = column_name.replace("_", " ").title()
    if title.endswith(" Rating"):
        return title.replace(" Rating", "<br>Rating")
    return title


def build_comparison_subrating_boxplots(df: pd.DataFrame, airline_slugs: list[str], rating_columns: list[str]) -> list[go.Figure]:
    """Build a list of boxplots comparing airlines across each rating column."""
    figs = []
    for col in rating_columns:
        fig = go.Figure()
        for i, slug in enumerate(airline_slugs):
            values = df[df["airline_name"] == slug][col].dropna()
            color = _get_airline_color(i)
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
            font=dict(color="#1f2234"),
            yaxis=dict(title=dict(text="Nilai Rating", font=dict(color="#1f2234")), range=[0, 5], tickfont=dict(color="#1f2234")),
            xaxis=dict(title=dict(text="Maskapai", font=dict(color="#1f2234")), automargin=True, tickfont=dict(color="#1f2234")),
            showlegend=False,
            margin=dict(l=40, r=20, t=70, b=60),
            height=340,
            paper_bgcolor="#f5f7fa",
            plot_bgcolor="#f5f7fa",
            title=dict(
                text=_pretty_boxplot_title(col),
                x=0.5,
                xanchor="center",
                y=0.95,
                yanchor="top",
                font=dict(color="#1f2234", size=13),
            ),
        )
        fig.update_yaxes(gridcolor="#d1d5db")
        figs.append(fig)

    return figs
