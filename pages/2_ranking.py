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
from charts.podium import build_podium

# Initialize session state
defaults = {
    "filter_country": None,
    "filter_cabin": ["Economy", "Business Class", "Premium Economy", "First Class"],
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
        st.session_state["filter_country"] = filter_country
        st.session_state["filter_cabin"] = selected_cabins
        st.session_state["results_visible"] = True

# RESULTS SECTION
if st.session_state["results_visible"]:
    st.markdown('<div id="results-anchor"></div>', unsafe_allow_html=True)

    # Auto-scroll script
    components.html(
        """
        <script>
            setTimeout(function(){
                var el = window.parent.document.getElementById('results-anchor');
                if(el) el.scrollIntoView({behavior:'smooth',block:'start'});
            }, 300);
        </script>
        """,
        height=0,
    )

    # Compute scores
    ranked_df = compute_composite_scores(
        df=df,
        weights=st.session_state["score_weights"],
        cabin_filter=st.session_state["filter_cabin"],
        year_range=(2002, 2015),
        include_no_year=True,
        country_filter=st.session_state["filter_country"],
    )

    if ranked_df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter. Coba perlebar kriteria filter.")
    else:
        # PODIUM
        top3 = ranked_df.head(3).copy()
        top3["display_name"] = top3["airline_name"].apply(slug_to_display)

        st.markdown("### Podium Teratas")
        fig_podium = build_podium(top3)
        st.markdown(fig_podium, unsafe_allow_html=True)

        # Podium clickable buttons
        pcol1, pcol2, pcol3 = st.columns(3)
        podium_order = [1, 0, 2]  # Silver-Gold-Bronze
        for i, col in zip(podium_order, [pcol1, pcol2, pcol3]):
            if i < len(top3):
                row = top3.iloc[i]
                with col:
                    if st.button(
                        f"Lihat Detail: {row['display_name']}", key=f"podium_btn_{i}"
                    ):
                        st.session_state["selected_airline"] = row["airline_name"]
                        st.switch_page("pages/3_detail.py")

        # RANKING TABLE
        st.markdown("### Semua Maskapai — Ranking Lengkap")

        display_df = ranked_df.copy()
        display_df["Nama Maskapai"] = display_df["airline_name"].apply(slug_to_display)
        display_df["Skor Komposit"] = display_df["composite_score"].map("{:.3f}".format)
        display_df["Rating Rata-rata"] = display_df["avg_overall_rating"].map(
            "{:.2f}".format
        )
        display_df["% Direkomendasikan"] = display_df["pct_recommended"].map(
            "{:.1f}%".format
        )
        display_df["Jumlah Ulasan"] = display_df["review_count"]
        display_df["Rank"] = display_df["rank"]

        # Add data terbatas note
        display_df["Catatan"] = display_df["review_count"].apply(
            lambda n: "Data terbatas" if n < 10 else ""
        )

        show_cols = [
            "Rank",
            "Nama Maskapai",
            "Skor Komposit",
            "Rating Rata-rata",
            "% Direkomendasikan",
            "Jumlah Ulasan",
            "Catatan",
        ]

        selected_rows = st.dataframe(
            display_df[show_cols],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="ranking_table",
        )

        if selected_rows and selected_rows["selection"]["rows"]:
            row_idx = selected_rows["selection"]["rows"][0]
            chosen = ranked_df.iloc[row_idx]["airline_name"]
            st.session_state["selected_airline"] = chosen
            st.switch_page("pages/3_detail.py")
