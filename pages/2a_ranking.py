import html

import pandas as pd
import streamlit as st

from ui_components import (
    build_podium,
    table_header_cell_html,
    table_text_cell_html,
    review_count_badge,
    score_bar_html,
    section_banner_html,
    section_description_html,
    section_hint_html,
    thin_divider_html,
    rank_pill_html,
)
from utils import load_airline_data, slug_to_display
from utils import aggregate_airline_scores, get_airline_country_options


RATING_COLS = [
    "seat_comfort_rating",
    "cabin_staff_rating",
    "food_beverages_rating",
    "inflight_entertainment_rating",
]

RATING_LABELS = {
    "seat_comfort_rating": "Seat Comfort",
    "cabin_staff_rating": "Cabin Staff",
    "food_beverages_rating": "Food & Beverages",
    "inflight_entertainment_rating": "Entertainment",
}

DEFAULT_WEIGHT_BY_COL = {
    "seat_comfort_rating": 0.25,
    "cabin_staff_rating": 0.25,
    "food_beverages_rating": 0.25,
    "inflight_entertainment_rating": 0.25,
}

SESSION_DEFAULTS = {
    "ranking_country": None,
    "ranking_min_reviews": 30,
    "ranking_weights": DEFAULT_WEIGHT_BY_COL,
    "selected_airline": None,
    "selected_airline_score": None,
    "compare_airlines": [],
    "page4_country": None,
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def _init_weights() -> dict:
    current = st.session_state.get("ranking_weights") or {}
    if all(col in current for col in RATING_COLS):
        weights = {col: float(current[col]) for col in RATING_COLS}
    else:
        legacy = st.session_state.get("score_weights", {})
        weights = {
            "seat_comfort_rating": float(legacy.get("seat", DEFAULT_WEIGHT_BY_COL["seat_comfort_rating"])),
            "cabin_staff_rating": float(legacy.get("cabin", DEFAULT_WEIGHT_BY_COL["cabin_staff_rating"])),
            "food_beverages_rating": float(legacy.get("food", DEFAULT_WEIGHT_BY_COL["food_beverages_rating"])),
            "inflight_entertainment_rating": float(legacy.get("entertainment", DEFAULT_WEIGHT_BY_COL["inflight_entertainment_rating"])),
        }

    total = sum(weights.values())
    if total <= 0:
        return DEFAULT_WEIGHT_BY_COL.copy()
    return {col: value / total for col, value in weights.items()}


def render_detail_button(airline_name: str, score: float, key: str) -> None:
    if st.button("Detail →", key=key, use_container_width=True):
        st.session_state["selected_airline"] = airline_name
        st.session_state["selected_airline_score"] = float(score)
        st.switch_page("pages/3_detail.py")


st.set_page_config(page_title="Ranking Maskapai", page_icon="✈️", layout="wide")

df = load_airline_data()
weights = _init_weights()
country_options = get_airline_country_options(df)
selected_country_value = st.session_state.get("ranking_country")
if selected_country_value not in country_options:
    selected_country_value = None

min_reviews = int(st.session_state.get("ranking_min_reviews", 30))

st.session_state["ranking_country"] = selected_country_value
st.session_state["ranking_min_reviews"] = int(min_reviews)
st.session_state["ranking_weights"] = weights

st.title("Ranking Maskapai")
country_label = selected_country_value or "Semua negara"
st.caption(
    f"Podium berada di kiri. Tabel lengkap dengan detail berada di kanan. Filter aktif: {country_label} · minimal {int(min_reviews)} review valid."
)

active_weight_label = sorted(weights, key=lambda key: weights[key], reverse=True)[0]
active_weight_text = RATING_LABELS[active_weight_label]
weight_summary = " · ".join(
    f"{RATING_LABELS[col]} {weights[col] * 100:.0f}%" for col in RATING_COLS
)

st.markdown(
    section_banner_html(
        primary_text=f"Kamu mementingkan {html.escape(active_weight_text.lower())} paling tinggi.",
        secondary_text=(
            "Skor komposit dihitung per baris dari bobot yang diwariskan, lalu dirata-ratakan per maskapai. "
            f"Maskapai yang tampil wajib punya minimal {int(min_reviews)} review valid setelah filter negara diterapkan."
        ),
        tertiary_text=f"Bobot aktif: {html.escape(weight_summary)}",
    ),
    unsafe_allow_html=True,
)

ranked_df = aggregate_airline_scores(
    df=df,
    rating_columns=RATING_COLS,
    weights=weights,
    group_columns=["airline_name"],
    country_filter=selected_country_value,
    min_reviews=int(min_reviews),
)

if ranked_df.empty:
    st.warning("Tidak ada maskapai yang memenuhi filter negara dan batas minimum review valid.")
    st.stop()

left_col, right_col = st.columns([1.05, 1.7], gap="large")

top3 = ranked_df.head(3).copy()
top3["display_name"] = top3["airline_name"].apply(slug_to_display)

with left_col:
    st.markdown("**Podium Teratas**")
    st.markdown(section_hint_html("Klik kartu atau tombol detail untuk membuka halaman maskapai."), unsafe_allow_html=True)
    podium_html = build_podium(top3)
    st.markdown(podium_html, unsafe_allow_html=True)

    btn_cols = st.columns(3)
    podium_order = [1, 0, 2]
    for slot, col in zip(podium_order, btn_cols):
        with col:
            if slot < len(top3):
                row = top3.iloc[slot]
                render_detail_button(
                    row["airline_name"],
                    row["composite_score"],
                    key=f"podium_detail_{int(row['rank'])}",
                )

    st.markdown(
        section_description_html(
            "Urutan podium mengikuti skor komposit tertinggi. Angka pada kartu adalah skor komposit rata-rata per maskapai setelah perhitungan baris valid."
        ),
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown("**Daftar Lengkap Maskapai**")
    st.markdown(
        section_description_html(
            "Maskapai, negara, skor komposit, jumlah ulasan, persentase rekomendasi, overall rating, dan tombol detail."
        ),
        unsafe_allow_html=True,
    )

    header_cols = st.columns([0.35, 2.3, 1.3, 1.65, 1.1, 1.2, 1.1, 0.9])
    headers = ["#", "Maskapai", "Negara", "Skor Komposit", "Ulasan", "% Rekomendasi", "Overall", ""]
    for col, title in zip(header_cols, headers):
        with col:
            st.markdown(table_header_cell_html(title), unsafe_allow_html=True)

    for idx, row in ranked_df.iterrows():
        row_cols = st.columns([0.35, 2.3, 1.3, 1.65, 1.1, 1.2, 1.1, 0.9])
        display_name = slug_to_display(row["airline_name"])
        country_name = row["airline_country"] if pd.notna(row["airline_country"]) and str(row["airline_country"]).strip() else "Other"
        rec_pct = float(row["pct_recommended"]) if pd.notna(row["pct_recommended"]) else 0.0
        overall_rating = float(row["overall_rating"]) if pd.notna(row["overall_rating"]) else 0.0

        with row_cols[0]:
            st.markdown(rank_pill_html(int(row["rank"])), unsafe_allow_html=True)
        with row_cols[1]:
            st.markdown(table_text_cell_html(html.escape(display_name), color="#f6f6f6", bold=True, pad_top="0rem"), unsafe_allow_html=True)
        with row_cols[2]:
            st.markdown(table_text_cell_html(html.escape(str(country_name))), unsafe_allow_html=True)
        with row_cols[3]:
            st.markdown(score_bar_html(float(row["composite_score"]), max_score=5.0), unsafe_allow_html=True)
        with row_cols[4]:
            st.markdown(
                f"<div style='padding-top:0.25rem;color:#f0f0f0;'>{review_count_badge(int(row['review_count']), int(min_reviews))}</div>",
                unsafe_allow_html=True,
            )
        with row_cols[5]:
            st.markdown(table_text_cell_html(f"{rec_pct:.1f}%", color="#f0f0f0", bold=True), unsafe_allow_html=True)
        with row_cols[6]:
            st.markdown(table_text_cell_html(f"{overall_rating:.1f}", color="#f0f0f0", bold=True), unsafe_allow_html=True)
        with row_cols[7]:
            render_detail_button(row["airline_name"], row["composite_score"], key=f"table_detail_{int(row['rank'])}")

        st.markdown(thin_divider_html(), unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="margin-top:0.75rem;color:#c9c9c9;font-size:0.9rem;line-height:1.5;">
            • Hijau &gt;100 ulasan • Kuning {int(min_reviews)}–99 ulasan • Maskapai dengan &lt;{int(min_reviews)} ulasan valid tidak ditampilkan.
        </div>
        """,
        unsafe_allow_html=True,
    )
