import streamlit as st
from utils import load_airline_data, get_airline_country_options

# Initialize session state defaults
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
    "ranking_country": None,
    "ranking_min_reviews": 30,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
df = load_airline_data()
country_options = get_airline_country_options(df)

st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .landing-hero {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 72vh;
        text-align: center;
        padding: 2rem 2rem 1rem 2rem;
    }
    .landing-title {
        font-size: 4rem;
        font-weight: 800;
        color: #1a1a2e;
        line-height: 1.1;
        margin-bottom: 1rem;
    }
    .landing-tagline {
        font-size: 1.5rem;
        color: #4a4a6a;
        margin-bottom: 2rem;
        max-width: 600px;
    }
    .landing-panel {
        max-width: 820px;
        width: 100%;
        padding: 1.2rem 1.2rem 0.8rem 1.2rem;
        border-radius: 1rem;
        background: rgba(255,255,255,0.86);
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
        border: 1px solid rgba(26,26,46,0.08);
        margin-top: 0.75rem;
    }
    .landing-sub {
        font-size: 1rem;
        color: #888;
        margin-top: 1.5rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="landing-hero">
    <div class="landing-title">DuniaMaskapai</div>
    <div class="landing-tagline">
        Temukan maskapai terbaik berdasarkan jutaan ulasan nyata dari penumpang di seluruh dunia.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

panel = st.container()
with panel:
    st.markdown('<div class="landing-panel">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        selected_country = st.selectbox(
            "Negara asal maskapai",
            options=["(Semua negara)"] + country_options,
            index=0,
            help="Nilai ini akan dipakai di page ranking",
        )
    with col2:
        min_reviews = st.number_input(
            "Minimal review valid per maskapai",
            min_value=1,
            max_value=1000,
            value=int(st.session_state.get("ranking_min_reviews", 30)),
            step=1,
            help="Maskapai dengan review di bawah angka ini tidak ditampilkan di ranking",
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.session_state["ranking_country"] = None if selected_country == "(Semua negara)" else selected_country
st.session_state["ranking_min_reviews"] = int(min_reviews)

# CTA button
col_l, col_c, col_r = st.columns([2, 1, 2])
with col_c:
    if st.button(
        "Temukan maskapai terbaik untukmu →",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/2_ranking.py")

st.markdown(
    '<div class="landing-sub">Data: 41,391 ulasan · 362 maskapai · 167 negara reviewer</div>',
    unsafe_allow_html=True,
)
