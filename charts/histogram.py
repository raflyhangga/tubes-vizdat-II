import plotly.graph_objects as go
import pandas as pd

def build_histogram(
    airline_df: pd.DataFrame, 
    color_discrete_sequence: list | None = None
) -> go.Figure:
    """
    Bar chart of overall_rating distribution for a single airline.
    The values are divided by 2 so the visible scale becomes 1–5.
    """
    # Convert 1–10 scores to a 1–5 scale so the chart stays consistent with the others.
    ratings = (airline_df["overall_rating"].dropna().astype(float) / 2.0).round(1)
    counts = ratings.value_counts().sort_index()

    # Ensure all values from 0.5 to 5.0 are represented in 0.5 steps.
    all_index = [x / 2 for x in range(1, 11)]
    all_vals = pd.Series(0, index=all_index)
    all_vals.update(counts)

    # Use the provided palette if available (green, orange, red); otherwise use the default.
    colors = color_discrete_sequence if color_discrete_sequence else ["#26ae60", "#f39d11", "#e94c3d"]
    color_high = colors[0]   # Green
    color_medium = colors[1] # Orange
    color_low = colors[2]    # Red

    # Color bars by rating quality
    bar_colors = []
    for v in all_index:
        if v >= 4.0:
            bar_colors.append(color_high)
        elif v >= 2.5:
            bar_colors.append(color_medium)
        else:
            bar_colors.append(color_low)

    fig = go.Figure(
        go.Bar(
            x=all_index,
            y=all_vals.values,
            marker_color=bar_colors,
            hovertemplate="Rating %{x:.1f}: %{y} reviews<extra></extra>",
            name="Review Count",
        )
    )

    fig.update_layout(
        font=dict(
            family="'Source Sans 3', sans-serif",
            color="#1f2234"
        ),
        xaxis=dict(
            title=dict(
                text="Overall Rating", 
                font=dict(family="'Source Sans 3', sans-serif", size=13, color="#1f2234")
            ),
            tickvals=all_index,
            ticktext=[f"{value:g}" for value in all_index],
            tickfont=dict(
                family="'Inter', sans-serif",
                size=11, 
                color="#1f2234"
            ),
            showgrid=False
        ),
        yaxis=dict(
            title=dict(
                text="Review Count", 
                font=dict(family="'Source Sans 3', sans-serif", size=13, color="#1f2234")
            ),
            tickfont=dict(
                family="'Source Sans 3', sans-serif",
                color="#1f2234"
            ),
            gridcolor="rgba(28, 120, 187, 0.15)"
        ),
        bargap=0.1,
        margin=dict(l=25, r=15, t=20, b=30),
        height=280,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
    )
    
    return fig