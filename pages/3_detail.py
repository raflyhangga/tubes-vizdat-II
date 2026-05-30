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
from ui_components import detail_header_html, rating_gauge_html
from charts.radar import build_radar
from charts.histogram import build_histogram

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2.2rem;
            padding-bottom: 0.5rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }
        .stMarkdown p {
            margin-bottom: 0.25rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

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
ranking_score_value = float(ranking_score) if ranking_score is not None else 0.0
summary = get_airline_review_summary(airline_df)
total_reviews = summary["review_count"]
cabins = airline_df["cabin_flown"].dropna().astype(str) if "cabin_flown" in airline_df.columns else pd.Series([], dtype=str)
cabin_text = cabins.mode().iloc[0] if len(cabins) > 0 else "Mixed cabin"
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
val_mean = airline_df["value_money_rating"].mean()

# HEADER
top_left, top_right = st.columns([3.25, 1], gap="small")
with top_left:
    st.markdown(
        detail_header_html(
            display_name=display_name,
            home_country=home_country,
            cabin_text=cabin_text,
            review_count=total_reviews,
            badge_text="Well-rounded" if summary["pct_recommended"] >= 70 else "Mixed",
        ),
        unsafe_allow_html=True,
    )
with top_right:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Bandingkan", type="primary", use_container_width=True):
        st.session_state["page4_country"] = home_country
        st.session_state["compare_airlines"] = [slug]
        st.switch_page("pages/4_comparison.py")

st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

sub_means = get_airline_subrating_means(airline_df, SUB_RATING_COLS)
g1, g2, g3, g4 = st.columns(4, gap="small")

def gauge_color(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "#7a7a7a"
    if value >= 4.0:
        return "#21b38a"
    if value >= 3.0:
        return "#f39c12"
    return "#ef5350"

gauge_specs = [
    ("Cabin staff", sub_means.get("cabin_staff_rating")),
    ("Seat comfort", sub_means.get("seat_comfort_rating")),
    ("Food & bev", sub_means.get("food_beverages_rating")),
    ("Entertainment", sub_means.get("inflight_entertainment_rating")),
]
for col, (label, val) in zip([g1, g2, g3, g4], gauge_specs):
    with col:
        st.markdown(rating_gauge_html(label, val, gauge_color(val)), unsafe_allow_html=True)

st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)

# ROW 2: Radar + Histogram
radar_col, hist_col = st.columns(2, gap="small")

with radar_col:
    st.markdown("**Profil layanan vs rata-rata industri**")
    fig_radar = build_radar(
        airlines_data={display_name: sub_means.to_dict()},
        benchmark=INDUSTRY_BENCHMARK,
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

with hist_col:
    st.markdown("**Distribusi overall rating (konsistensi)**")
    fig_hist = build_histogram(airline_df)
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)

# ROW 3: Anotasi bawah dalam satu card memanjang
if ranking_score_value >= 4.0:
    score_color = "#21b38a"
elif ranking_score_value >= 3.0:
    score_color = "#f39c12"
else:
    score_color = "#ef5350"

st.markdown(
    f"""
    <div style='margin-top:0.2rem;padding:1.15rem 1.25rem;border-radius:1.15rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);box-shadow:0 12px 28px rgba(0,0,0,0.14);'>
        <div style='display:flex;align-items:stretch;gap:0;flex-wrap:wrap;'>
            <div style='flex:1.45;min-width:360px;display:flex;align-items:center;'>
                <div style='width:100%;display:flex;align-items:stretch;'>
                    <div style='flex:1;min-width:0;padding:0.2rem 0.8rem 0.2rem 0.1rem;text-align:center;display:flex;flex-direction:column;justify-content:center;'>
                        <div style='font-size:2rem;font-weight:900;color:#ffffff;line-height:1;'>{summary['pct_recommended']:.0f}%</div>
                        <div style='font-size:0.88rem;color:#cfd8ff;margin-top:0.25rem;'>Persentase rekomendasi</div>
                    </div>
                    <div style='width:1px;background:rgba(255,255,255,0.12);margin:0.35rem 0;'></div>
                    <div style='flex:1;min-width:0;padding:0.2rem 0.8rem;text-align:center;display:flex;flex-direction:column;justify-content:center;'>
                        <div style='font-size:2rem;font-weight:900;color:#ffffff;line-height:1;'>{total_reviews:,}</div>
                        <div style='font-size:0.88rem;color:#cfd8ff;margin-top:0.25rem;'>Total ulasan</div>
                    </div>
                    <div style='width:1px;background:rgba(255,255,255,0.12);margin:0.35rem 0;'></div>
                    <div style='flex:1;min-width:0;padding:0.2rem 0.8rem;text-align:center;display:flex;flex-direction:column;justify-content:center;'>
                        <div style='font-size:2rem;font-weight:900;color:{score_color};line-height:1;'>{ranking_score_value:.1f}</div>
                        <div style='font-size:0.88rem;color:#cfd8ff;margin-top:0.25rem;'>Skor komposit</div>
                    </div>
                </div>
            </div>
            <div style='width:1px;background:rgba(255,255,255,0.12);margin:0 0.9rem;'></div>
            <div style='flex:1;min-width:300px;padding:0.1rem 0.15rem;display:flex;flex-direction:column;justify-content:center;'>
                <div style='font-size:0.95rem;font-weight:800;color:#e8e8e8;margin-bottom:0.25rem;'>Apa itu skor komposit?</div>
                <div style='font-size:0.88rem;line-height:1.45;color:#c7c7c7;'>Skor komposit adalah rata-rata tertimbang dari empat rating layanan: seat comfort, cabin staff, food & beverages, dan inflight entertainment. Bobotnya mengikuti pengaturan yang kamu pilih di halaman sebelumnya. Semakin tinggi bobot dan rating suatu aspek, semakin besar kontribusinya ke skor akhir maskapai.</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
