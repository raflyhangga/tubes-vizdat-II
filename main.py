import streamlit as st

st.set_page_config(
    page_title="DuniaMaskapai",
    page_icon="static/favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Define pages
landing = st.Page(
    "pages/1_landing.py", title="Beranda", url_path="landing", default=True
)
ranking = st.Page("pages/2_ranking.py", title="Ranking", url_path="ranking")
detail = st.Page("pages/3_detail.py", title="Detail", url_path="detail")
compare = st.Page(
    "pages/4_comparison.py", title="Perbandingan", url_path="perbandingan"
)

# Navigation with hidden sidebar
pg = st.navigation([landing, ranking, detail, compare], position="hidden")
pg.run()
