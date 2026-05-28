import streamlit as st
import pandas as pd
import numpy as np

from utils import load_data, apply_global_filters, calculate_kpis
from charts.choropleth import build_choropleth, build_top15_table

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="DuniaMaskapai",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Cabin Flown (Airline-specific)
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

# Traveller Type
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

kpis = calculate_kpis(filtered_data)

with col1:
    st.metric("Total Reviews", f"{kpis['total_reviews']:,}")
with col2:
    st.metric("Avg Overall Rating", f"{kpis['avg_rating']:.2f}/10" if pd.notna(kpis['avg_rating']) else "N/A")
with col3:
    st.metric("% Recommended", f"{kpis['pct_recommended']:.1f}%")
with col4:
    st.metric("Entities Covered", f"{kpis['unique_entities']:,}")

st.divider()

# ============================================================================
# CHOROPLETH MAP
# ============================================================================
st.subheader("🗺️ Reviewer Geographic Distribution")

if len(filtered_data) > 0:
    fig = build_choropleth(filtered_data, choropleth_metric)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    # ============================================================================
    # TOP-15 COUNTRIES TABLE
    # ============================================================================
    st.subheader("📊 Top 15 Reviewer Countries")

    top15 = build_top15_table(filtered_data)
    if not top15.empty:
        st.dataframe(top15, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ No data matches the selected filters. Try adjusting the filter criteria.")
