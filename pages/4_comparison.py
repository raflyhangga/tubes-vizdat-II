import streamlit as st
import pandas as pd

from utils import (
    load_airline_data,
    SUB_RATING_COLS,
    INDUSTRY_BENCHMARK,
    get_airline_country,
    get_airline_review_summary,
    slug_to_display,
    get_airline_subrating_means,
)
from charts.radar import build_radar
from charts.boxplot import (
    build_single_airline_subrating_boxplot,
    build_comparison_subrating_boxplots,
)

st.set_page_config(page_title="Airline Comparison", layout="wide")

PAGE_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600;700&display=swap');

.stApp {
    background: #d5eafe;
    font-family: 'Source Sans 3', sans-serif;
    --primary-color: #1c78bb;
    --primary-background-color: #1c78bb;
}
.stApp .css-18e3th9 {
    background: #d5eafe;
}
.stApp [data-baseweb="tag"] {
    background-color: #1c78bb !important;
    border-color: #1c78bb !important;
    color: #ffffff !important;
}
.stApp [data-baseweb="tag"] button {
    color: #ffffff !important;
}
.comparison-page__title {
    text-align: center;
}
.comparison-page__title h1 {
    color: #1f2234;
    font-family: 'Inter', sans-serif;
    font-size: 2.6rem;
    margin: 0 0 0.35rem 0;
}
.comparison-page__subtitle {
    text-align: center;
    color: #1f2234;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 1rem;
    line-height: 1.6;
    max-width: 760px;
    margin: 0 auto 1.5rem auto;
}
.comparison-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 0.85rem 1rem;
    box-shadow: 0 12px 24px rgba(31, 34, 52, 0.08);
    color: #1f2234;
    margin-bottom: 0.75rem;
    font-family: 'Source Sans 3', sans-serif;
}
.comparison-card-heading {
    font-size: 0.95rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    margin-bottom: 0.25rem;
}
.comparison-card-subtitle {
    font-size: 0.8rem;
    color: #6b7280;
    margin-bottom: 0.8rem;
}
.comparison-card-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    align-items: start;
}
.comparison-card-metric-label {
    font-size: 0.72rem;
    color: #1c78bb;
    font-weight: 700;
    margin-bottom: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.comparison-card-metric-value,
.comparison-card-metric-unit {
    display: inline-block;
    vertical-align: middle;
}
.comparison-card-metric-value {
    font-size: 1.25rem;
    color: #1f2234;
    font-weight: 800;
    line-height: 1.05;
    white-space: nowrap;
}
.comparison-card-metric-unit {
    font-size: 0.88rem;
    color: #6b7280;
    margin-left: 0.35rem;
}
.comparison-section-title {
    color: #1f2234;
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.9rem;
}
.stButton>button[kind="primary"], .stButton button[kind="primary"] {
    background-color: #1c78bb !important;
    color: #ffffff !important;
    border-color: #1c78bb !important;
    font-family: 'Source Sans 3', sans-serif;
}
.stButton>button[kind="primary"]:hover, .stButton button[kind="primary"]:hover {
    background-color: #1667a1 !important;
}
.stButton>button[kind="primary"]:focus-visible, .stButton button[kind="primary"]:focus-visible {
    box-shadow: 0 0 0 3px rgba(28, 120, 187, 0.3) !important;
}
</style>
"""

st.markdown(PAGE_STYLE, unsafe_allow_html=True)

df = load_airline_data()

st.markdown(
    "<div class='comparison-page__title'><h1>Airline Comparison</h1></div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='comparison-page__subtitle'>Choose a default airline, then select up to 3 airlines to compare. Press <strong>Apply</strong> to display the radar and boxplots.</div>",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data state
# -----------------------------------------------------------------------------
vc = df["airline_name"].value_counts()

default_country = st.session_state.get("page4_country") or "United Kingdom"
page4_applied = st.session_state.get("page4_applied", False)

page4_default_airline = st.session_state.get("page4_default_airline")
page4_compare_airlines = st.session_state.get("page4_compare_airlines", [])
legacy_compare = st.session_state.get("compare_airlines", [])

if not page4_default_airline and legacy_compare:
    page4_default_airline = legacy_compare[0]

if not page4_compare_airlines and legacy_compare:
    page4_compare_airlines = legacy_compare[1:]

active_slugs = [
    slug
    for slug in [page4_default_airline] + page4_compare_airlines
    if slug
]

active_df = (
    df[df["airline_name"].isin(active_slugs)]
    if active_slugs
    else pd.DataFrame()
)

boxplot_rating_columns = [
    col for col in SUB_RATING_COLS
    if col != "value_money_rating"
]

# -----------------------------------------------------------------------------
# Default single airline for the initial boxplot
# -----------------------------------------------------------------------------
default_country_name = st.session_state.get("page4_country") or default_country

if default_country_name == "(Semua negara)":
    default_country_airlines = df["airline_name"].unique().tolist()
else:
    default_country_airlines = [
        a for a in df["airline_name"].unique()
        if get_airline_country(a) == default_country_name
    ]

default_country_airlines_sorted = sorted(
    default_country_airlines,
    key=lambda a: -vc.get(a, 0)
)

default_single_slug = (
    default_country_airlines_sorted[0]
    if default_country_airlines_sorted
    else None
)

# -----------------------------------------------------------------------------
# Helper: render radar
# -----------------------------------------------------------------------------
def render_radar():
    st.markdown("<div class='comparison-section-title'>Airline Comparison Radar</div>", unsafe_allow_html=True)

    if active_slugs:
        airlines_data = {
            slug_to_display(slug): get_airline_subrating_means(
                active_df[active_df["airline_name"] == slug],
                SUB_RATING_COLS
            ).to_dict()
            for slug in active_slugs
        }

        fig_radar = build_radar(
            airlines_data=airlines_data,
            benchmark=INDUSTRY_BENCHMARK
        )

        st.plotly_chart(fig_radar, use_container_width=True)

    else:
        st.info("Select airlines and press Apply to view the comparison radar.")


# -----------------------------------------------------------------------------
# Helper: airline label
# -----------------------------------------------------------------------------
def _airline_display_label(slug: str) -> str:
    return f"{slug_to_display(slug)} ({get_airline_country(slug)})"


def _sort_airlines_by_country_priority(
    reference_slug: str | None,
    slugs: list[str]
) -> list[str]:
    reference_country = get_airline_country(reference_slug) if reference_slug else None

    def sort_key(slug: str):
        country = get_airline_country(slug)
        same_country = country == reference_country

        return (
            0 if same_country else 1,
            country.lower(),
            slug_to_display(slug).lower(),
        )

    return sorted(slugs, key=sort_key)


# -----------------------------------------------------------------------------
# Helper: render filter form
# -----------------------------------------------------------------------------
def render_filter_form():
    all_airlines = df["airline_name"].unique().tolist()
    selected_default = page4_default_airline or default_single_slug

    default_airline_order = _sort_airlines_by_country_priority(
        selected_default,
        all_airlines,
    )

    default_display_options = {
        _airline_display_label(slug): slug
        for slug in default_airline_order
    }

    default_labels = list(default_display_options.keys())

    default_index = (
        default_labels.index(_airline_display_label(selected_default))
        if selected_default and _airline_display_label(selected_default) in default_labels
        else 0
    )

    selected_default_label = st.selectbox(
        "Default Airline",
        options=default_labels,
        index=default_index,
        key="page4_default_airline_display",
    )

    selected_default_slug = default_display_options[selected_default_label]

    compare_candidates = [
        slug for slug in all_airlines
        if slug != selected_default_slug
    ]

    compare_order = _sort_airlines_by_country_priority(
        selected_default_slug,
        compare_candidates,
    )

    compare_display_options = {
        _airline_display_label(slug): slug
        for slug in compare_order
    }

    pre_selected_compare = (
        page4_compare_airlines
        if page4_compare_airlines
        else [slug for slug in active_slugs if slug != selected_default_slug]
    )

    pre_selected_compare_display = [
        _airline_display_label(slug)
        for slug in pre_selected_compare
        if slug in compare_order
    ]

    selected_compare_display = st.multiselect(
        "Select up to 3 airlines to compare",
        options=list(compare_display_options.keys()),
        default=pre_selected_compare_display,
        max_selections=3,
        key="page4_compare_airlines_display",
    )

    selected_compare_slugs = [
        compare_display_options[label]
        for label in selected_compare_display
    ]

    if st.button("Apply", type="primary", key="page4_apply_button"):
        st.session_state["page4_default_airline"] = selected_default_slug
        st.session_state["page4_compare_airlines"] = selected_compare_slugs
        st.session_state["compare_airlines"] = [
            selected_default_slug,
            *selected_compare_slugs,
        ]
        st.session_state["page4_country"] = get_airline_country(selected_default_slug)
        st.session_state["page4_applied"] = True
        st.rerun()


# -----------------------------------------------------------------------------
# Helper: render airline info cards
# -----------------------------------------------------------------------------
def render_airline_info_cards():
    default_airline = st.session_state.get("page4_default_airline")
    compare_slugs = st.session_state.get("page4_compare_airlines", [])

    if default_airline:
        summary = get_airline_review_summary(df[df["airline_name"] == default_airline])
        submeans = get_airline_subrating_means(df[df["airline_name"] == default_airline], boxplot_rating_columns)
        composite = float(submeans.mean()) if not submeans.isna().all() else 0.0
        airline_label = f"{slug_to_display(default_airline)} ({get_airline_country(default_airline)})"

        with st.container():
            st.markdown(
                f"""
                <div class='comparison-card'>
                    <div class='comparison-card-heading'>{airline_label}</div>
                    <div class='comparison-card-grid'>
                        <div>
                            <div class='comparison-card-metric-label'>Composite Score</div>
                            <div class='comparison-card-metric-value'>{composite:.2f} <span class='comparison-card-metric-unit'>/ 5</span></div>
                        </div>
                        <div>
                            <div class='comparison-card-metric-label'>Recommendation</div>
                            <div class='comparison-card-metric-value'>{summary.get('pct_recommended', 0):.1f}%</div>
                        </div>
                        <div>
                            <div class='comparison-card-metric-label'>Reviews</div>
                            <div class='comparison-card-metric-value'>{int(summary.get('review_count', 0))}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if compare_slugs:
        for slug in compare_slugs:
            submeans = get_airline_subrating_means(df[df["airline_name"] == slug], boxplot_rating_columns)
            composite = float(submeans.mean()) if not submeans.isna().all() else 0.0
            summary = get_airline_review_summary(df[df["airline_name"] == slug])
            airline_label = f"{slug_to_display(slug)} ({get_airline_country(slug)})"

            with st.container():
                st.markdown(
                    f"""
                    <div class='comparison-card'>
                        <div class='comparison-card-heading'>{airline_label}</div>
                        <div class='comparison-card-grid'>
                            <div>
                                <div class='comparison-card-metric-label'>Composite Score</div>
                                <div class='comparison-card-metric-value'>{composite:.2f} <span class='comparison-card-metric-unit'>/ 5</span></div>
                            </div>
                            <div>
                                <div class='comparison-card-metric-label'>Recommendation</div>
                                <div class='comparison-card-metric-value'>{summary.get('pct_recommended', 0):.1f}%</div>
                            </div>
                            <div>
                                <div class='comparison-card-metric-label'>Reviews</div>
                                <div class='comparison-card-metric-value'>{int(summary.get('review_count', 0))}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No comparison airlines selected yet.")

    if st.button("Edit Filter", key="page4_edit_button"):
        st.session_state["page4_applied"] = False
        st.rerun()


def render_default_info_box(slug: str | None):
    if not slug:
        return
    summary = get_airline_review_summary(df[df["airline_name"] == slug])
    submeans = get_airline_subrating_means(df[df["airline_name"] == slug], boxplot_rating_columns)
    composite = float(submeans.mean()) if not submeans.isna().all() else 0.0
    airline_label = f"{slug_to_display(slug)} ({get_airline_country(slug)})"
    st.markdown(
        f"""
        <div class='comparison-card'>
            <div class='comparison-card-heading'>{airline_label}</div>
            <div class='comparison-card-grid'>
                <div>
                    <div class='comparison-card-metric-label'>Composite Score</div>
                    <div class='comparison-card-metric-value'>{composite:.2f} <span class='comparison-card-metric-unit'>/ 5</span></div>
                </div>
                <div>
                    <div class='comparison-card-metric-label'>Recommendation</div>
                    <div class='comparison-card-metric-value'>{summary.get('pct_recommended', 0):.1f}%</div>
                </div>
                <div>
                    <div class='comparison-card-metric-label'>Reviews</div>
                    <div class='comparison-card-metric-value'>{int(summary.get('review_count', 0))}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# ROW 1
# -----------------------------------------------------------------------------
if page4_applied:
    # After Apply button:
    # Row 1 remains 2 columns:
    # column 1 = radar chart
    # column 2 = airline info cards
    radar_col, info_col = st.columns([1, 1], gap="large")

    with radar_col:
        render_radar()

    with info_col:
        render_airline_info_cards()

else:
    # Before Apply button:
    # Row 1 consists of 2 columns:
    # column 1 = radar chart
    # column 2 = filter
    radar_col, filter_col = st.columns([2, 1], gap="large")

    with radar_col:
        render_radar()
        # show compact default airline info under radar for quick glance
        current_default = st.session_state.get("page4_default_airline", default_single_slug)
        render_default_info_box(current_default)

    with filter_col:
        st.markdown("#### Filter")
        render_filter_form()


# -----------------------------------------------------------------------------
# ROW 2: Boxplot
# -----------------------------------------------------------------------------
st.markdown("---")

if not page4_applied:
    single_slug = st.session_state.get(
        "page4_default_airline",
        default_single_slug
    )

    if single_slug:
        st.markdown("#### Default Airline Subrating Boxplot")

        single_df = df[df["airline_name"] == single_slug]

        fig_single = build_single_airline_subrating_boxplot(
            single_df,
            single_slug,
            boxplot_rating_columns
        )

        st.plotly_chart(fig_single, use_container_width=True)

else:
    if len(active_slugs) >= 2:
        figures = build_comparison_subrating_boxplots(
            active_df,
            active_slugs,
            boxplot_rating_columns
        )

        boxplot_cols = st.columns(len(figures), gap="small")

        for fig, col in zip(figures, boxplot_cols):
            with col:
                st.plotly_chart(fig, use_container_width=True)

    elif active_slugs:
        st.info(
            "Add at least one more airline to see the comparison."
        )

    else:
        st.info(
            "Select airlines and press Apply to show the comparison boxplots."
        )