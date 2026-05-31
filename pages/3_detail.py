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

# Import fonts from Google Fonts and set global CSS according to the design guide
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@800;900&family=Source+Sans+3:wght@600&display=swap');
        
        /* Hide the default Streamlit header/navbar (Deploy button, menu) */
        [data-testid="stHeader"] {
            display: none !important;
        }

        /* Set background and default font (Source Sans 3) */
        .stApp {
            background-color: #d5eafe !important;
            font-family: 'Source Sans 3', sans-serif !important;
            font-weight: 600 !important;
            color: #1f2234 !important;
        }

        /* Use Inter for titles and important/strong text */
        h1, h2, h3, h4, h5, h6, .stMarkdown p strong {
            font-family: 'Inter', sans-serif !important;
            font-weight: 800 !important;
            color: #1f2234 !important;
        }

        .block-container {
            padding-top: 2.2rem;
            padding-bottom: 0.5rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }
        
        .stMarkdown p {
            margin-bottom: 0.25rem;
        }
        
        /* Customize white cards for st.container (gauge & charts) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            border: 1px solid #1c78bb !important;
            border-radius: 1.15rem !important;
            box-shadow: 0 12px 28px rgba(0,0,0,0.06) !important;
            padding: 0.5rem !important;
        }
        
        /* Force inner Streamlit layers to stay white */
        [data-testid="stVerticalBlockBorderWrapper"] > div,
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
            background-color: #ffffff !important;
            border-radius: 1.15rem !important;
        }

        /* Style the Compare button */
        div[data-testid="stButton"] button[kind="primary"] {
            background-color: #1f2234 !important;
            color: #ffffff !important;
            border: 1px solid #1f2234 !important;
        }

        div[data-testid="stButton"] button[kind="primary"] p,
        div[data-testid="stButton"] button[kind="primary"] span,
        div[data-testid="stButton"] button[kind="primary"] div {
            color: #ffffff !important;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover {
            background-color: #2a2e42 !important;
            border-color: #2a2e42 !important;
        }
        
          /* =========================================================
              NEW CSS SOLUTION: Separate Header and Gauge rules
              ========================================================= */

          /* HEADER: Force all text in the header section to stay dark */
        .header-wrapper, .header-wrapper * {
            color: #1f2234 !important;
        }

        /* GAUGE: Force numbers/elements inside the gauge to match the indicator color (var(--g-color)) */
        .gauge-wrapper, 
        .gauge-wrapper div, 
        .gauge-wrapper span, 
        .gauge-wrapper p, 
        .gauge-wrapper h1, .gauge-wrapper h2, .gauge-wrapper h3, .gauge-wrapper h4, 
        .gauge-wrapper strong, .gauge-wrapper b, .gauge-wrapper small {
            color: var(--g-color) !important;
        }
        
        /* Extra protection for SVG text if the gauge uses SVG text elements */
        .gauge-wrapper svg text, .gauge-wrapper svg tspan {
            fill: var(--g-color) !important;
            color: var(--g-color) !important;
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
    st.warning("No airline has been selected. Return to the ranking page.")
    if st.button("Back to Ranking"):
        st.switch_page("pages/2_ranking.py")
    st.stop()

df = load_airline_data()
slug = st.session_state["selected_airline"]
airline_df = df[df["airline_name"] == slug].copy()

if airline_df.empty:
    st.error(f"Data for '{slug}' was not found.")
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
    header_html = detail_header_html(
        display_name=display_name,
        home_country=home_country,
        cabin_text=cabin_text,
        review_count=total_reviews,
        badge_text="",
    )
    
    # PERBAIKAN: Hapus semua karakter newline/enter agar Markdown parser Streamlit tidak rusak
    header_html = header_html.replace("\n", "")
    
    # Wrap the header in a dedicated class
    st.markdown(f"<div class='header-wrapper'>{header_html}</div>", unsafe_allow_html=True)

with top_right:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Compare", type="primary", use_container_width=True):
        st.session_state["page4_country"] = home_country
        st.session_state["page4_default_airline"] = slug
        st.session_state["page4_compare_airlines"] = []
        st.session_state["compare_airlines"] = [slug]
        st.switch_page("pages/4_comparison.py")

st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

# ROW 1: GAUGE CHARTS (Inside the white card)
sub_means = get_airline_subrating_means(airline_df, SUB_RATING_COLS)

with st.container(border=True):
    g1, g2, g3, g4 = st.columns(4, gap="small")

    def gauge_color(value: float | None) -> str:
        if value is None or pd.isna(value):
            return "#7a7a7a"
        if value >= 4.0:
            return "#26ae60"  # Hijau
        if value >= 3.0:
            return "#f39d11"  # Oranye
        return "#e94c3d"      # Merah

    gauge_specs = [
        ("Cabin staff", sub_means.get("cabin_staff_rating")),
        ("Seat comfort", sub_means.get("seat_comfort_rating")),
        ("Food & beverage", sub_means.get("food_beverages_rating")),
        ("Entertainment", sub_means.get("inflight_entertainment_rating")),
    ]
    for col, (label, val) in zip([g1, g2, g3, g4], gauge_specs):
        with col:
            g_color = gauge_color(val)
            gauge_html = rating_gauge_html(label, val, g_color)
            
            # Python trick: inject a dark color only for the label text ("Cabin staff", etc.).
            # Because this is inline styling with !important, CSS cannot override it.
            safe_label = f"<span style='color: #1f2234 !important;'>{label}</span>"
            
            # Replace the original label with the protected dark-colored label
            gauge_html = gauge_html.replace(f">{label}<", f">{safe_label}<")
            if safe_label not in gauge_html: 
                gauge_html = gauge_html.replace(label, safe_label)
            
            # Render the gauge with indicator-colored values while keeping the label dark
            st.markdown(
                f"<div class='gauge-wrapper' style='--g-color: {g_color};'>{gauge_html}</div>", 
                unsafe_allow_html=True
            )

st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)


# ROW 2: RADAR & HISTOGRAM (Inside the white card)
chart_colors = ["#26ae60", "#f39d11", "#e94c3d"]

with st.container(border=True):
    radar_col, hist_col = st.columns(2, gap="small")

    with radar_col:
        st.markdown("**Service profile vs industry average**")
        fig_radar = build_radar(
            airlines_data={display_name: sub_means.to_dict()},
            benchmark=INDUSTRY_BENCHMARK,
            color_discrete_sequence=chart_colors
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

    with hist_col:
        st.markdown("**Overall rating distribution (consistency)**")
        fig_hist = build_histogram(
            airline_df,
            color_discrete_sequence=chart_colors
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)


# ROW 3: BOTTOM NOTES (Manual HTML card)
if ranking_score_value >= 4.0:
    score_color = "#26ae60"
elif ranking_score_value >= 3.0:
    score_color = "#f39d11"
else:
    score_color = "#e94c3d"

html_card = f"""
<div style='margin-top:0.2rem;padding:1.15rem 1.25rem;border-radius:1.15rem;background:#ffffff;border:1px solid #1c78bb;box-shadow:0 12px 28px rgba(0,0,0,0.06);'>
    <div style='display:flex;align-items:stretch;gap:0;flex-wrap:wrap;'>
        <div style='flex:1.45;min-width:360px;display:flex;align-items:center;'>
            <div style='width:100%;display:flex;align-items:stretch;'>
                <div style='flex:1;min-width:0;padding:0.2rem 0.8rem 0.2rem 0.1rem;text-align:center;display:flex;flex-direction:column;justify-content:center;'>
                    <div style='font-family:"Inter", sans-serif;font-size:2rem;font-weight:900;color:#1f2234;line-height:1;'>{summary['pct_recommended']:.0f}%</div>
                    <div style='font-family:"Source Sans 3", sans-serif;font-size:0.88rem;color:#1c78bb;margin-top:0.25rem;font-weight:600;'>Recommendation rate</div>
                </div>
                <div style='width:1px;background:#1c78bb;margin:0.35rem 0;'></div>
                <div style='flex:1;min-width:0;padding:0.2rem 0.8rem;text-align:center;display:flex;flex-direction:column;justify-content:center;'>
                    <div style='font-family:"Inter", sans-serif;font-size:2rem;font-weight:900;color:#1f2234;line-height:1;'>{total_reviews:,}</div>
                    <div style='font-family:"Source Sans 3", sans-serif;font-size:0.88rem;color:#1c78bb;margin-top:0.25rem;font-weight:600;'>Total reviews</div>
                </div>
                <div style='width:1px;background:#1c78bb;margin:0.35rem 0;'></div>
                <div style='flex:1;min-width:0;padding:0.2rem 0.8rem;text-align:center;display:flex;flex-direction:column;justify-content:center;'>
                    <div style='font-family:"Inter", sans-serif;font-size:2rem;font-weight:900;color:{score_color};line-height:1;'>{ranking_score_value:.1f}</div>
                    <div style='font-family:"Source Sans 3", sans-serif;font-size:0.88rem;color:#1c78bb;margin-top:0.25rem;font-weight:600;'>Composite score</div>
                </div>
            </div>
        </div>
        <div style='width:1px;background:#1c78bb;margin:0 0.9rem;'></div>
        <div style='flex:1;min-width:300px;padding:0.1rem 0.15rem;display:flex;flex-direction:column;justify-content:center;'>
            <div style='font-family:"Inter", sans-serif;font-size:0.95rem;font-weight:800;color:#1f2234;margin-bottom:0.25rem;'>What is a composite score?</div>
            <div style='font-family:"Source Sans 3", sans-serif;font-size:0.88rem;font-weight:600;line-height:1.45;color:#1f2234;'>A composite score is the weighted average of four service ratings: seat comfort, cabin staff, food & beverages, and inflight entertainment. The weights follow the settings you chose on the previous page. The higher the weight and rating of an aspect, the greater its contribution to the airline's final score.</div>
        </div>
    </div>
</div>
"""
st.markdown(html_card, unsafe_allow_html=True)