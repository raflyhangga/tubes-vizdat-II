import streamlit as st
import pandas as pd

from utils import (
    load_airline_data,
    SUB_RATING_COLS,
    INDUSTRY_BENCHMARK,
    slug_to_display,
    get_airline_country,
)
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
total_reviews = len(airline_df)
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

st.divider()

# ROW 1: 4 KPI Circles
def render_kpi_circle(label, value):
    """Returns HTML string for a colored circle KPI."""
    if value is None or pd.isna(value):
        color = "#999999"
        display = "N/A"
    else:
        display = f"{value:.2f}"
        if value >= 4.0:
            color = "#27ae60"  # green
        elif value >= 3.0:
            color = "#f39c12"  # yellow
        elif value >= 2.0:
            color = "#e67e22"  # orange
        else:
            color = "#e74c3c"  # red

    return f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 0.5rem;
    ">
        <div style="
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background-color: {color};
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.6rem;
            font-weight: 700;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">{display}</div>
        <div style="
            margin-top: 0.5rem;
            font-size: 0.8rem;
            text-align: center;
            color: #444;
            max-width: 100px;
        ">{label}</div>
    </div>
    """


col1, col2, col3, col4 = st.columns(4)
sub_means = airline_df[SUB_RATING_COLS].mean()
kpi_data = [
    ("Kenyamanan Kursi", sub_means.get("seat_comfort_rating")),
    ("Layanan Kabin", sub_means.get("cabin_staff_rating")),
    ("Makanan & Minuman", sub_means.get("food_beverages_rating")),
    ("Hiburan", sub_means.get("inflight_entertainment_rating")),
]
for col, (label, val) in zip([col1, col2, col3, col4], kpi_data):
    with col:
        st.markdown(render_kpi_circle(label, val), unsafe_allow_html=True)

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
    pct_rec = airline_df["recommended_int"].mean() * 100
    rec_color = "#27ae60" if pct_rec >= 70 else "#e74c3c"
    st.markdown(
        f"""
    <div style="text-align:center">
        <div style="font-size:3.5rem;font-weight:800;color:{rec_color}">{pct_rec:.0f}%</div>
        <div style="font-size:1rem;color:#666">Penumpang merekomendasikan maskapai ini</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with r3col2:
    val_mean = airline_df["value_money_rating"].mean()
    st.markdown(render_kpi_circle("Nilai Uang", val_mean), unsafe_allow_html=True)

with r3col3:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Bandingkan dengan maskapai lain →", type="primary", use_container_width=True):
        st.session_state["page4_country"] = home_country
        st.session_state["compare_airlines"] = [slug]
        st.switch_page("pages/4_comparison.py")
