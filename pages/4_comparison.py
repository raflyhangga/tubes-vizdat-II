import streamlit as st
import pandas as pd

from utils import (
    load_airline_data,
    SUB_RATING_COLS,
    INDUSTRY_BENCHMARK,
    get_airline_country,
    get_airline_country_options,
    slug_to_display,
    get_airline_subrating_means,
)
from charts.radar import build_radar
from charts.boxplot import (
    build_single_airline_subrating_boxplot,
    build_comparison_subrating_boxplots,
)

st.set_page_config(page_title="Perbandingan Maskapai", layout="wide")

df = load_airline_data()

st.title("Perbandingan Maskapai")
st.markdown(
    "Pilih negara, pilih beberapa maskapai, lalu tekan **Terapkan** untuk melihat perbandingan radar dan boxplot."
)

# -----------------------------------------------------------------------------
# Controls data
# -----------------------------------------------------------------------------
default_country = st.session_state.get("page4_country") or "United Kingdom"

countries = get_airline_country_options(df)
vc = df["airline_name"].value_counts()

default_country_name = st.session_state.get("page4_country") or default_country

if default_country_name == "(Semua negara)":
    default_country_airlines = df["airline_name"].unique().tolist()
else:
    default_country_airlines = [
        a for a in df["airline_name"].unique()
        if get_airline_country(a) == default_country_name
    ]

default_country_airlines_sorted = sorted(
    default_country_airlines,
    key=lambda a: -vc.get(a, 0)
)

default_single_slug = (
    default_country_airlines_sorted[0]
    if default_country_airlines_sorted
    else None
)

page4_applied = st.session_state.get("page4_applied", False)
active_slugs = st.session_state.get("compare_airlines", [])

active_df = (
    df[df["airline_name"].isin(active_slugs)]
    if active_slugs
    else pd.DataFrame()
)

# -----------------------------------------------------------------------------
# Layout
# -----------------------------------------------------------------------------
left_col, right_col = st.columns([1.5, 1], gap="large")

with left_col:
    st.markdown("#### Radar Perbandingan Maskapai")

    if active_slugs:
        airlines_data = {
            slug_to_display(slug): get_airline_subrating_means(
                active_df[active_df["airline_name"] == slug],
                SUB_RATING_COLS
            ).to_dict()
            for slug in active_slugs
        }

        fig_radar = build_radar(
            airlines_data=airlines_data,
            benchmark=INDUSTRY_BENCHMARK
        )

        st.plotly_chart(fig_radar, use_container_width=True)

    else:
        st.info("Pilih maskapai lalu tekan Terapkan untuk melihat radar perbandingan.")

    if not page4_applied:
        current_selected = st.session_state.get("compare_airlines", [])
        single_slug = current_selected[0] if current_selected else default_single_slug

        if single_slug:
            st.markdown("#### Boxplot Subrating Maskapai Default")

            single_df = df[df["airline_name"] == single_slug]

            fig_single = build_single_airline_subrating_boxplot(
                single_df,
                single_slug,
                SUB_RATING_COLS
            )

            st.plotly_chart(fig_single, use_container_width=True)

    st.markdown("---")
    st.markdown("### Perbandingan 4 Subrating")

    if len(active_slugs) >= 2:
        figures = build_comparison_subrating_boxplots(
            active_df,
            active_slugs,
            SUB_RATING_COLS
        )

        cols = st.columns(4, gap="small")

        for fig, col in zip(figures, cols):
            col.plotly_chart(fig, use_container_width=True)

    elif active_slugs:
        st.info("Tambahkan setidaknya satu maskapai lagi untuk melihat perbandingan antar maskapai.")

    else:
        st.info("Pilih maskapai dan tekan Terapkan untuk menampilkan perbandingan boxplot.")

with right_col:
    if page4_applied:
        display_country = st.session_state.get("page4_country") or "(Semua negara)"
        selected_slugs = st.session_state.get("compare_airlines", [])

        st.markdown("**Filter diterapkan**")
        st.write(f"- Negara: {display_country}")

        if selected_slugs:
            st.write("- Maskapai:")
            for slug in selected_slugs:
                st.write(f"  - {slug_to_display(slug)} ({get_airline_country(slug)})")
        else:
            st.info("Tidak ada maskapai terpilih.")

        if st.button("Ubah", key="page4_edit_button"):
            st.session_state["page4_applied"] = False
            st.rerun()

    else:
        chosen_country = st.selectbox(
            "Negara Asal Maskapai",
            options=["(Semua negara)"] + countries,
            index=(countries.index(default_country) + 1)
            if default_country in countries
            else 0,
            key="page4_chosen_country",
        )

        if chosen_country == "(Semua negara)":
            country_airlines = df["airline_name"].unique().tolist()
        else:
            country_airlines = [
                a for a in df["airline_name"].unique()
                if get_airline_country(a) == chosen_country
            ]

        country_airlines_sorted = sorted(
            country_airlines,
            key=lambda a: -vc.get(a, 0)
        )

        display_options = {
            slug_to_display(a): a
            for a in country_airlines_sorted
        }

        pre_selected_slugs = st.session_state.get("compare_airlines", [])

        pre_selected_display = [
            slug_to_display(s)
            for s in pre_selected_slugs
            if slug_to_display(s) in display_options
        ]

        selected_display = st.multiselect(
            "Pilih maskapai untuk dibandingkan (2–6 maskapai)",
            options=list(display_options.keys()),
            default=pre_selected_display,
            max_selections=6,
            key="page4_selected_display",
        )

        selected_slugs = [
            display_options[d]
            for d in selected_display
        ]

        if st.button("Terapkan", type="primary", key="page4_apply_button"):
            st.session_state["compare_airlines"] = selected_slugs
            st.session_state["page4_country"] = (
                chosen_country
                if chosen_country != "(Semua negara)"
                else None
            )
            st.session_state["page4_applied"] = True

            st.rerun()