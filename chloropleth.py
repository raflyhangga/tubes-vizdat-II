import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="DuniaMaskapai",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSTANTS
# ============================================================================
COUNTRY_NAME_MAP = {
    "Russian Federation": "Russia",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "Wallis & Futuna Islands": "Wallis and Futuna",
    "Macedonia": "North Macedonia",
    "East Timor": "Timor-Leste",
    "Palestinian Territories": "Palestine",
    "Hong Kong": "China",
    "Netherlands Antilles": None,
}

METRIC_COL = {
    "Review Count": "review_count",
    "Avg Overall Rating": "avg_overall_rating",
    "Recommendation Rate (%)": "recommendation_rate",
}

# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and clean the consolidated reviews dataset."""
    df = pd.read_csv(
        "data/cleaned/reviews_consolidated.csv",
        parse_dates=["date"]
    )
    df["author_country"] = df["author_country"].replace(COUNTRY_NAME_MAP)
    df = df[df["author_country"].notna() & (df["author_country"].str.strip() != "")]
    return df

# ============================================================================
# FILTERING FUNCTION
# ============================================================================
def apply_global_filters(
    df: pd.DataFrame,
    review_type_list: list,
    year_range: tuple,
    cabin_flown_list: list,
    type_traveller_list: list,
    author_country_list: list,
) -> pd.DataFrame:
    """
    Apply all sidebar filters to the dataframe.
    Returns a filtered copy ready for aggregation into any chart.
    """
    filtered = df.copy()

    # Review type filter
    if review_type_list:
        filtered = filtered[filtered["review_type"].isin(review_type_list)]

    # Year range filter
    filtered = filtered[
        (filtered["review_year"] >= year_range[0]) &
        (filtered["review_year"] <= year_range[1])
    ]

    # Cabin flown filter (only applies to airline reviews and if column exists)
    if cabin_flown_list and "airline" in review_type_list and "cabin_flown" in filtered.columns:
        filtered = filtered[filtered["cabin_flown"].isin(cabin_flown_list)]

    # Traveller type filter (only if column exists)
    if type_traveller_list and "type_traveller" in filtered.columns:
        filtered = filtered[filtered["type_traveller"].isin(type_traveller_list)]

    # Reviewer country filter
    if author_country_list:
        filtered = filtered[filtered["author_country"].isin(author_country_list)]

    return filtered

# ============================================================================
# CHOROPLETH AGGREGATION FUNCTION
# ============================================================================
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

# ============================================================================
# LOAD DATA
# ============================================================================
df = load_data()

# ============================================================================
# PAGE HEADER
# ============================================================================
st.title("🌍 Skytrax Reviews Dashboard")
st.caption(
    "Analyze airline, airport, lounge, and seat reviews from the Skytrax platform (2015). "
    "Use the filters below to explore reviewer countries, ratings, and trends."
)

# ============================================================================
# SIDEBAR — GLOBAL FILTERS
# ============================================================================
st.sidebar.header("📊 Filters")

# Review Type Multiselect
review_types = st.sidebar.multiselect(
    "Review Type",
    options=["All", "airline", "airport", "lounge", "seat"],
    default=["All"],
    help="Select review categories to include"
)
if "All" in review_types or not review_types:
    review_type_filter = df["review_type"].unique().tolist()
else:
    review_type_filter = review_types

# Year Range Slider
year_min_data = int(df["review_year"].min())
year_max_data = int(df["review_year"].max())
year_range = st.sidebar.slider(
    "Year Range",
    min_value=year_min_data,
    max_value=year_max_data,
    value=(year_min_data, year_max_data),
    help="Filter reviews by publication year"
)

# Cabin Flown (Airline-specific — only in airline_clean.csv, not in consolidated)
cabin_flown = []
if "cabin_flown" in df.columns:
    cabin_options = sorted([x for x in df["cabin_flown"].dropna().unique() if pd.notna(x)])
    cabin_flown = st.sidebar.multiselect(
        "Cabin Class (Airline only)",
        options=cabin_options,
        default=cabin_options,
        help="Only applies to airline reviews"
    )
else:
    st.sidebar.info("ℹ️ Cabin Class filter unavailable in consolidated view. Use airline_clean.csv for detailed analysis.")

# Traveller Type (sparse across categories — not in consolidated)
type_traveller = []
if "type_traveller" in df.columns:
    traveller_options = sorted([x for x in df["type_traveller"].dropna().unique() if pd.notna(x)])
    type_traveller = st.sidebar.multiselect(
        "Traveller Type",
        options=traveller_options,
        default=traveller_options,
        help="Filter by traveller type (sparse data)"
    )
else:
    st.sidebar.info("ℹ️ Traveller Type filter unavailable in consolidated view.")

# Reviewer Country
country_options = sorted([x for x in df["author_country"].dropna().unique() if pd.notna(x)])
author_country = st.sidebar.multiselect(
    "Reviewer Country",
    options=country_options,
    default=country_options,
    help="Filter by reviewer's country of origin"
)

# Choropleth Metric Radio
choropleth_metric = st.sidebar.radio(
    "Choropleth Color Metric",
    options=["Review Count", "Avg Overall Rating", "Recommendation Rate (%)"],
    help="Which metric to visualize on the map"
)

# ============================================================================
# APPLY GLOBAL FILTERS
# ============================================================================
filtered_data = apply_global_filters(
    df,
    review_type_filter,
    year_range,
    cabin_flown,
    type_traveller,
    author_country
)

# ============================================================================
# KPI STRIP
# ============================================================================
st.subheader("📈 Dashboard Overview")
col1, col2, col3, col4 = st.columns(4)

total_reviews = len(filtered_data)
avg_rating = filtered_data["overall_rating"].mean() if len(filtered_data) > 0 else np.nan
pct_recommended = (filtered_data["recommended_int"].mean() * 100) if len(filtered_data) > 0 else 0
unique_entities = filtered_data["entity_name"].nunique() if "entity_name" in filtered_data.columns else 0

with col1:
    st.metric("Total Reviews", f"{total_reviews:,}")
with col2:
    st.metric("Avg Overall Rating", f"{avg_rating:.2f}/10" if pd.notna(avg_rating) else "N/A")
with col3:
    st.metric("% Recommended", f"{pct_recommended:.1f}%")
with col4:
    st.metric("Entities Covered", f"{unique_entities:,}")

st.divider()

# ============================================================================
# CHOROPLETH MAP
# ============================================================================
st.subheader("🗺️ Reviewer Geographic Distribution")

if len(filtered_data) > 0:
    agg = aggregate_for_choropleth(filtered_data)
    color_col = METRIC_COL[choropleth_metric]

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
        title=f"{choropleth_metric} by Reviewer Country",
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
    st.subheader("📊 Top 15 Reviewer Countries")

    top15 = agg.nlargest(15, "review_count")[
        ["author_country", "review_count", "avg_overall_rating", "recommendation_rate"]
    ].rename(columns={
        "author_country": "Country",
        "review_count": "Reviews",
        "avg_overall_rating": "Avg Rating",
        "recommendation_rate": "Recommended %",
    }).reset_index(drop=True)

    st.dataframe(top15, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ No data matches the selected filters. Try adjusting the filter criteria.")
