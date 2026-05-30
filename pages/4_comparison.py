import streamlit as st
import pandas as pd

from utils import (
    load_airline_data,
    SUB_RATING_COLS,
    INDUSTRY_BENCHMARK,
    get_available_countries,
    slug_to_display,
    get_airline_country,
    AIRLINE_COUNTRY_MAP,
)
from charts.radar import build_radar
from charts.boxplot import build_boxplot

# Initialize session state
defaults = {
    "filter_country": None,
    "filter_cabin": ["Economy", "Business Class", "Premium Economy", "First Class"],
    "filter_year": (2004, 2015),
    "filter_include_no_year": True,
    "score_weights": {
        "seat": 0.2,
        "cabin": 0.2,
        "food": 0.2,
        "entertainment": 0.2,
        "value": 0.2,
    },
    "results_visible": False,
    "selected_airline": None,
    "compare_airlines": [],
    "page4_country": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

df = load_airline_data()

st.title("Perbandingan Maskapai")

# TOP FILTERS
default_country = st.session_state.get("page4_country") or "United Kingdom"

countries = get_available_countries()
chosen_country = st.selectbox(
    "Negara Asal Maskapai",
    options=["(Semua negara)"] + countries,
    index=(
        (countries.index(default_country) + 1)
        if default_country in countries
        else 0
    ),
)

# Get airlines for selected country
if chosen_country == "(Semua negara)":
    country_airlines = df["airline_name"].unique().tolist()
else:
    if chosen_country == "Other":
        country_airlines = [
            a
            for a in df["airline_name"].unique()
            if a not in AIRLINE_COUNTRY_MAP
        ]
    else:
        country_airlines = [
            a
            for a in df["airline_name"].unique()
            if AIRLINE_COUNTRY_MAP.get(a) == chosen_country
        ]

# Sort by review count
vc = df["airline_name"].value_counts()
country_airlines_sorted = sorted(country_airlines, key=lambda a: -vc.get(a, 0))

# Display names for multi-select
display_options = {slug_to_display(a): a for a in country_airlines_sorted}

# Pre-select airlines from session state
pre_selected_slugs = st.session_state.get("compare_airlines", [])
pre_selected_display = [
    slug_to_display(s) for s in pre_selected_slugs if slug_to_display(s) in display_options
]

selected_display = st.multiselect(
    "Pilih maskapai untuk dibandingkan (2–6 maskapai)",
    options=list(display_options.keys()),
    default=pre_selected_display,
    max_selections=6,
)
selected_slugs = [display_options[d] for d in selected_display]

if st.button("Terapkan", type="primary"):
    st.session_state["compare_airlines"] = selected_slugs
    st.session_state["page4_country"] = (
        chosen_country if chosen_country != "(Semua negara)" else None
    )

# RESULTS
active_slugs = st.session_state.get("compare_airlines", [])
if len(active_slugs) < 2:
    st.info("Pilih minimal 2 maskapai dan tekan 'Terapkan' untuk melihat perbandingan.")
else:
    compare_df = df[df["airline_name"].isin(active_slugs)].copy()

    # Compute per-airline sub-rating means for radar
    airlines_data = {}
    for slug in active_slugs:
        sub = compare_df[compare_df["airline_name"] == slug][SUB_RATING_COLS].mean()
        airlines_data[slug_to_display(slug)] = sub.to_dict()

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("**Radar — Profil Layanan**")
        fig_radar = build_radar(
            airlines_data=airlines_data,
            benchmark=INDUSTRY_BENCHMARK,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with right_col:
        st.markdown("**Distribusi Rating Keseluruhan**")
        fig_box = build_boxplot(compare_df, active_slugs)
        st.plotly_chart(fig_box, use_container_width=True)

    # AUTO-GENERATED ANNOTATION
    st.markdown("---")
    st.markdown("**Insight Otomatis:**")
    for col_key, col_label in {
        "seat_comfort_rating": "kenyamanan kursi",
        "cabin_staff_rating": "layanan kabin",
        "food_beverages_rating": "makanan & minuman",
        "inflight_entertainment_rating": "hiburan",
        "value_money_rating": "nilai uang",
    }.items():
        best_slug = max(
            active_slugs,
            key=lambda s: compare_df[compare_df["airline_name"] == s][col_key].mean(),
        )
        best_val = (
            compare_df[compare_df["airline_name"] == best_slug][col_key].mean()
        )
        st.markdown(
            f"- **{slug_to_display(best_slug)}** unggul dalam {col_label} (rata-rata: {best_val:.2f}/5)"
        )
