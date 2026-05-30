import plotly.graph_objects as go

RADAR_AXIS_LABELS = [
    "Seat Comfort",
    "Cabin Staff",
    "Food & Beverages",
    "Entertainment",
]
RADAR_COL_KEYS = [
    "seat_comfort_rating",
    "cabin_staff_rating",
    "food_beverages_rating",
    "inflight_entertainment_rating",
]

AIRLINE_COLORS = [
    "#2ecc71",
    "#3498db",
    "#e74c3c",
    "#9b59b6",
    "#f39c12",
    "#1abc9c",
]


def build_radar(airlines_data: dict, benchmark: dict | None = None) -> go.Figure:
    """
    Build a radar chart for one or more airlines.

    airlines_data: dict mapping display name -> dict of col_key -> mean_value
    benchmark: dict of col_key -> global_mean (drawn as dashed line if provided)
    """
    fig = go.Figure()

    # Plot each airline
    for i, (name, values) in enumerate(airlines_data.items()):
        r_values = [values.get(k, 0) for k in RADAR_COL_KEYS]
        r_values_closed = r_values + [r_values[0]]
        theta_closed = RADAR_AXIS_LABELS + [RADAR_AXIS_LABELS[0]]

        color = AIRLINE_COLORS[i % len(AIRLINE_COLORS)]
        fig.add_trace(
            go.Scatterpolar(
                r=r_values_closed,
                theta=theta_closed,
                fill="toself",
                fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)",
                line=dict(color=color, width=2),
                name=name,
                hovertemplate="%{theta}: %{r:.2f}/5<extra>" + name + "</extra>",
            )
        )

    # Plot industry benchmark as dashed line
    if benchmark:
        b_values = [benchmark.get(k, 0) for k in RADAR_COL_KEYS]
        b_values_closed = b_values + [b_values[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=b_values_closed,
                theta=RADAR_AXIS_LABELS + [RADAR_AXIS_LABELS[0]],
                fill="none",
                line=dict(color="#888888", width=1.5, dash="dash"),
                name="Rata-rata Industri",
                hovertemplate="%{theta}: %{r:.2f}/5<extra>Rata-rata Industri</extra>",
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                tickfont=dict(size=10),
                gridcolor="#e0e0e0",
            ),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.12, font=dict(size=10)),
        margin=dict(l=25, r=25, t=20, b=35),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
