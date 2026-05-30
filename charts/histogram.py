import plotly.graph_objects as go
import pandas as pd


def build_histogram(airline_df: pd.DataFrame) -> go.Figure:
    """
    Bar chart of overall_rating distribution for a single airline.
    Uses bins 1–10 with color coding.
    """
    ratings = airline_df["overall_rating"].dropna()
    counts = ratings.value_counts().sort_index()

    # Ensure all values 1–10 are represented
    all_vals = pd.Series(0, index=range(1, 11))
    all_vals.update(counts)

    # Color bars by rating quality
    bar_colors = []
    for v in range(1, 11):
        if v >= 8:
            bar_colors.append("#27ae60")  # green
        elif v >= 5:
            bar_colors.append("#f39c12")  # amber
        else:
            bar_colors.append("#e74c3c")  # red

    fig = go.Figure(
        go.Bar(
            x=list(range(1, 11)),
            y=all_vals.values,
            marker_color=bar_colors,
            hovertemplate="Rating %{x}: %{y} ulasan<extra></extra>",
            name="Jumlah Ulasan",
        )
    )

    fig.update_layout(
        xaxis=dict(
            title="Rating Keseluruhan",
            tickvals=list(range(1, 11)),
            ticktext=[str(i) for i in range(1, 11)],
        ),
        yaxis=dict(title="Jumlah Ulasan"),
        bargap=0.1,
        margin=dict(l=25, r=15, t=20, b=30),
        height=280,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig
