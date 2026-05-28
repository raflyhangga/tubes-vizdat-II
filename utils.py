import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

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

DATA_DIR = Path("data/cleaned")
REVIEW_SOURCE_FILES = [
    ("airline", "airline_clean.csv", "airline_name_clean"),
    ("airport", "airport_clean.csv", "airport_name_clean"),
    ("lounge", "lounge_clean.csv", "lounge_name"),
    ("seat", "seat_clean.csv", "airline_name_clean"),
]

# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and clean the full reviews dataset with category-specific fields."""
    frames = []

    for review_type, filename, entity_column in REVIEW_SOURCE_FILES:
        frame = pd.read_csv(DATA_DIR / filename, parse_dates=["date"])
        frame["review_type"] = review_type
        frame["entity_name"] = frame[entity_column] if entity_column in frame.columns else pd.NA
        frame["author_country"] = frame["author_country"].replace(COUNTRY_NAME_MAP)
        frames.append(frame)

    df = pd.concat(frames, ignore_index=True, sort=False)
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
    if not review_type_list:
        return df.iloc[0:0].copy()

    filtered = df.copy()

    # Review type filter
    if review_type_list:
        filtered = filtered[filtered["review_type"].isin(review_type_list)]

    # Year range filter
    filtered = filtered[
        (filtered["review_year"] >= year_range[0]) &
        (filtered["review_year"] <= year_range[1])
    ]

    # Cabin flown filter
    if cabin_flown_list and "cabin_flown" in filtered.columns:
        filtered = filtered[filtered["cabin_flown"].isin(cabin_flown_list)]

    # Traveller type filter
    if type_traveller_list and "type_traveller" in filtered.columns:
        filtered = filtered[filtered["type_traveller"].isin(type_traveller_list)]

    # Reviewer country filter
    if author_country_list:
        filtered = filtered[filtered["author_country"].isin(author_country_list)]

    return filtered

# ============================================================================
# KPI CALCULATIONS
# ============================================================================
def calculate_kpis(filtered_data: pd.DataFrame) -> dict:
    """Calculate KPI metrics for the dashboard overview."""
    total_reviews = len(filtered_data)
    avg_rating = filtered_data["overall_rating"].mean() if len(filtered_data) > 0 else np.nan
    pct_recommended = (filtered_data["recommended_int"].mean() * 100) if len(filtered_data) > 0 else 0
    unique_entities = filtered_data["entity_name"].nunique() if "entity_name" in filtered_data.columns else 0

    return {
        "total_reviews": total_reviews,
        "avg_rating": avg_rating,
        "pct_recommended": pct_recommended,
        "unique_entities": unique_entities,
    }
