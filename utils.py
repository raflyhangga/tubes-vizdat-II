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
    "value_money_rating": "Value for Money",
}

AIRLINE_COUNTRY_MAP = {
    "spirit-airlines": "United States",
    "united-airlines": "United States",
    "american-airlines": "United States",
    "delta-air-lines": "United States",
    "frontier-airlines": "United States",
    "southwest-airlines": "United States",
    "jetblue-airways": "United States",
    "us-airways": "United States",
    "hawaiian-airlines": "United States",
    "alaska-airlines": "United States",
    "virgin-america": "United States",
    "allegiant-air": "United States",
    "british-airways": "United Kingdom",
    "virgin-atlantic-airways": "United Kingdom",
    "easyjet": "United Kingdom",
    "thomson-airways": "United Kingdom",
    "monarch-airlines": "United Kingdom",
    "flybe": "United Kingdom",
    "thomas-cook-airlines": "United Kingdom",
    "jet2-com": "United Kingdom",
    "air-canada-rouge": "Canada",
    "air-canada": "Canada",
    "sunwing-airlines": "Canada",
    "air-transat": "Canada",
    "porter-airlines": "Canada",
    "jet-airways": "India",
    "air-india": "India",
    "indigo-airlines": "India",
    "emirates": "United Arab Emirates",
    "etihad-airways": "United Arab Emirates",
    "lufthansa": "Germany",
    "air-berlin": "Germany",
    "condor-airlines": "Germany",
    "germanwings": "Germany",
    "ryanair": "Ireland",
    "aer-lingus": "Ireland",
    "qantas-airways": "Australia",
    "virgin-australia": "Australia",
    "jetstar-airways": "Australia",
    "tigerair": "Australia",
    "turkish-airlines": "Turkey",
    "pegasus-airlines": "Turkey",
    "cathay-pacific-airways": "Hong Kong",
    "dragonair": "Hong Kong",
    "qatar-airways": "Qatar",
    "malaysia-airlines": "Malaysia",
    "airasia": "Malaysia",
    "airasia-x": "Malaysia",
    "norwegian": "Norway",
    "singapore-airlines": "Singapore",
    "silkair": "Singapore",
    "scoot": "Singapore",
    "tap-portugal": "Portugal",
    "finnair": "Finland",
    "klm-royal-dutch-airlines": "Netherlands",
    "iberia": "Spain",
    "vueling-airlines": "Spain",
    "air-europa": "Spain",
    "thai-airways": "Thailand",
    "bangkok-airways": "Thailand",
    "garuda-indonesia": "Indonesia",
    "lion-air": "Indonesia",
    "batik-air": "Indonesia",
    "air-france": "France",
    "swiss-international-air-lines": "Switzerland",
    "air-new-zealand": "New Zealand",
    "korean-air": "South Korea",
    "asiana-airlines": "South Korea",
    "vietnam-airlines": "Vietnam",
    "philippine-airlines": "Philippines",
    "cebu-pacific": "Philippines",
    "austrian-airlines": "Austria",
    "icelandair": "Iceland",
    "lan-airlines": "Chile",
    "tam-airlines": "Brazil",
    "avianca": "Colombia",
    "aeromexico": "Mexico",
    "aerolineas-argentinas": "Argentina",
    "copa-airlines": "Panama",
    "ana-all-nippon-airways": "Japan",
    "japan-airlines": "Japan",
    "south-african-airways": "South Africa",
    "china-southern-airlines": "China",
    "china-eastern-airlines": "China",
    "air-china": "China",
    "hainan-airlines": "China",
    "aeroflot-russian-airlines": "Russia",
    "ethiopian-airlines": "Ethiopia",
    "kenya-airways": "Kenya",
    "brussels-airlines": "Belgium",
    "eva-air": "Taiwan",
    "china-airlines": "Taiwan",
    "egyptair": "Egypt",
    "sas-scandinavian-airlines": "Sweden",
    "aegean-airlines": "Greece",
    "el-al-israel-airlines": "Israel",
    "gulf-air": "Bahrain",
    "oman-air": "Oman",
    "kuwait-airways": "Kuwait",
    "royal-jordanian-airlines": "Jordan",
    "saudi-arabian-airlines": "Saudi Arabia",
    "air-mauritius": "Mauritius",
    "royal-air-maroc": "Morocco",
    "pia-pakistan-international-airlines": "Pakistan",
    "lot-polish-airlines": "Poland",
    "airbaltic": "Latvia",
    "wizz-air": "Hungary",
    "ukraine-international-airlines": "Ukraine",
    "air-astana": "Kazakhstan",
    "fiji-airways": "Fiji",
    "srilankan-airlines": "Sri Lanka",
    "royal-brunei-airlines": "Brunei",
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


def get_airline_country(slug: str) -> str:
    """Get the country of origin for an airline slug."""
    return AIRLINE_COUNTRY_MAP.get(slug, "Other")


def get_available_countries() -> list:
    """Return sorted list of unique countries, plus 'Other'."""
    return sorted(set(AIRLINE_COUNTRY_MAP.values())) + ["Other"]


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
    )

    agg["pct_recommended"] = (agg["pct_recommended"] * 100).round(1)
    agg["composite_score"] = agg["composite_score"].round(3)
    agg = agg.sort_values("composite_score", ascending=False).reset_index(drop=True)
    agg["rank"] = agg.index + 1

    return agg


