import streamlit as st
import pandas as pd
import plotly.express as px
from utils import METRIC_COL


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


def build_choropleth(filtered_data: pd.DataFrame, metric: str) -> None:
    """Render the choropleth map and top-15 table section."""
    # ============================================================================
    # CHOROPLETH MAP
    # ============================================================================
    st.subheader("Reviewer Geographic Distribution")

    if len(filtered_data) == 0:
        return

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
    st.plotly_chart(fig, use_container_width=True)

    # ============================================================================
    # TOP-15 COUNTRIES TABLE
    # ============================================================================
    st.subheader("Top 15 Reviewer Countries")

    top15 = agg.nlargest(15, "review_count")[
        ["author_country", "review_count", "avg_overall_rating", "recommendation_rate"]
    ].rename(columns={
        "author_country": "Country",
        "review_count": "Reviews",
        "avg_overall_rating": "Avg Rating",
        "recommendation_rate": "Recommended %",
    }).reset_index(drop=True)

    st.dataframe(top15, use_container_width=True, hide_index=True)
