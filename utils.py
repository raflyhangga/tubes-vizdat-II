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

# ============================================================================
# AIRLINE-SPECIFIC CONSTANTS & FUNCTIONS (Pages 1-4)
# ============================================================================
SUB_RATING_COLS = [
    "seat_comfort_rating",
    "cabin_staff_rating",
    "food_beverages_rating",
    "inflight_entertainment_rating",
    "value_money_rating",
]

INDUSTRY_BENCHMARK = {
    "seat_comfort_rating": 3.115,
    "cabin_staff_rating": 3.333,
    "food_beverages_rating": 2.886,
    "inflight_entertainment_rating": 2.549,
    "value_money_rating": 3.180,
}

RADAR_LABELS = {
    "seat_comfort_rating": "Seat Comfort",
    "cabin_staff_rating": "Cabin Staff",
    "food_beverages_rating": "Food & Beverages",
    "inflight_entertainment_rating": "Entertainment",
}

DISPLAY_NAME_OVERRIDES = {
    "klm-royal-dutch-airlines": "KLM Royal Dutch Airlines",
    "ana-all-nippon-airways": "ANA All Nippon Airways",
    "tap-portugal": "TAP Air Portugal",
    "sas-scandinavian-airlines": "SAS Scandinavian Airlines",
    "pia-pakistan-international-airlines": "PIA Pakistan International Airlines",
    "eva-air": "EVA Air",
    "lan-airlines": "LAN Airlines",
    "tam-airlines": "TAM Airlines",
}


def slug_to_display(slug: str) -> str:
    """Convert airline slug to human-readable display name."""
    if slug in DISPLAY_NAME_OVERRIDES:
        return DISPLAY_NAME_OVERRIDES[slug]
    return slug.replace("-", " ").title()


@st.cache_data
def _load_airline_country_map() -> dict:
    """Build a slug-to-country map from the airline_clean dataset."""
    df = load_airline_data()
    if "airline_name" not in df.columns or "airline_country" not in df.columns:
        return {}

    cleaned = (
        df[["airline_name", "airline_country"]]
        .dropna(subset=["airline_name", "airline_country"])
        .drop_duplicates(subset=["airline_name"], keep="first")
    )
    return cleaned.set_index("airline_name")["airline_country"].astype(str).to_dict()


def get_airline_country(slug: str) -> str:
    """Get the country of origin for an airline slug."""
    airline_country_map = _load_airline_country_map()
    return airline_country_map.get(slug, "Other")


def get_available_countries() -> list:
    """Return sorted list of unique countries found in the airline dataset."""
    df = load_airline_data()
    if "airline_country" not in df.columns:
        return ["Other"]
    countries = sorted(df["airline_country"].dropna().astype(str).unique().tolist())
    if "Other" not in countries:
        countries.append("Other")
    return countries


def get_airline_country_options(df: pd.DataFrame) -> list:
    """Return sorted country options inferred from airline data."""
    if "airline_country" not in df.columns:
        return ["Other"]
    values = sorted(df["airline_country"].dropna().astype(str).unique().tolist())
    if "Other" not in values:
        values.append("Other")
    return values


def normalize_recommendation_rate(recommended_series: pd.Series) -> float:
    """Return recommendation rate as a percentage."""
    if recommended_series is None or len(recommended_series) == 0:
        return 0.0
    return float(recommended_series.mean() * 100)


def calculate_weighted_row_score(
    df: pd.DataFrame,
    rating_columns: list[str],
    weights: dict,
    output_column: str = "row_composite_score",
) -> pd.DataFrame:
    """Add a weighted score column based on rating columns and normalized weights."""
    scored = df.copy()
    for column in rating_columns:
        scored[column] = pd.to_numeric(scored[column], errors="coerce")

    scored = scored.dropna(subset=rating_columns)
    if scored.empty:
        scored[output_column] = pd.Series(dtype=float)
        return scored

    scored[output_column] = sum(scored[column] * weights[column] for column in rating_columns)
    return scored


def aggregate_airline_scores(
    df: pd.DataFrame,
    rating_columns: list[str],
    weights: dict,
    group_columns: list[str] | None = None,
    min_reviews: int = 1,
    country_filter: str | None = None,
    country_column: str = "airline_country",
) -> pd.DataFrame:
    """Compute row-level weighted scores and aggregate them per airline."""
    if group_columns is None:
        group_columns = ["airline_name"]

    filtered = df.copy()
    if country_filter:
        if country_column in filtered.columns:
            filtered = filtered[filtered[country_column] == country_filter]
        elif "airline_name" in filtered.columns:
            filtered = filtered[filtered["airline_name"].map(get_airline_country) == country_filter]

    if filtered.empty:
        return pd.DataFrame()

    scored = calculate_weighted_row_score(filtered, rating_columns, weights)
    if scored.empty:
        return pd.DataFrame()

    agg_kwargs = {
        "composite_score": ("row_composite_score", "mean"),
        "review_count": (group_columns[0], "size"),
        "pct_recommended": (
            "recommended_int",
            "mean",
        )
        if "recommended_int" in scored.columns
        else (group_columns[0], "size"),
        "overall_rating": (
            "overall_rating",
            "mean",
        )
        if "overall_rating" in scored.columns
        else (group_columns[0], "size"),
    }

    groupby_cols = group_columns.copy()
    if country_column in scored.columns and country_column not in groupby_cols:
        groupby_cols.append(country_column)

    agg = scored.groupby(groupby_cols, as_index=False).agg(**agg_kwargs)
    agg = agg[agg["review_count"] >= min_reviews].copy()
    if agg.empty:
        return agg

    if "pct_recommended" in agg.columns:
        agg["pct_recommended"] = (agg["pct_recommended"] * 100).round(1)
    if "overall_rating" in agg.columns:
        agg["overall_rating"] = pd.to_numeric(agg["overall_rating"], errors="coerce").fillna(0)

    agg["composite_score"] = pd.to_numeric(agg["composite_score"], errors="coerce").fillna(0).round(3)
    agg = agg.sort_values(
        ["composite_score", "review_count", "overall_rating"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    agg["rank"] = range(1, len(agg) + 1)
    return agg


def get_airline_review_summary(df: pd.DataFrame) -> dict:
    """Return common airline summary metrics used across detail and ranking views."""
    summary = {
        "review_count": len(df),
        "avg_overall_rating": float(df["overall_rating"].mean()) if len(df) > 0 else 0.0,
        "pct_recommended": normalize_recommendation_rate(df["recommended_int"]) if "recommended_int" in df.columns else 0.0,
    }
    return summary


def get_airline_subrating_means(df: pd.DataFrame, rating_columns: list[str]) -> pd.Series:
    """Return per-column mean for the requested rating columns."""
    if len(df) == 0:
        return pd.Series({column: np.nan for column in rating_columns})
    return df[rating_columns].mean()


@st.cache_data
def load_airline_data() -> pd.DataFrame:
    """Load airline_clean.csv with appropriate dtypes."""
    df = pd.read_csv(
        "data/cleaned/airline_clean.csv",
        dtype={
            "airline_name": "string",
            "cabin_flown": "string",
            "type_traveller": "string",
            "author_country": "string",
        },
    )
    return df


def compute_composite_scores(
    df: pd.DataFrame,
    weights: dict,
    cabin_filter: list,
    year_range: tuple,
    include_no_year: bool,
    country_filter: str | None,
) -> pd.DataFrame:
    """
    Compute per-airline composite scores with weighted sub-ratings.
    Applies filters, imputes nulls with global means, and returns ranked DataFrame.
    """
    data = df.copy()

    # Cabin filter (keep nulls)
    if cabin_filter:
        data = data[
            data["cabin_flown"].isin(cabin_filter) | data["cabin_flown"].isna()
        ]

    # Year filter
    if include_no_year:
        year_mask = data["review_year"].isna() | (
            (data["review_year"] >= year_range[0])
            & (data["review_year"] <= year_range[1])
        )
    else:
        year_mask = (data["review_year"] >= year_range[0]) & (
            data["review_year"] <= year_range[1]
        )
    data = data[year_mask]

    # Country filter (airline origin)
    if country_filter:
        data["_origin"] = data["airline_name"].map(get_airline_country)
        data = data[data["_origin"] == country_filter]

    if data.empty:
        return pd.DataFrame()

    # Null imputation with global means (pre-filter)
    col_means = df[SUB_RATING_COLS].mean()
    for col in SUB_RATING_COLS:
        data[col] = data[col].fillna(col_means[col])

    # Weighted composite per row
    w = weights
    data["_composite"] = (
        w["seat"] * data["seat_comfort_rating"]
        + w["cabin"] * data["cabin_staff_rating"]
        + w["food"] * data["food_beverages_rating"]
        + w["entertainment"] * data["inflight_entertainment_rating"]
        + w["value"] * data["value_money_rating"]
    )

    # Aggregate per airline
    agg = data.groupby("airline_name", as_index=False).agg(
        composite_score=("_composite", "mean"),
        review_count=("airline_name", "count"),
        avg_overall_rating=("overall_rating", "mean"),
        pct_recommended=("recommended_int", "mean"),
        avg_seat_comfort=("seat_comfort_rating", "mean"),
        avg_cabin_staff=("cabin_staff_rating", "mean"),
        avg_food=("food_beverages_rating", "mean"),
        avg_entertainment=("inflight_entertainment_rating", "mean"),
        avg_value=("value_money_rating", "mean"),
    )

    agg["pct_recommended"] = (agg["pct_recommended"] * 100).round(1)
    agg["composite_score"] = agg["composite_score"].round(3)
    agg = agg.sort_values("composite_score", ascending=False).reset_index(drop=True)
    agg["rank"] = agg.index + 1

    return agg
