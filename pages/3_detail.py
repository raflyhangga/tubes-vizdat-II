import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils import (
    load_airline_data,
    SUB_RATING_COLS,
    INDUSTRY_BENCHMARK,
    slug_to_display,
    get_airline_review_summary,
    get_airline_subrating_means,
)

st.set_page_config(page_title="Detail Maskapai", page_icon="✈️", layout="wide")

# =====================================================================
# CSS GLOBAL & KUSTOMISASI KARTU
# =====================================================================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@700;800;900&family=Source+Sans+3:wght@400;600;700&display=swap');

        :root {
            --bg: #d5eafe;
            --navy: #1f2234;
            --blue: #1c78bb;
            --green: #26ae60;
            --red: #e94c3d;
            --orange: #f39d11;
        }

        html, body, [class*='css'] {
            font-family: 'Source Sans 3', sans-serif;
            color: var(--navy);
        }

        .stApp {
            background-color: var(--bg) !important;
        }

        header[data-testid="stHeader"] {
            display: none !important;
        }

        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 1200px;
        }

        /* Trik CSS: Membuat container Streamlit menjadi kartu putih */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.white-card) {
            background-color: #ffffff !important;
            border-radius: 20px !important;
            border: none !important;
            box-shadow: 0px 8px 24px rgba(31, 34, 52, 0.08) !important;
            padding: 1.5rem !important; 
            position: relative; /* Agar badge rank bisa diletakkan absolute */
        }

        /* Menghapus gap bawaan Streamlit dalam card */
        div[data-testid='stVerticalBlockBorderWrapper']:has(.white-card) > div {
            gap: 0 !important;
        }

        .page-title {
            font-family: 'Inter', sans-serif;
            font-size: 2.8rem;
            font-weight: 900;
            color: var(--navy);
            text-align: center;
            text-transform: uppercase;
            margin-bottom: 2.5rem;
            letter-spacing: 0.02em;
        }

        .card-title {
            font-family: 'Inter', sans-serif;
            font-size: 1.15rem;
            font-weight: 900;
            color: var(--navy);
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            margin-bottom: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state (Fallback pengaman)
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
    "selected_airline": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Guard (Kembali ke ranking jika tidak ada yang dipilih)
if not st.session_state.get("selected_airline"):
    st.warning("Tidak ada maskapai yang dipilih. Kembali ke halaman ranking.")
    if st.button("Kembali ke Ranking"):
        st.switch_page("pages/2_ranking.py")
    st.stop()

# Load Data
df = load_airline_data()
slug = st.session_state["selected_airline"]
airline_df = df[df["airline_name"] == slug].copy()

if airline_df.empty:
    st.error(f"Data untuk '{slug}' tidak ditemukan.")
    st.stop()

display_name = slug_to_display(slug)
summary = get_airline_review_summary(airline_df)
sub_means = get_airline_subrating_means(airline_df, SUB_RATING_COLS)

# =====================================================================
# KALKULASI RANKING MASKAPAI (Untuk Badge Lencana)
# =====================================================================
min_reviews = st.session_state.get("ranking_min_reviews", 30)
weights = st.session_state.get("score_weights", {"seat": 0.25, "cabin": 0.25, "food": 0.25, "entertainment": 0.25})

all_stats = df.groupby("airline_name").agg(
    count=("author", "count"),
    seat=("seat_comfort_rating", "mean"),
    cabin=("cabin_staff_rating", "mean"),
    food=("food_beverages_rating", "mean"),
    ent=("inflight_entertainment_rating", "mean")
)
valid_airlines = all_stats[all_stats["count"] >= min_reviews].copy()
valid_airlines["score"] = (
    valid_airlines["seat"].fillna(0) * weights["seat"] +
    valid_airlines["cabin"].fillna(0) * weights["cabin"] +
    valid_airlines["food"].fillna(0) * weights["food"] +
    valid_airlines["ent"].fillna(0) * weights["entertainment"]
)
valid_airlines = valid_airlines.sort_values("score", ascending=False).reset_index()

try:
    rank_pos = valid_airlines[valid_airlines["airline_name"] == slug].index[0] + 1
    composite_score = valid_airlines.loc[valid_airlines["airline_name"] == slug, "score"].values[0]
except IndexError:
    rank_pos = "-"
    composite_score = 0.0

# =====================================================================
# UI LAYOUT: HEADER
# =====================================================================
st.markdown(f'<div class="page-title">{display_name}</div>', unsafe_allow_html=True)

# Grid 2x2
col_left, col_right = st.columns([1, 1], gap="large")

# =====================================================================
# KARTU ATAS KIRI: KOMPOSIT SKOR & SUMMARY
# =====================================================================
with col_left:
    with st.container(border=True):
        st.markdown('<div class="white-card"></div>', unsafe_allow_html=True)
        
        # Lencana Badge (Absolute Position)
        st.markdown(f"""
            <div style="position: absolute; top: -20px; left: -22px; z-index: 10;">
                <svg width="68" height="68" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                  <polygon points="50,0 61,11 77,8 82,23 97,28 93,43 100,57 87,68 88,84 73,86 63,99 48,92 34,99 24,85 9,85 11,70 0,56 7,41 0,26 15,21 19,6 35,10" fill="#1f2234" />
                  <text x="50" y="60" font-family="Inter" font-weight="900" font-size="34" fill="white" text-anchor="middle">{rank_pos}</text>
                </svg>
            </div>
        """, unsafe_allow_html=True)

        # Konten Skor (HTML dirapatkan agar tidak dirusak oleh Markdown parser)
        html_content = (
            f"<div style='display: flex; align-items: center; justify-content: center; min-height: 140px; font-family: \"Source Sans 3\", sans-serif;'>"
            f"<div style='flex: 1; text-align: center;'>"
            f"<span style='font-family: \"Inter\", sans-serif; font-size: 3.8rem; font-weight: 900; color: #1f2234; line-height: 1;'>{composite_score:.2f}</span>"
            f"<span style='font-size: 1.6rem; font-weight: 600; color: #1f2234;'> / 5</span>"
            f"<br>"
            f"<span style='color: #1c78bb; font-size: 1.15rem; font-weight: 600;'>Composite Score</span>"
            f"</div>"
            f"<div style='width: 2px; height: 70px; background-color: #1c78bb; opacity: 0.25; margin: 0 1.5rem;'></div>"
            f"<div style='flex: 1; text-align: left; padding-left: 0.5rem;'>"
            f"<div style='margin-bottom: 0.8rem;'>"
            f"<span style='font-family: \"Inter\", sans-serif; font-size: 1.4rem; font-weight: 900; color: #1f2234;'>{summary['review_count']}</span>"
            f"<span style='color: #1c78bb; font-size: 1.05rem;'> Total Reviews</span>"
            f"</div>"
            f"<div>"
            f"<span style='font-family: \"Inter\", sans-serif; font-size: 1.4rem; font-weight: 900; color: #1f2234;'>{summary['pct_recommended']:.0f}%</span>"
            f"<span style='color: #1c78bb; font-size: 1.05rem;'> Recommended</span>"
            f"</div>"
            f"</div>"
            f"</div>"
        )
        st.markdown(html_content, unsafe_allow_html=True)
        
# =====================================================================
# KARTU ATAS KANAN: GAUGE CHART
# =====================================================================
def get_gauge_color(val):
    if pd.isna(val): return "#d3d3d3"
    if val >= 3.5: return "#26ae60"  # Hijau
    if val >= 2.5: return "#f39d11"  # Oranye
    return "#e94c3d"                 # Merah

with col_right:
    with st.container(border=True):
        st.markdown('<div class="white-card"></div>', unsafe_allow_html=True)
        
        gauges_html = ""
        gauge_specs = [
            ("Cabin\nService", sub_means.get("cabin_staff_rating", 0)),
            ("Seat\nComfort", sub_means.get("seat_comfort_rating", 0)),
            ("Food &\nBeverage", sub_means.get("food_beverages_rating", 0)),
            ("Inflight\nEntertainment", sub_means.get("inflight_entertainment_rating", 0)),
        ]
        
        for label, val in gauge_specs:
            color = get_gauge_color(val)
            pct = (val / 5.0) * 100 if not pd.isna(val) else 0
            display_val = f"{val:.2f}" if not pd.isna(val) else "N/A"
            label_html = label.replace('\n', '<br>')
            
            gauges_html += f"""
            <div style="display: flex; flex-direction: column; align-items: center; width: 25%;">
                <div style="width: 85px; height: 85px; border-radius: 50%; background: conic-gradient({color} {pct}%, #e2e8f0 0); display: flex; align-items: center; justify-content: center;">
                    <div style="width: 63px; height: 63px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center; font-family: 'Inter', sans-serif; font-size: 1.25rem; font-weight: 900; color: #1f2234;">
                        {display_val}
                    </div>
                </div>
                <div style="margin-top: 0.6rem; font-family: 'Source Sans 3', sans-serif; font-size: 0.95rem; text-align: center; color: #1f2234; line-height: 1.15;">
                    {label_html}
                </div>
            </div>
            """

        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; min-height: 140px; width: 100%; padding: 0 0.5rem;">
                {gauges_html}
            </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

# Grid Bawah 2x2
col_bot_left, col_bot_right = st.columns([1, 1], gap="large")

# =====================================================================
# KARTU BAWAH KIRI: RADAR CHART
# =====================================================================
with col_bot_left:
    with st.container(border=True):
        st.markdown('<div class="white-card"></div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">SERVICE FACTOR VS INDUSTRY AVERAGE</div>', unsafe_allow_html=True)
        
        categories = ['Cabin Staff', 'Seat Comfort', 'Entertainment', 'Food & Beverages']
        airline_vals = [
            sub_means.get("cabin_staff_rating", 0),
            sub_means.get("seat_comfort_rating", 0),
            sub_means.get("inflight_entertainment_rating", 0),
            sub_means.get("food_beverages_rating", 0)
        ]
        
        industry_vals = [
            INDUSTRY_BENCHMARK.get("cabin_staff_rating", 0),
            INDUSTRY_BENCHMARK.get("seat_comfort_rating", 0),
            INDUSTRY_BENCHMARK.get("inflight_entertainment_rating", 0),
            INDUSTRY_BENCHMARK.get("food_beverages_rating", 0)
        ]

        # Menambahkan titik awal di akhir agar garis chart tersambung melingkar
        categories.append(categories[0])
        airline_vals.append(airline_vals[0])
        industry_vals.append(industry_vals[0])

        fig_radar = go.Figure()
        
        # Industry Average
        fig_radar.add_trace(go.Scatterpolar(
            r=industry_vals,
            theta=categories,
            mode='lines',
            line_color='#c0c8d6',
            line_width=2,
            name='Industry Average',
            hoverinfo='none'
        ))
        
        # Airline Data
        fig_radar.add_trace(go.Scatterpolar(
            r=airline_vals,
            theta=categories,
            mode='lines+markers',
            line_color='#1c78bb',
            line_width=3,
            marker=dict(color='#1c78bb', size=8),
            name=display_name,
            hoverinfo='none'
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickfont=dict(color='#a0aabf', size=10),
                    gridcolor='#e2e8f0',
                    linecolor='rgba(0,0,0,0)'
                ),
                angularaxis=dict(
                    tickfont=dict(color='#1f2234', size=12, family="Source Sans 3"),
                    gridcolor='#e2e8f0',
                    linecolor='#e2e8f0'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=25, b=25, l=40, r=40),
            height=260
        )
        
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# KARTU BAWAH KANAN: OVERALL RATING HISTOGRAM
# =====================================================================
with col_bot_right:
    with st.container(border=True):
        st.markdown('<div class="white-card"></div>', unsafe_allow_html=True)
        
        # Menghitung distribusi rating 1 sampai 5
        rating_counts = airline_df["overall_rating"].value_counts().reindex([1.0, 2.0, 3.0, 4.0, 5.0], fill_value=0)
        
        # Array Warna Berdasarkan Rating (1,2: Merah | 3: Oranye | 4,5: Hijau)
        bar_colors = ["#e94c3d", "#e94c3d", "#f39d11", "#26ae60", "#26ae60"]

        fig_hist = go.Figure(data=[
            go.Bar(
                x=["1", "2", "3", "4", "5"],
                y=rating_counts.values,
                marker_color=bar_colors,
                hoverinfo='none'
            )
        ])

        fig_hist.update_layout(
            xaxis=dict(visible=False, showgrid=False),
            yaxis=dict(visible=False, showgrid=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=10, l=10, r=10),
            height=260,
            bargap=0.08
        )

        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="card-title" style="margin-top: -10px;">OVERALL RATING</div>', unsafe_allow_html=True)