def triple_range_slider(
    label: str = "Pilih 3 titik",
    default_points: tuple[int, int, int] = (25, 50, 75),
    key: str | None = None,
) -> dict:
    from typing import Any

    HTML = """
<div class="tri-slider">
  <div class="tri-slider__header">
    <div class="tri-slider__title"></div>
  </div>

  <div class="tri-slider__track-area">
    <div class="tri-slider__track"></div>
    <div class="tri-slider__fill"></div>

    <input class="tri-slider__input" data-handle="1" type="range" min="0" max="100" step="1" />
    <input class="tri-slider__input" data-handle="2" type="range" min="0" max="100" step="1" />
    <input class="tri-slider__input" data-handle="3" type="range" min="0" max="100" step="1" />
  </div>
</div>
"""

    CSS = """
.tri-slider {
  font-family: inherit;
  display: grid;
  gap: 0.9rem;
  padding: 0.25rem 0 0.5rem;
}

.tri-slider__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.tri-slider__title {
  font-size: 1rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
}

.tri-slider__track-area {
  position: relative;
  height: 3.2rem;
  display: flex;
  align-items: center;
}

.tri-slider__track,
.tri-slider__fill {
  position: absolute;
  left: 0;
  right: 0;
  height: 0.55rem;
  border-radius: 999px;
}

.tri-slider__track {
  background: rgba(255, 255, 255, 0.12);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.04);
}

.tri-slider__fill {
  background: linear-gradient(90deg, #10b981 0%, #f59e0b 50%, #ef4444 100%);
  opacity: 0.9;
}

.tri-slider__input {
  position: absolute;
  left: 0;
  width: 100%;
  margin: 0;
  pointer-events: none;
  background: transparent;
  -webkit-appearance: none;
  appearance: none;
}

.tri-slider__input::-webkit-slider-runnable-track {
  height: 0.55rem;
  background: transparent;
}

.tri-slider__input::-moz-range-track {
  height: 0.55rem;
  background: transparent;
  border: 0;
}

.tri-slider__input::-webkit-slider-thumb {
  pointer-events: auto;
  -webkit-appearance: none;
  appearance: none;
  width: 1.15rem;
  height: 1.15rem;
  border-radius: 50%;
  border: 2px solid #ffffff;
  background: #0f172a;
  box-shadow: 0 0.35rem 1rem rgba(15, 23, 42, 0.35);
  cursor: grab;
  margin-top: -0.3rem;
}

.tri-slider__input::-moz-range-thumb {
  pointer-events: auto;
  width: 1.15rem;
  height: 1.15rem;
  border-radius: 50%;
  border: 2px solid #ffffff;
  background: #0f172a;
  box-shadow: 0 0.35rem 1rem rgba(15, 23, 42, 0.35);
  cursor: grab;
}
"""

    JS = """
function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function normalizePoints(values) {
  const first = clamp(values[0], 0, 100);
  const second = clamp(values[1], first, 100);
  const third = clamp(values[2], second, 100);
  return [first, second, third];
}

function computeRanges(points) {
  const [first, second, third] = points;
  return {
    var_1: first,
    var_2: second - first,
    var_3: third - second,
    var_4: 100 - third,
    total: 100,
  };
}

export default function(component) {
  const { parentElement, data, setStateValue } = component;
  const title = parentElement.querySelector('.tri-slider__title');
  const fill = parentElement.querySelector('.tri-slider__fill');
  const inputs = Array.from(parentElement.querySelectorAll('.tri-slider__input'));

  title.textContent = data?.label ?? 'Slider 3 Titik';

  const defaults = Array.isArray(data?.points) && data.points.length === 3
    ? data.points
    : [25, 50, 75];

  const initial = normalizePoints(defaults.map(Number));

  inputs.forEach((input, index) => {
    input.value = String(initial[index]);
  });

  function render() {
    const points = normalizePoints(inputs.map((input) => Number(input.value)));

    inputs.forEach((input, index) => {
      input.value = String(points[index]);
    });

    const ranges = computeRanges(points);
    const [first, second, third] = points;

    fill.style.left = '0%';
    fill.style.width = `${third}%`;

    setStateValue('value', {
      points: {
        first,
        second,
        third,
      },
      ranges,
    });
  }

  inputs.forEach((input) => {
    input.addEventListener('input', render);
    input.addEventListener('change', render);
  });

  render();
}
"""

    tri_slider = st.components.v2.component(
        "triple_range_slider",
        html=HTML,
        css=CSS,
        js=JS,
    )

    result = tri_slider(
        key=key,
        data={"label": label, "points": list(default_points)},
        default={
            "value": {
                "points": {
                    "first": default_points[0],
                    "second": default_points[1],
                    "third": default_points[2],
                },
                "ranges": {
                    "var_1": default_points[0],
                    "var_2": default_points[1] - default_points[0],
                    "var_3": default_points[2] - default_points[1],
                    "var_4": 100 - default_points[2],
                    "total": 100,
                },
            }
        },
        on_value_change=lambda: None,
    )

    if result.value is None:
        return {
            "points": {
                "first": default_points[0],
                "second": default_points[1],
                "third": default_points[2],
            },
            "ranges": {
                "var_1": default_points[0],
                "var_2": default_points[1] - default_points[0],
                "var_3": default_points[2] - default_points[1],
                "var_4": 100 - default_points[2],
                "total": 100,
            },
        }

    return result.value
