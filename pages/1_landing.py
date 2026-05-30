import streamlit as st

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
    "compare_airlines": [],
    "page4_country": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Hide default Streamlit chrome
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
        min-height: 80vh;
        text-align: center;
        padding: 2rem;
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
        margin-bottom: 3rem;
        max-width: 600px;
    }
    .landing-sub {
        font-size: 1rem;
        color: #888;
        margin-top: 2rem;
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
