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

DEFAULT_COLORS = [
    "#1c78bb",  # Blue (primary / selected airline)
    "#f39d11",  # Orange (for the first comparison airline)
    "#26ae60",  # Green (for the second comparison airline)
    "#9b59b6",  # Purple (for the third comparison airline)
    "#e94c3d",  # Red
]

def build_radar(
    airlines_data: dict, 
    benchmark: dict | None = None,
    color_discrete_sequence: list | None = None
) -> go.Figure:
    """
    Build a radar chart for one or more airlines.

    airlines_data: dict mapping display name -> dict of col_key -> mean_value
    benchmark: dict of col_key -> global_mean (drawn as dashed line if provided)
    color_discrete_sequence: list of hex colors to override defaults (ignored so the radar stays blue)
    """
    fig = go.Figure()
    
    colors = DEFAULT_COLORS

    for i, (name, values) in enumerate(airlines_data.items()):
        r_values = [values.get(k, 0) for k in RADAR_COL_KEYS]
        r_values_closed = r_values + [r_values[0]]
        theta_closed = RADAR_AXIS_LABELS + [RADAR_AXIS_LABELS[0]]

        color = colors[i % len(colors)]
        
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        
        fig.add_trace(
            go.Scatterpolar(
                r=r_values_closed,
                theta=theta_closed,
                fill="toself",
                fillcolor=f"rgba({r},{g},{b},0.2)",
                line=dict(color=color, width=2.5),
                name=name,
                hovertemplate="%{theta}: %{r:.2f}/5<extra>" + name + "</extra>",
            )
        )

    # Plot the industry average as a dashed line.
    if benchmark:
        b_values = [benchmark.get(k, 0) for k in RADAR_COL_KEYS]
        b_values_closed = b_values + [b_values[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=b_values_closed,
                theta=RADAR_AXIS_LABELS + [RADAR_AXIS_LABELS[0]],
                fill="none",
                line=dict(color="#888888", width=1.5, dash="dash"),
                name="Industry Average",
                hovertemplate="%{theta}: %{r:.2f}/5<extra>Industry Average</extra>",
            )
        )

    fig.update_layout(
        font=dict(
            family="'Source Sans 3', sans-serif",
            color="#1f2234"
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                tickfont=dict(size=10, color="#1f2234"),
                gridcolor="rgba(28, 120, 187, 0.2)",
            ),
            angularaxis=dict(
                tickfont=dict(
                    size=12, 
                    family="'Inter', sans-serif",
                    color="#1f2234"
                ),
                gridcolor="rgba(28, 120, 187, 0.2)",
            ),
            bgcolor="rgba(255, 255, 255, 0.4)",
        ),
        showlegend=True,
        legend=dict(
            orientation="h", 
            y=-0.15, 
            font=dict(size=11, family="'Source Sans 3', sans-serif")
        ),
        margin=dict(l=25, r=25, t=20, b=35),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig