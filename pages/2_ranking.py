import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from utils import (
    load_airline_data,
    compute_composite_scores,
    get_available_countries,
    slug_to_display,
    triple_range_slider,
)
from charts.choropleth import build_airline_origin_choropleth

# Initialize session state
defaults = {
    "filter_country": None,
    "filter_cabin": ["Economy", "Business Class", "Premium Economy", "First Class"],
    "ranking_min_reviews": 30,
    "score_weights": {
        "seat": 0.25,
        "cabin": 0.25,
        "food": 0.25,
        "entertainment": 0.25,
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

st.title("Temukan Maskapai Terbaik")
st.caption(
    "Sesuaikan preferensimu, lalu tekan 'Terapkan Filter' untuk melihat ranking."
)

# FILTER SECTION
col1, col2 = st.columns(2)

with col1:
    countries = get_available_countries()
    selected_country = st.selectbox(
        "Negara Asal Maskapai",
        options=["(Semua negara)"] + countries,
        index=0,
        help="Filter maskapai berdasarkan negara asal mereka",
    )
    filter_country = (
        None if selected_country == "(Semua negara)" else selected_country
    )

with col2:
    cabin_options = [
        "Economy",
        "Business Class",
        "Premium Economy",
        "First Class",
    ]
    selected_cabins = st.multiselect(
        "Kelas Kabin",
        options=cabin_options,
        default=st.session_state["filter_cabin"],
    )

min_reviews = st.number_input(
    "Minimal review valid per maskapai",
    min_value=1,
    max_value=1000,
    value=int(st.session_state.get("ranking_min_reviews", 30)),
    step=1,
    help="Maskapai dengan review di bawah angka ini tidak akan ditampilkan di halaman ranking berikutnya.",
)

# WEIGHT SLIDERS
st.markdown("### Seberapa penting kriteria ini bagimu?")

current_weights = st.session_state["score_weights"]
default_point_1 = int(current_weights["seat"] * 100)
default_point_2 = default_point_1 + int(current_weights["cabin"] * 100)
default_point_3 = default_point_2 + int(current_weights["food"] * 100)

slider_result = triple_range_slider(
    label="",
    default_points=(default_point_1, default_point_2, default_point_3)
)

ranges = slider_result.get("ranges", {})
weight_inputs = {
    "seat": ranges.get("var_1", 25),
    "cabin": ranges.get("var_2", 25),
    "food": ranges.get("var_3", 25),
    "entertainment": ranges.get("var_4", 25),
}

# Display weight breakdown
criteria_labels = ["Kenyamanan Kursi", "Layanan Kabin", "Makanan & Minuman", "Hiburan"]
weight_cols = st.columns(4)
for i, label in enumerate(criteria_labels):
    with weight_cols[i]:
        st.metric(label, f"{weight_inputs[list(weight_inputs.keys())[i]]}%")

total_weight = sum(weight_inputs.values())
apply_disabled = total_weight != 100

# APPLY BUTTON
if st.button("Terapkan Filter", type="primary", disabled=apply_disabled):
    if total_weight == 100:
        normalized_weights = {k: v / 100.0 for k, v in weight_inputs.items()}
        st.session_state["score_weights"] = normalized_weights
        st.session_state["ranking_weights"] = {
            "seat_comfort_rating": normalized_weights["seat"],
            "cabin_staff_rating": normalized_weights["cabin"],
            "food_beverages_rating": normalized_weights["food"],
            "inflight_entertainment_rating": normalized_weights["entertainment"],
        }
        st.session_state["filter_country"] = filter_country
        st.session_state["filter_cabin"] = selected_cabins
        st.session_state["ranking_country"] = filter_country
        st.session_state["ranking_min_reviews"] = int(min_reviews)
        st.switch_page("pages/2a_ranking.py")

# AIRLINE ORIGIN MAP (always visible, independent of filters)
st.markdown("### Peta Persebaran Data")
fig_choropleth = build_airline_origin_choropleth(df)
if fig_choropleth:
    st.plotly_chart(
        fig_choropleth,
        use_container_width=True,
        config={"scrollZoom": False, "displayModeBar": False},
    )

