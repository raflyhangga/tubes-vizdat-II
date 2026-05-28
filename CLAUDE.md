# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tubes Vizdat II** is an analytical dashboard for the **Skytrax 2015 reviews dataset** built with Streamlit. It visualizes airline, airport, lounge, and seat reviews across 167 countries with interactive filters and multi-metric analysis.

**Current Status:** Phase 1 complete (choropleth map + KPI strip + global filter architecture)

## Quick Start

### Run the Dashboard
```bash
# Activate venv (Windows)
.venv\Scripts\Activate.ps1

# Run the app
streamlit run main.py

# Dashboard opens at http://localhost:8501
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Streamlit Installation
```bash
streamlit hello
```

## Architecture & Design

### Global Filter Architecture (Key Pattern)
All visualizations consume a single `filtered_data` DataFrame. The pattern:

1. **Sidebar controls** → populate individual filter variables (review_types, year_range, author_country, etc.)
2. **`apply_global_filters()`** → centralizes all filter logic, returns filtered_data
3. **Per-chart aggregation** → `filtered_data.groupby(...).agg(...)`
4. **Chart render** → `st.plotly_chart(fig)`

**Why this matters:** Phase 2 adds 5 new charts (bar, line, heatmap, scatter, word cloud). Each reuses the same filtered_data, so there's no filter duplication or state management complexity.

### Data Flow

```
data/cleaned/reviews_consolidated.csv (55K rows, 14 columns)
    ↓
load_data() [cached with @st.cache_data]
    ↓
Country name normalization (COUNTRY_NAME_MAP)
    ↓
apply_global_filters(review_type, year_range, author_country, ...)
    ↓
filtered_data (dynamic based on sidebar selections)
    ↓
Per-chart aggregation (groupby, agg)
    ↓
Plotly visualization (choropleth, KPI cards, table)
```

### Critical Implementation Details

**Country Name Normalization**
- The consolidated CSV has free-text country names (e.g., "Russian Federation", "Trinidad & Tobago")
- Plotly's `locationmode='country names'` requires exact matches
- `COUNTRY_NAME_MAP` dict handles ~12 edge cases (Russia, North Macedonia, Palestine, etc.)
- Rows where country → None are dropped before visualization

**Missing Columns in Consolidated CSV**
- The consolidated file has only 14 shared columns across all review types
- `cabin_flown` and `type_traveller` do NOT exist in consolidated (only in category-specific CSVs)
- **Fix applied:** All sidebar filters check `if "column" in df.columns` before accessing
- Unavailable filters show info messages instead of crashing

**Data Caching**
- `@st.cache_data` on `load_data()` ensures the 47 MB CSV loads once per session
- Country name replacement happens inside the cached function, so normalization is done once

## Data Sources

### Files Used
- **Primary:** `data/cleaned/reviews_consolidated.csv` (55,611 rows after null-filtering)
- **Reference:** `data/cleaned/{airline,airport,lounge,seat}_clean.csv` (for Phase 2+ if expanding beyond consolidated)
- **Metadata:** `DATASET-METADATA.md` (comprehensive schema and column descriptions)

### Dataset Overview
- **Total rows:** 62,633 (raw), 55,611 (after null-filtering author_country)
- **Date range:** 1970–2015 (2015 is data collection date)
- **Columns:** review_type, entity_name, author, author_country, date, content, title, overall_rating, recommended, recommended_int, review_year, review_month, avg_sub_rating, review_word_count
- **Review types:** airline (41K), airport (17K), lounge (2K), seat (1K)

## Main.py Structure

The app is a single-file implementation (~240 lines) organized as:

1. **Imports & Config** (streamlit, pandas, plotly, page config)
2. **Constants** (COUNTRY_NAME_MAP, METRIC_COL, etc.)
3. **Functions**
   - `load_data()` — cached CSV load + normalization
   - `apply_global_filters()` — centralizes all filter logic
   - `aggregate_for_choropleth()` — country-level aggregation
4. **Main execution**
   - Sidebar filters
   - `filtered_data = apply_global_filters(...)`
   - KPI strip (4 st.metric cards)
   - Choropleth map (px.choropleth)
   - Top-15 table

## Phase 2 Roadmap (Not Yet Implemented)

The plan in `CHOROPLETH-PLAN.md` describes 5 additional charts to add:

1. **Top/Bottom-N Bar Chart** — best/worst entities by overall_rating
2. **Line Chart** — monthly/yearly rating trends, one line per review_type
3. **Heatmap** — sub-ratings by cabin class (airline reviews only, ~30 lines of code)
4. **Scatter** — overall_rating vs avg_sub_rating, colored by recommended
5. **Word Cloud** — split recommended=yes vs no (requires `wordcloud` package)

Each follows the pattern:
```python
agg_data = filtered_data.groupby(...).agg(...)
fig = px.<chart_type>(...)
st.plotly_chart(fig, use_container_width=True)
```

**To add a Phase 2 chart:**
1. Aggregate `filtered_data` by your grouping dimension
2. Create the Plotly figure
3. Add `st.subheader()` and `st.plotly_chart()` to main.py
4. No filter changes needed — they all consume the same `filtered_data`

## Common Development Tasks

### Debug a filter issue
- Add `st.write(filtered_data.head())` to inspect what rows are present after filtering
- Check `filtered_data.shape` to see row count at each filter stage
- Use `st.sidebar.write(review_type_filter)` to verify sidebar values are correct

### Add a new sidebar filter
1. Create the `st.sidebar.multiselect()` or `st.sidebar.slider()` control
2. Add logic to `apply_global_filters()` to apply the filter
3. Call `apply_global_filters()` again with the new parameter
4. All charts automatically react (they use filtered_data)

### Optimize performance
- The main bottleneck is loading the 47 MB CSV; `@st.cache_data` prevents this from running on every interaction
- If you add charts that do heavy computation, wrap them in `@st.cache_data` keyed on filter values
- Avoid groupby on 55K rows more than necessary; aggregate once, render multiple charts if possible

### Test without Streamlit
- Use `python -c` to test data loading, filtering, and aggregation logic directly
- Example: `python -c "import pandas as pd; df = pd.read_csv('data/cleaned/reviews_consolidated.csv'); print(df.shape)"`

## Known Gotchas

1. **Column availability** — `cabin_flown` and `type_traveller` don't exist in the consolidated CSV. Always check `if "column" in df.columns` before filtering on category-specific columns.

2. **Country name mismatches** — If a new country appears in the data that Plotly doesn't recognize, the choropleth will silently drop it. Add it to COUNTRY_NAME_MAP if needed.

3. **Year range quirk** — The data spans 1970–2015, but most reviews are 2004–2015. Early years have sparse data.

4. **Cached data stale on filter UI changes** — If you add a new filter, Streamlit may keep old cached data. Run `streamlit cache clear` to reset.

## File References

- **`CHOROPLETH-PLAN.md`** — Detailed implementation plan, Phase 2 chart blueprints, 27-point verification checklist
- **`DATASET-METADATA.md`** — Complete schema, null rates, column descriptions, known limitations
- **`README.md`** — Setup instructions (venv, installing dependencies)
