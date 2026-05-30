import streamlit as st
import pandas as pd

from utils import (
    load_airline_data,
    SUB_RATING_COLS,
    INDUSTRY_BENCHMARK,
    slug_to_display,
    get_airline_country,
    get_airline_subrating_means,
    get_airline_review_summary,
)
from ui_components import kpi_circle_html, score_pill_html, recommendation_callout_html
from charts.radar import build_radar
from charts.histogram import build_histogram

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
    "selected_airline_score": None,
    "compare_airlines": [],
    "page4_country": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Guard
if not st.session_state.get("selected_airline"):
    st.warning("Tidak ada maskapai yang dipilih. Kembali ke halaman ranking.")
    if st.button("Kembali ke Ranking"):
        st.switch_page("pages/2_ranking.py")
    st.stop()

df = load_airline_data()
slug = st.session_state["selected_airline"]
airline_df = df[df["airline_name"] == slug].copy()

if airline_df.empty:
    st.error(f"Data untuk '{slug}' tidak ditemukan.")
    st.stop()

display_name = slug_to_display(slug)
home_country = get_airline_country(slug)
ranking_score = st.session_state.get("selected_airline_score")
summary = get_airline_review_summary(airline_df)
total_reviews = summary["review_count"]
year_min = (
    int(airline_df["review_year"].dropna().min())
    if airline_df["review_year"].notna().any()
    else "N/A"
)
year_max = (
    int(airline_df["review_year"].dropna().max())
    if airline_df["review_year"].notna().any()
    else "N/A"
)

# HEADER
st.markdown(f"## {display_name}")
st.caption(f"{home_country} · {total_reviews:,} ulasan · {year_min}–{year_max}")

if ranking_score is not None:
    st.markdown(score_pill_html(float(ranking_score)), unsafe_allow_html=True)

st.divider()

col1, col2, col3, col4 = st.columns(4)
sub_means = get_airline_subrating_means(airline_df, SUB_RATING_COLS)
kpi_data = [
    ("Kenyamanan Kursi", sub_means.get("seat_comfort_rating")),
    ("Layanan Kabin", sub_means.get("cabin_staff_rating")),
    ("Makanan & Minuman", sub_means.get("food_beverages_rating")),
    ("Hiburan", sub_means.get("inflight_entertainment_rating")),
]
for col, (label, val) in zip([col1, col2, col3, col4], kpi_data):
    with col:
        st.markdown(kpi_circle_html(label, val), unsafe_allow_html=True)

st.divider()

# ROW 2: Radar + Histogram
radar_col, hist_col = st.columns(2)

with radar_col:
    st.markdown("**Profil Rating Sub-Dimensi**")
    fig_radar = build_radar(
        airlines_data={display_name: sub_means.to_dict()},
        benchmark=INDUSTRY_BENCHMARK,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with hist_col:
    st.markdown("**Distribusi Rating Keseluruhan**")
    fig_hist = build_histogram(airline_df)
    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ROW 3: Recommendation + Value KPI + Button
r3col1, r3col2, r3col3 = st.columns([2, 1, 1])

with r3col1:
    pct_rec = summary["pct_recommended"]
    st.markdown(recommendation_callout_html(pct_rec), unsafe_allow_html=True)

with r3col2:
    val_mean = airline_df["value_money_rating"].mean()
    st.markdown(kpi_circle_html("Nilai Uang", val_mean), unsafe_allow_html=True)

with r3col3:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Bandingkan dengan maskapai lain →", type="primary", use_container_width=True):
        st.session_state["page4_country"] = home_country
        st.session_state["compare_airlines"] = [slug]
        st.switch_page("pages/4_comparison.py")
