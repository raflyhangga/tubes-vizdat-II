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

# Custom CSS for the landing page
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap');
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Set overall background color */
    .stApp {
        background-color: #dceef8;
    }

    /* Container Styling */
    .hero-container {
        font-family: 'Source Sans 3', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 2rem;
    }

    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: #1f2234;
        text-align: center;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }

    .description {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1.1rem;
        color: #1f2234;
        text-align: center;
        max-width: 700px;
        line-height: 1.5;
        margin-bottom: 2rem;
    }

    /* Card Styling */
    .data-card {
        background-color: transparent;
        width: 100%;
        max-width: 750px;
        margin-bottom: 2.5rem;
    }

    .card-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #1f2234;
        text-align: center;
        line-height: 1;
        margin-bottom: 0.8rem;
    }

    .card-subtitle {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1rem;
        color: #1f2234;
        text-align: center;
        margin-bottom: 1.5rem;
        line-height: 1.4;
    }

    /* Chart Layout */
    .chart-wrapper {
        display: flex;
        align-items: stretch;
        margin-top: 1rem;
    }

    /* Left Side: Labels and Icons */
    .y-axis-labels {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        padding-right: 15px;
        width: 200px;
        padding-top: 5px;
        padding-bottom: 25px;
    }

    .label-row {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 12px;
        height: 50px;
    }

    .label-text {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.95rem;
        text-align: right;
    }
    
    .label-text.highlight {
        color: #1f2234;
        font-weight: 700;
    }

    .label-text.normal {
        color: #1f2234;
        font-weight: 400;
    }

    .icon-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .icon-circle.highlight { background-color: #1f2234; }
    .icon-circle.normal { background-color: #1c78ba; }

    .icon-circle svg {
        width: 20px;
        height: 20px;
        fill: white;
    }

    /* Right Side: Plot Area */
    .plot-area {
        flex: 1;
        position: relative;
        border-left: 1px solid #1c78ba;
        border-bottom: 1px solid #1c78ba;
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        padding-top: 5px;
        padding-bottom: 5px;
    }

    /* Grid Lines Background */
    .grid-lines {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 0;
    }

    .grid-line {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 1px;
        background-color: rgba(28, 120, 186, 0.15);
    }

    /* Bars */
    .bar-row {
        display: flex;
        align-items: center;
        position: relative;
        z-index: 1;
        height: 50px;
    }

    .bar {
        height: 32px;
        /* No border radius on the right in your new image */
    }

    .bar.highlight { background-color: #1f2234; }
    .bar.normal { background-color: #1c78ba; }

    .bar-value {
        font-family: 'Inter', sans-serif; /* Explicitly Inter font */
        font-size: 1.15rem;
        margin-left: 8px;
        font-weight: 400;
    }

    .bar-value.highlight { color: #1f2234; }
    .bar-value.normal { color: #1c78ba; }

    /* X-Axis Footer */
    .x-axis {
        position: relative;
        height: 20px;
        margin-top: 5px;
        font-family: 'Source Sans 3', sans-serif;
        color: #1f2234;
        font-size: 0.8rem;
    }

    .x-axis span {
        position: absolute;
        transform: translateX(-50%);
    }

    .x-axis-title {
        text-align: center;
        font-family: 'Source Sans 3', sans-serif;
        color: #1f2234;
        font-size: 0.85rem;
        margin-top: 2px;
    }

    /* CTA Button Override */
    div.stButton > button {
        background-color: #1f2234 !important;
        border: none !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 8px 15px rgba(31, 34, 52, 0.2) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px rgba(31, 34, 52, 0.3) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# HTML Structure for the UI
st.html(
    """
    <div class="hero-container">

        <div class="main-title">WHAT DRIVES AIRLINE SATISFACTION?</div>

        <div class="description">Linear regression of 17.803 economic fligh reviews identifies which service factors were most significant to the overall passenger rating.</div>
        <div class="data-card">
            <div class="card-title">CABIN SERVICE IS THE KEY DRIVER</div>
            <div class="card-subtitle">Standardized Coefficient measures each factor's relative contribution to overall satisfaction.<br>The higher the value, the stronger the predictor.</div>
            
            <div class="chart-wrapper">
                <div class="y-axis-labels">
                    <div class="label-row">
                        <span class="label-text highlight">Cabin Service</span>
                        <div class="icon-circle highlight">
                            <svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
                        </div>
                    </div>
                    <div class="label-row">
                        <span class="label-text normal">Seat Comfort</span>
                        <div class="icon-circle normal">
                            <svg viewBox="0 0 24 24"><path d="M7.59 5.41c-.78-.78-.78-2.05 0-2.83.78-.78 2.05-.78 2.83 0 .78.78.78 2.05 0 2.83-.79.79-2.05.79-2.83 0zM6 16V7H4v9c0 2.76 2.24 5 5 5h6v-2H9c-1.65 0-3-1.35-3-3zm14 4.07L14.93 15H11.5v-3.68c1.4 1.15 3.6 2.16 5.5 2.16v-2.16c-1.66.02-3.61-.87-4.67-2.04l-1.4-1.55c-.19-.21-.43-.38-.69-.5-.29-.14-.62-.23-.96-.23h-.03C8.01 7 7 8.01 7 9.25V15c0 1.66 1.34 3 3 3h5.07l3.5 3.5L20 20.07z"/></svg>
                        </div>
                    </div>
                    <div class="label-row">
                        <span class="label-text normal">Food & Beverage</span>
                        <div class="icon-circle normal">
                            <svg viewBox="0 0 24 24"><path d="M11 9H9V2H7v7H5V2H3v7c0 2.12 1.66 3.84 3.75 3.97V22h2.5v-9.03C11.34 12.84 13 11.12 13 9V2h-2v7zm5-3v8h2.5v8H21V2c-2.76 0-5 2.24-5 4z"/></svg>
                        </div>
                    </div>
                    <div class="label-row">
                        <span class="label-text normal" style="line-height: 1.2;">Inflight<br>Entertainment</span>
                        <div class="icon-circle normal">
                            <svg viewBox="0 0 24 24"><path d="M21 5H3C1.9 5 1 5.9 1 7v10c0 1.1 0.9 2 2 2h2.5l-1.5 2.5h1.8L7.5 19h9l1.7 2.5h1.8l-1.5-2.5H21c1.1 0 2-0.9 2-2V7c0-1.1-0.9-2-2-2zM21 17H3V7h18v10zM10 9v6l5-3z"/></svg>
                        </div>
                    </div>
                </div>

                <div class="plot-area">
                    <div class="grid-lines">
                        <div class="grid-line" style="left: 20%;"></div>
                        <div class="grid-line" style="left: 40%;"></div>
                        <div class="grid-line" style="left: 60%;"></div>
                        <div class="grid-line" style="left: 80%;"></div>
                    </div>

                    <div class="bar-row">
                        <div class="bar highlight" style="width: 75.7%;"></div>
                        <span class="bar-value highlight">0.757</span>
                    </div>
                    <div class="bar-row">
                        <div class="bar normal" style="width: 58.8%;"></div>
                        <span class="bar-value normal">0.588</span>
                    </div>
                    <div class="bar-row">
                        <div class="bar normal" style="width: 23.0%;"></div>
                        <span class="bar-value normal">0.230</span>
                    </div>
                    <div class="bar-row">
                        <div class="bar normal" style="width: 10.0%;"></div>
                        <span class="bar-value normal">0.100</span>
                    </div>
                </div>
            </div>

            <div style="margin-left: 200px;"> 
                <div class="x-axis">
                    <span style="left: 20%">0.2</span>
                    <span style="left: 40%">0.4</span>
                    <span style="left: 60%">0.6</span>
                    <span style="left: 80%">0.8</span>
                </div>
                <div class="x-axis-title">Standardized Coefficient</div>
            </div>
        </div>
    </div>
    """
)

# CTA button
col_l, col_c, col_r = st.columns([1, 1.5, 1])
with col_c:
    if st.button(
        "FIND YOUR PERSONALIZATION HERE!",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/2_ranking.py")