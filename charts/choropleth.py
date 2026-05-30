import pandas as pd
import plotly.express as px
from utils import METRIC_COL, get_airline_country


def aggregate_for_choropleth(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare country-level aggregations for the choropleth map."""
    if len(filtered_df) == 0:
        return pd.DataFrame(columns=["author_country", "review_count", "avg_overall_rating", "recommendation_rate"])

    agg = filtered_df.groupby("author_country", as_index=False).agg(
        review_count=("author_country", "count"),
        avg_overall_rating=("overall_rating", "mean"),
        recommendation_rate=("recommended_int", "mean"),
    )
    agg["recommendation_rate"] = (agg["recommendation_rate"] * 100).round(1)
    agg["avg_overall_rating"] = agg["avg_overall_rating"].round(2)
    return agg


def build_choropleth(filtered_data: pd.DataFrame, metric: str) -> px.choropleth:
    """
    Build and return a choropleth map figure.

    Args:
        filtered_data: The filtered DataFrame to visualize
        metric: The metric to color by (e.g., "Review Count", "Avg Overall Rating")

    Returns:
        A Plotly choropleth figure
    """
    if len(filtered_data) == 0:
        return None

    agg = aggregate_for_choropleth(filtered_data)
    color_col = METRIC_COL[metric]

    fig = px.choropleth(
        agg,
        locations="author_country",
        locationmode="country names",
        color=color_col,
        color_continuous_scale="Blues",
        labels={
            "review_count": "Reviews",
            "avg_overall_rating": "Avg Rating (1–10)",
            "recommendation_rate": "Recommended (%)",
            "author_country": "Country",
        },
        title=f"{metric} by Reviewer Country",
        hover_name="author_country",
        hover_data={
            "review_count": ":,",
            "avg_overall_rating": ":.2f",
            "recommendation_rate": ":.1f",
            "author_country": False,
        },
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
        ),
        height=600,
    )
    return fig


def build_top15_table(filtered_data: pd.DataFrame) -> pd.DataFrame:
    """
    Build a top-15 countries table.

    Args:
        filtered_data: The filtered DataFrame to aggregate

    Returns:
        A formatted DataFrame for display
    """
    if len(filtered_data) == 0:
        return pd.DataFrame()

    agg = aggregate_for_choropleth(filtered_data)
    top15 = agg.nlargest(15, "review_count")[
        ["author_country", "review_count", "avg_overall_rating", "recommendation_rate"]
    ].rename(columns={
        "author_country": "Country",
        "review_count": "Reviews",
        "avg_overall_rating": "Avg Rating",
        "recommendation_rate": "Recommended %",
    }).reset_index(drop=True)

    return top15


def build_airline_origin_choropleth(airline_data: pd.DataFrame) -> px.choropleth:
    """
    Build a choropleth map showing airline origin countries.

    Args:
        airline_data: The raw airline reviews DataFrame

    Returns:
        A Plotly choropleth figure
    """
    if len(airline_data) == 0:
        return None

    data = airline_data.copy()
    data["origin_country"] = data["airline_name"].apply(get_airline_country)

    agg = data.groupby("origin_country", as_index=False).agg(
        num_airlines=("airline_name", "nunique"),
        total_reviews=("airline_name", "size"),
    ).rename(columns={
        "origin_country": "country"
    })

    fig = px.choropleth(
        agg,
        locations="country",
        locationmode="country names",
        color="total_reviews",
        color_continuous_scale="Blues",
        labels={
            "total_reviews": "Total Reviews",
            "num_airlines": "Airlines",
            "country": "Country",
        },
        hover_name="country",
        hover_data={
            "num_airlines": True,
            "total_reviews": ":,",
            "country": False,
        },
        title="",
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Airlines: %{customdata[1]}<br>Total Reviews: %{customdata[2]:,}<extra></extra>",
        customdata=agg[["country", "num_airlines", "total_reviews"]].values,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
        ),
        height=500,
    )

    return fig
