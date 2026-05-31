import html
import pandas as pd
import streamlit as st

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

# =====================================================================
# CSS GLOBAL & KUSTOMISASI PALET WARNA LIGHT MODE
# =====================================================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@700;800;900&family=Source+Sans+3:wght@400;600;700&display=swap');

        :root {
            --bg: #d5eafe;
            --navy: #1f2234;
            --blue: #1c78bb;
            --soft-blue: #86c8f4;
            --green: #26ae60;
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
            max-width: 1400px;
        }

        /* ========================================================= */
        /* MENGUBAH BUTTON MENJADI TEKS KLIKABEL (HYPERLINK STYLE) */
        /* ========================================================= */
        div[data-testid='stButton'] button {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            min-height: auto !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        div[data-testid='stButton'] button:hover {
            background-color: transparent !important;
        }
        
        div[data-testid='stButton'] button p,
        div[data-testid='stButton'] button span,
        div[data-testid='stButton'] button div {
            color: var(--blue) !important; /* Warna biru seperti link */
            white-space: nowrap !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 900 !important;
            font-size: 0.95rem !important;
            margin: 0 !important;
            transition: color 0.2s ease;
        }
        
        /* Efek saat kursor diarahkan ke tulisan Detail */
        div[data-testid='stButton'] button:hover p,
        div[data-testid='stButton'] button:hover span,
        div[data-testid='stButton'] button:hover div {
            color: var(--navy) !important; /* Menjadi gelap */
            text-decoration: underline !important;
        }

        /* Container Card Putih untuk Tabel (Jika didukung browser) */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.white-card) {
            background-color: #ffffff !important;
            border-radius: 16px !important;
            border: none !important;
            box-shadow: 0px 6px 20px rgba(31, 34, 52, 0.06) !important;
            padding: 1.2rem 1.5rem !important; 
        }
        
        /* Memaksa elemen Markdown lain mengikuti light mode */
        [data-testid="stMarkdownContainer"] p, 
        [data-testid="stMarkdownContainer"] h3 {
            color: var(--navy) !important;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# KOMPONEN KUSTOM HTML INLINE
# =====================================================================
def custom_banner(primary, secondary, tertiary):
    return f"""
    <div style="background-color: #ffffff; border-left: 6px solid #1c78bb; padding: 1.2rem 1.5rem; border-radius: 10px; box-shadow: 0 4px 10px rgba(31,34,52,0.05); margin-bottom: 2rem;">
        <div style="font-family: 'Inter', sans-serif; font-size: 1.2rem; font-weight: 900; color: #1f2234 !important; margin-bottom: 0.35rem; text-transform: uppercase;">{primary}</div>
        <div style="font-family: 'Source Sans 3', sans-serif; font-size: 0.95rem; font-weight: 600; color: #1f2234 !important; margin-bottom: 0.6rem; line-height: 1.4;">{secondary}</div>
        <div style="font-family: 'Source Sans 3', sans-serif; font-size: 0.85rem; font-weight: 700; color: #1c78bb !important; display: inline-block; background: #d5eafe; padding: 0.2rem 0.6rem; border-radius: 6px;">{tertiary}</div>
    </div>
    """

def custom_header(text):
    return f"<div style='font-family: Inter, sans-serif; font-weight: 900; font-size: 0.85rem; color: #1c78bb !important; border-bottom: 2px solid #86c8f4; padding-bottom: 0.5rem; margin-bottom: 0.2rem; white-space: nowrap;'>{text}</div>"

def custom_text(text, bold=False):
    fw = "900" if bold else "600"
    ff = "'Inter', sans-serif" if bold else "'Source Sans 3', sans-serif"
    return f"<div style='font-family: {ff}; font-weight: {fw}; font-size: 0.95rem; color: #1f2234 !important; padding: 0.2rem 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{text}</div>"

def custom_score_bar(score, max_score=5.0):
    pct = max(0.0, min((score / max_score) * 100.0, 100.0))
    if score >= 3.5:
        bar_color = "#26ae60"
        track_color = "rgba(38, 174, 96, 0.18)"
    elif score >= 2.5:
        bar_color = "#f39d11"
        track_color = "rgba(243, 157, 17, 0.18)"
    else:
        bar_color = "#e94c3d"
        track_color = "rgba(233, 76, 61, 0.18)"

    return f"""
    <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.2rem 0;">
        <div style="flex-grow: 1; height: 8px; background-color: {track_color}; border-radius: 4px; overflow: hidden; min-width: 40px;">
            <div style="width: {pct}%; height: 100%; background-color: {bar_color}; border-radius: 4px;"></div>
        </div>
        <div style="font-family: 'Inter', sans-serif; font-weight: 900; font-size: 1rem; color: {bar_color} !important; min-width: 2.2rem; text-align: right;">
            {score:.2f}
        </div>
    </div>
    """

def custom_review_badge(count, min_reviews):
    color = "#26ae60" if count >= 100 else "#f39d11"
    return f"""
    <div style="display: flex; align-items: center; gap: 0.35rem; font-family: 'Source Sans 3', sans-serif; font-size: 0.95rem; font-weight: 700; color: #1f2234 !important; padding: 0.2rem 0; white-space: nowrap;">
        <div style="width: 8px; height: 8px; border-radius: 50%; background-color: {color}; flex-shrink: 0;"></div>
        {count}
    </div>
    """

def build_podium(top3_df: pd.DataFrame) -> str:
    """
    Returns an HTML string for the podium visualization.
    Visual order: Silver(2nd) | Gold(1st) | Bronze(3rd)
    """
    PODIUM_STYLES = {
        1: ("🥇", "#FFD700", "linear-gradient(135deg, #FFD700, #FFA500)", 250, "#1"),
        2: ("🥈", "#C0C0C0", "linear-gradient(135deg, #C0C0C0, #A8A8A8)", 210, "#2"),
        3: ("🥉", "#CD7F32", "linear-gradient(135deg, #CD7F32, #A0522D)", 180, "#3"),
    }

    visual_order = []
    for target_rank in [2, 1, 3]:
        row = top3_df[top3_df["rank"] == target_rank]
        if not row.empty:
            visual_order.append(row.iloc[0])
        else:
            visual_order.append(None)

    cards = []
    for row in visual_order:
        if row is None:
            cards.append('<div style="flex:1"></div>')
            continue

        rank = int(row["rank"])
        medal, border_color, bg_grad, height, rank_label = PODIUM_STYLES[rank]
        name = row["display_name"]
        score = row["composite_score"]
        pct = row["pct_recommended"]

        name_size = "1.1rem" if rank == 1 else "0.95rem"
        score_size = "1.3rem" if rank == 1 else "1.1rem"

        card_html = (
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;margin:0 8px;">'
            f'<div style="font-size:2rem;margin-bottom:0.5rem">{medal}</div>'
            f'<div style="background:{bg_grad};border:2px solid {border_color};border-radius:12px 12px 0 0;'
            f'padding:1.5rem 1rem;width:100%;height:{height}px;display:flex;flex-direction:column;'
            f'align-items:center;justify-content:flex-end;box-shadow:0 4px 15px rgba(0,0,0,0.1);text-align:center;">'
            f'<div style="font-size:2rem;font-weight:800;color:rgba(0,0,0,0.3);line-height:1;">{rank_label}</div>'
            f'<div style="font-size:{name_size};font-weight:700;color:#1a1a1a;margin-top:0.5rem;line-height:1.2;">{name}</div>'
            f'<div style="font-size:{score_size};font-weight:800;color:#1a1a1a;margin-top:0.3rem;">{score:.3f}</div>'
            f'<div style="font-size:0.75rem;color:rgba(0,0,0,0.6);margin-top:0.2rem;">{pct:.0f}% direkomendasikan</div>'
            f'</div></div>'
        )
        cards.append(card_html)

    podium_html = (
        '<div style="display:flex;align-items:flex-end;justify-content:center;width:100%;padding:1rem 0;min-height:280px;">'
        f"{''.join(cards)}"
        '</div>'
    )
    return podium_html

# =====================================================================
# LOGIKA DATA
# =====================================================================
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

st.markdown(f"<h1 style='font-family: Inter; font-weight: 900; color: #1f2234; text-transform: uppercase; margin-bottom: 0;'>Ranking Maskapai</h1>", unsafe_allow_html=True)

country_label = selected_country_value or "Semua negara"
st.markdown(
    f"<div style='font-family: Source Sans 3; font-size: 1.05rem; font-weight: 600; color: #1c78bb; margin-bottom: 1.5rem;'>"
    f"Podium berada di kiri. Tabel lengkap dengan detail berada di kanan. Filter aktif: <b>{country_label}</b> · minimal <b>{int(min_reviews)} review valid</b>."
    f"</div>", 
    unsafe_allow_html=True
)

active_weight_label = sorted(weights, key=lambda key: weights[key], reverse=True)[0]
active_weight_text = RATING_LABELS[active_weight_label]
weight_summary = " · ".join(
    f"{RATING_LABELS[col]} {weights[col] * 100:.0f}%" for col in RATING_COLS
)

st.markdown(
    custom_banner(
        primary=f"KAMU MEMENTINGKAN {html.escape(active_weight_text)} PALING TINGGI.",
        secondary=(
            "Skor dihitung per baris dari bobot yang diwariskan, lalu dirata-ratakan per maskapai. "
            f"Maskapai yang tampil wajib punya minimal {int(min_reviews)} review valid setelah filter negara diterapkan."
        ),
        tertiary=f"Bobot aktif: {html.escape(weight_summary)}",
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

# =====================================================================
# RENDER UI - PEMBAGIAN KOLOM
# =====================================================================
left_col, right_col = st.columns([1.05, 1.95], gap="large")

top3 = ranked_df.head(3).copy()
top3["display_name"] = top3["airline_name"].apply(slug_to_display)

with left_col:
    st.markdown("<h3 style='font-family: Inter; font-weight: 900; color: #1f2234 !important; margin-bottom: 0.2rem;'>Podium Teratas</h3>", unsafe_allow_html=True)
    st.markdown(build_podium(top3), unsafe_allow_html=True)
    st.markdown(
        "<div style='font-family: Source Sans 3; font-weight: 600; color: #1f2234 !important; font-size: 0.9rem; margin-top: 1.5rem; background: rgba(255,255,255,0.6); padding: 0.8rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.8);'>"
        "Urutan podium mengikuti skor tertinggi. Angka pada kartu adalah skor rata-rata per maskapai setelah perhitungan baris valid."
        "</div>",
        unsafe_allow_html=True,
    )

with right_col:
    with st.container(border=True):
        st.markdown('<div class="white-card"></div>', unsafe_allow_html=True)
        
        st.markdown("<h3 style='font-family: Inter; font-weight: 900; color: #1f2234 !important; margin-bottom: 0.2rem;'>Daftar Lengkap Maskapai</h3>", unsafe_allow_html=True)
        st.markdown("<div style='font-family: Source Sans 3; font-weight: 600; color: #1c78bb; font-size: 0.95rem; margin-bottom: 1.2rem;'>Klik tombol detail untuk membuka halaman maskapai.</div>", unsafe_allow_html=True)

        col_ratios = [0.4, 2.3, 1.4, 2.0, 1.1, 1.8, 1.1, 1.2]
        table_scroll_height = 650

        with st.container(height=table_scroll_height, border=False):
            header_cols = st.columns(col_ratios, vertical_alignment="bottom")
            headers = ["#", "Maskapai", "Negara", "Skor", "Ulasan", "% Rekomendasi", "Overall", ""]
            for col, title in zip(header_cols, headers):
                with col:
                    st.markdown(custom_header(title), unsafe_allow_html=True)

            st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)

            for idx, row in ranked_df.iterrows():
                row_cols = st.columns(col_ratios, vertical_alignment="center")

                display_name = slug_to_display(row["airline_name"])
                country_name = row["airline_country"] if pd.notna(row["airline_country"]) and str(row["airline_country"]).strip() else "Other"
                rec_pct = float(row["pct_recommended"]) if pd.notna(row["pct_recommended"]) else 0.0
                overall_rating = float(row["overall_rating"]) if pd.notna(row["overall_rating"]) else 0.0

                with row_cols[0]:
                    st.markdown(custom_text(str(int(row["rank"])), bold=True), unsafe_allow_html=True)
                with row_cols[1]:
                    st.markdown(custom_text(html.escape(display_name), bold=True), unsafe_allow_html=True)
                with row_cols[2]:
                    st.markdown(custom_text(html.escape(str(country_name))), unsafe_allow_html=True)
                with row_cols[3]:
                    st.markdown(custom_score_bar(float(row["composite_score"]), max_score=5.0), unsafe_allow_html=True)
                with row_cols[4]:
                    st.markdown(custom_review_badge(int(row['review_count']), int(min_reviews)), unsafe_allow_html=True)
                with row_cols[5]:
                    st.markdown(custom_text(f"{rec_pct:.1f}%", bold=True), unsafe_allow_html=True)
                with row_cols[6]:
                    st.markdown(custom_text(f"{overall_rating:.1f}", bold=True), unsafe_allow_html=True)
                with row_cols[7]:
                    render_detail_button(row["airline_name"], row["composite_score"], key=f"table_detail_{int(row['rank'])}")

                st.markdown("<hr style='border: none; border-top: 1px solid rgba(28, 120, 187, 0.18); margin: 0.35rem 0;'>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="margin-top:0.8rem; font-family: 'Source Sans 3', sans-serif; font-size: 0.9rem; font-weight: 600; color: #1c78bb !important; text-align: right;">
                <span style="color: #26ae60;">●</span> &ge;100 ulasan &nbsp;&nbsp; 
                <span style="color: #f39d11;">●</span> {int(min_reviews)}–99 ulasan &nbsp;&nbsp; 
                <span style="color: #1f2234 !important; opacity: 0.6;">(Hanya menampilkan &ge; {int(min_reviews)} ulasan valid)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )