import html
import json

import pandas as pd
import streamlit as st

from charts.choropleth import build_airline_origin_choropleth
from utils import get_available_countries, load_airline_data, triple_range_slider


st.set_page_config(page_title="Ranking Maskapai", page_icon="✈️", layout="wide")

# =====================================================================
# CSS GLOBAL - Kompak tapi tetap rapi dan proporsional
# =====================================================================
st.markdown("""
    <style>
        header[data-testid="stHeader"] { display: none !important; }
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1360px;
        }
    </style>
""", unsafe_allow_html=True)

defaults = {
        "filter_country": None,
        "filter_cabin": ["Economy"], 
        "ranking_min_reviews": 30,
        "score_weights": {
                "seat": 0.20,
                "cabin": 0.20,
                "food": 0.45,
                "entertainment": 0.15,
        },
        "results_visible": False,
        "selected_airline": None,
        "compare_airlines": [],
        "page4_country": None,
}
for key, value in defaults.items():
        if key not in st.session_state:
                st.session_state[key] = value


def format_count(value: int) -> str:
        return f"{value:,}".replace(",", ".")


def cabin_selector(selected_default: list[str], cabin_counts: dict[str, int]) -> list[str]:
        cabins = [
                {"key": "First Class", "title": "FIRST\nCLASS", "count": cabin_counts.get("First Class", 0)},
                {"key": "Business Class", "title": "BUSINESS\nCLASS", "count": cabin_counts.get("Business Class", 0)},
                {"key": "Premium Economy", "title": "PREMIUM\nECONOMY", "count": cabin_counts.get("Premium Economy", 0)},
                {"key": "Economy", "title": "ECONOMY", "count": cabin_counts.get("Economy", 0)},
        ]

        component = st.components.v2.component(
                "ranking_cabin_selector",
                html="""
                <div class="cabin-selector">
                    <div class="cabin-selector__grid"></div>
                </div>
                """,
                css="""
                .cabin-selector { font-family: 'Source Sans 3', sans-serif; width: 100%; }
                .cabin-selector__grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.6rem; }
                
                /* Container Card Kabin (Default) */
                .cabin-card { 
                    appearance: none; 
                    border: 2px solid transparent; 
                    border-radius: 14px; 
                    padding: 0; 
                    min-height: 72px; 
                    background: transparent; 
                    cursor: pointer; 
                    display: flex; 
                    flex-direction: column; 
                    align-items: center; 
                    transition: all 0.16s ease; 
                }
                
                .cabin-card__inner-pill { 
                    background: #86c8f4; 
                    border-radius: 12px; 
                    width: 100%; 
                    height: 100%; 
                    display: flex; 
                    flex-direction: column; 
                    align-items: center; 
                    justify-content: center; 
                    transition: all 0.16s ease; 
                }
                
                .cabin-card__title { font-family: 'Inter', sans-serif; font-size: 0.8rem; line-height: 1.05; font-weight: 800; letter-spacing: 0.01em; white-space: pre-line; color: #1f2234; }
                .cabin-card__count { margin-top: 0.25rem; font-family: 'Source Sans 3', sans-serif; font-size: 0.7rem; line-height: 1; color: #1f2234; font-weight: 600; }
                
                /* STATE TIDAK AKTIF (Lebih terang / Sama dengan latar) */
                .cabin-card:not(.is-active) { 
                    background: #d5eafe; 
                    border: 2px solid #86c8f4; 
                    padding: 0.25rem; 
                    justify-content: flex-start; 
                }
                .cabin-card:not(.is-active) .cabin-card__inner-pill { height: 38px; justify-content: center; }
                .cabin-card:not(.is-active) .cabin-card__count { color: #1c78bb; margin-top: auto; margin-bottom: 0.2rem; }
                
                /* Visibilitas Count Text dibalik */
                .cabin-card.is-active .cabin-card__count-outer { display: none; }
                .cabin-card.is-active .cabin-card__count-inner { display: block; }
                .cabin-card:not(.is-active) .cabin-card__count-outer { display: block; }
                .cabin-card:not(.is-active) .cabin-card__count-inner { display: none; }
                """,
                js="""
                export default function(component) {
                    const { parentElement, data, setStateValue } = component;
                    const grid = parentElement.querySelector('.cabin-selector__grid');
                    const cabins = Array.isArray(data?.cabins) ? data.cabins : [];
                    
                    // SINKRONISASI STATE: Mencegah state JS tertimpa oleh proses re-render Streamlit
                    const incomingSelected = Array.isArray(data?.selected) && data.selected.length ? data.selected : cabins.map((item) => item.key);
                    const incomingSelectedStr = JSON.stringify(incomingSelected);
                    
                    if (!parentElement.customState || parentElement.lastIncoming !== incomingSelectedStr) {
                        parentElement.customState = new Set(incomingSelected);
                        parentElement.lastIncoming = incomingSelectedStr;
                    }
                    
                    let selected = parentElement.customState;

                    function render() {
                        grid.innerHTML = cabins.map((item) => `
                            <button type="button" class="cabin-card${selected.has(item.key) ? ' is-active' : ''}" data-cabin="${item.key}">
                                <div class="cabin-card__inner-pill">
                                    <div class="cabin-card__title">${item.title}</div>
                                    <div class="cabin-card__count cabin-card__count-inner">${item.count.toLocaleString('id-ID')} Reviews</div>
                                </div>
                                <div class="cabin-card__count cabin-card__count-outer">${item.count.toLocaleString('id-ID')} Reviews</div>
                            </button>
                        `).join('');

                        const buttons = Array.from(parentElement.querySelectorAll('.cabin-card'));
                        buttons.forEach((button) => {
                            button.addEventListener('click', () => {
                                const key = button.dataset.cabin;
                                if (selected.has(key)) { selected.delete(key); } else { selected.add(key); }
                                if (selected.size === 0 && cabins.length > 0) { selected = new Set([cabins[0].key]); }
                                
                                // Simpan state secara persisten di DOM agar tidak di-reset
                                parentElement.customState = selected;
                                parentElement.lastIncoming = JSON.stringify(Array.from(selected));
                                
                                // HANYA trigger update Streamlit saat ada interaksi klik!
                                setStateValue('value', Array.from(selected));
                                render();
                            });
                        });
                    }
                    render();
                }
                """,
        )

        result = component(
                key="ranking-cabin-selector",
                data={"cabins": cabins, "selected": selected_default},
                default={"value": selected_default},
                on_value_change=lambda: None,
        )

        if result.value is None: return selected_default
        return list(result.value)

st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@700;800;900&family=Source+Sans+3:wght@400;600;700&display=swap');
:root { --bg: #d5eafe; --navy: #1f2234; --blue: #1c78bb; --soft-blue: #86c8f4; --green: #b2e278; --orange: #fecd72; --pink: #ffb2c0; }
html, body, [class*='css'] { font-family: 'Source Sans 3', sans-serif; color: var(--navy); }
.stApp { background-color: var(--bg) !important; }
.hero-title { font-family: 'Inter', sans-serif; font-size: 2.6rem; line-height: 0.98; font-weight: 900; letter-spacing: 0.02em; color: var(--navy); text-align: center; margin-top: -0.5rem; margin-bottom: 0.2rem; }
.hero-subtitle { font-family: 'Source Sans 3', sans-serif; font-size: 1.1rem; line-height: 1.2; color: var(--navy); text-align: center; margin-bottom: 0.8rem; }
[data-testid='stVerticalBlockBorderWrapper'] { background-color: #ffffff !important; border: none !important; border-radius: 16px !important; box-shadow: 0px 4px 14px rgba(31, 34, 52, 0.06) !important; padding: 0.8rem 1rem !important; }
[data-testid='stVerticalBlockBorderWrapper'] > div { gap: 0.4rem !important; }
.field-label { display: flex; align-items: center; min-height: 2.8rem; margin: 0; padding: 0; font-family: 'Source Sans 3', sans-serif; font-size: 1.05rem; font-weight: 600; color: var(--blue); line-height: 1.2; }
.field-label.center { justify-content: center; }
div[data-testid='stSelectbox'] label, div[data-testid='stNumberInput'] label { display: none; }
div[data-baseweb='select'] > div { min-height: 2.8rem !important; border-radius: 10px !important; border: none !important; background-color: var(--soft-blue) !important; }
div[data-baseweb='select'] * { font-family: 'Inter', sans-serif !important; font-size: 0.95rem !important; font-weight: 800 !important; color: var(--navy) !important; display: flex; align-items: center; }
div[data-baseweb='select'] svg { fill: var(--blue) !important; color: var(--blue) !important; }
div[data-testid="stNumberInput"] div[data-baseweb="input"], div[data-testid="stNumberInput"] div[data-baseweb="base-input"] { background-color: var(--soft-blue) !important; border: none !important; border-radius: 10px !important; outline: none !important; min-height: 2.8rem !important; }
div[data-testid="stNumberInput"] div[data-baseweb="base-input"]::before, div[data-testid="stNumberInput"] div[data-baseweb="base-input"]::after { display: none !important; }
div[data-testid="stNumberInput"] input { color: var(--navy) !important; -webkit-text-fill-color: var(--navy) !important; font-family: 'Inter', sans-serif !important; font-size: 1rem !important; font-weight: 800 !important; background-color: transparent !important; padding-top: 0 !important; padding-bottom: 0 !important; }
div[data-testid='stNumberInput'] button { color: var(--blue) !important; background-color: transparent !important; border: none !important; }
div[data-testid='stNumberInput'] button svg { fill: var(--blue) !important; }
div[data-testid='stButton'] button[kind='primary'] { background-color: var(--navy) !important; color: #ffffff !important; border-radius: 12px !important; height: 72px !important; font-family: 'Inter', sans-serif !important; font-size: 1.3rem !important; font-weight: 900 !important; border: none !important; letter-spacing: 0.02em; box-shadow: 0 6px 14px rgba(31, 34, 52, 0.15) !important; margin-top: 0 !important; }
div[data-testid='stButton'] button[kind='primary']:hover { background-color: #161826 !important; }
.section-title { font-family: 'Source Sans 3', sans-serif; font-size: 1.25rem; font-weight: 600; color: var(--navy); margin: 0rem 0 0.25rem; }
.weight-card { border-radius: 12px; padding: 0.5rem; text-align: center; height: 72px; display: flex; flex-direction: column; justify-content: center; }
.weight-card__title { font-family: 'Source Sans 3', sans-serif; font-size: 0.85rem; font-weight: 600; line-height: 1; color: var(--navy); }
.weight-card__value { font-family: 'Inter', sans-serif; font-size: 1.75rem; line-height: 1; font-weight: 900; margin-top: 0.35rem; color: var(--navy); }
.map-title { font-family: 'Inter', sans-serif; text-align: center; font-size: 1rem; font-weight: 900; color: var(--navy); letter-spacing: 0.01em; margin-top: 0.5rem; margin-bottom: 0rem; }
.spacer-05 { height: 0.5rem; }
.spacer-08 { height: 0.8rem; }
</style>
""", unsafe_allow_html=True)

df = load_airline_data()

st.markdown('<div class="hero-title">FIND YOUR AIRLINE!</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Customize your preferences, then press “Check” to see the rankings of your airline recomendations.</div>', unsafe_allow_html=True)

# =====================================================================
# FRAGMENT 1: Bagian Atas (Filter & Peta berada dalam satu siklus interaktif)
# =====================================================================
@st.fragment
def render_top_section():
        top_left, top_right = st.columns([0.42, 0.58], gap="medium")
        
        with top_left:
                with st.container(border=True):
                        row_left, row_right = st.columns([0.85, 1.15], vertical_alignment="center")
                        with row_left:
                                st.markdown('<div class="field-label">Airline’s Country</div>', unsafe_allow_html=True)
                        with row_right:
                                countries = get_available_countries()
                                country_options = ["(Semua negara)"] + countries
                                default_country = st.session_state.get("filter_country")
                                country_index = country_options.index(default_country) if default_country in country_options else 0
                                selected_country = st.selectbox(
                                        "Negara Asal Maskapai",
                                        options=country_options,
                                        index=country_index,
                                        label_visibility="collapsed",
                                )
                        filter_country = None if selected_country == "(Semua negara)" else selected_country

                st.markdown('<div class="spacer-08"></div>', unsafe_allow_html=True)

                with st.container(border=True):
                        st.markdown('<div class="field-label center">Cabin Class</div>', unsafe_allow_html=True)
                        st.markdown('<div class="spacer-05"></div>', unsafe_allow_html=True)
                        cabin_options = ["First Class", "Business Class", "Premium Economy", "Economy"]
                        
                        cabin_counts = df["cabin_flown"].value_counts(dropna=True).to_dict() if "cabin_flown" in df.columns else {}
                        selected_cabins = cabin_selector(st.session_state.get("filter_cabin", cabin_options), cabin_counts)

                st.markdown('<div class="spacer-08"></div>', unsafe_allow_html=True)

                with st.container(border=True):
                        row_left, row_right = st.columns([0.85, 1.15], vertical_alignment="center")
                        with row_left:
                                st.markdown('<div class="field-label">Minimum<br>Number of Reviews</div>', unsafe_allow_html=True)
                        with row_right:
                                min_reviews = st.number_input(
                                        "Minimal review valid per maskapai",
                                        min_value=1,
                                        max_value=1000,
                                        value=int(st.session_state.get("ranking_min_reviews", 30)),
                                        step=1,
                                        label_visibility="collapsed",
                                )
                
                st.session_state["filter_country"] = filter_country
                st.session_state["filter_cabin"] = selected_cabins
                st.session_state["ranking_min_reviews"] = int(min_reviews)

        with top_right:
                filtered_df = df.copy()
                if "cabin_flown" in filtered_df.columns and selected_cabins:
                        filtered_df = filtered_df[filtered_df["cabin_flown"].isin(selected_cabins)]
                
                with st.container(border=True):
                        fig_choropleth = build_airline_origin_choropleth(filtered_df)
                        if fig_choropleth:
                                fig_choropleth.update_layout(
                                        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                                        geo=dict(bgcolor='#ffffff', showland=True, landcolor='#86c8f4', showcountries=True, countrycolor='#ffffff', countrywidth=0.5, showframe=False, showcoastlines=False, projection_type='equirectangular'),
                                        margin=dict(l=0, r=0, t=10, b=0), height=310
                                )
                                fig_choropleth.update_traces(showscale=False) 
                                st.plotly_chart(fig_choropleth, use_container_width=True, theme=None, config={"scrollZoom": False, "displayModeBar": False})
                        st.markdown('<div class="map-title">DISTRIBUTION OF DATA</div>', unsafe_allow_html=True)

render_top_section()

# =====================================================================
# FRAGMENT 2: Bagian Slider (Bawah) berjalan mandiri
# =====================================================================
@st.fragment
def render_weights_and_submit():
        st.markdown('<div class="spacer-05"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">How important this criteria is to you?</div>', unsafe_allow_html=True)

        current_weights = st.session_state["score_weights"]
        default_point_1 = int(current_weights["seat"] * 100)
        default_point_2 = default_point_1 + int(current_weights["cabin"] * 100)
        default_point_3 = default_point_2 + int(current_weights["food"] * 100)

        slider_result = triple_range_slider(label="", default_points=(default_point_1, default_point_2, default_point_3))
        ranges = slider_result.get("ranges", {})
        weight_inputs = {
                "seat": ranges.get("var_1", 20),
                "cabin": ranges.get("var_2", 20),
                "food": ranges.get("var_3", 45),
                "entertainment": ranges.get("var_4", 15),
        }

        bottom_cols = st.columns([1, 1, 1, 1, 1.3], gap="medium")
        card_specs = [
                ("Cabin Service", "#86c8f4", "seat"),
                ("Seat Comfort", "#b2e278", "cabin"),
                ("Food & Beverage", "#fecd72", "food"),
                ("Inflight Entertainment", "#ffb2c0", "entertainment"),
        ]

        for i, (label, color, key) in enumerate(card_specs):
                with bottom_cols[i]:
                        st.markdown(
                                f"""
                                <div class="weight-card" style="background:{color};">
                                    <div class="weight-card__title">{html.escape(label)}</div>
                                    <div class="weight-card__value">{weight_inputs[key]}%</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                        )

        total_weight = sum(weight_inputs.values())
        apply_disabled = total_weight != 100

        with bottom_cols[4]:
                if st.button("CHECK!!! ►", type="primary", disabled=apply_disabled, use_container_width=True):
                        normalized_weights = {k: v / 100.0 for k, v in weight_inputs.items()}
                        st.session_state["score_weights"] = normalized_weights
                        st.session_state["ranking_weights"] = {
                                "seat_comfort_rating": normalized_weights["seat"],
                                "cabin_staff_rating": normalized_weights["cabin"],
                                "food_beverages_rating": normalized_weights["food"],
                                "inflight_entertainment_rating": normalized_weights["entertainment"],
                        }
                        
                        st.session_state["ranking_country"] = st.session_state.get("filter_country")
                        st.switch_page("pages/2a_ranking.py")

render_weights_and_submit()