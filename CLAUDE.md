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

## Project Structure (Modular Architecture)

The codebase is organized for scalability and reusability:

```
main.py                  # Entry point: page config, filters, orchestration
utils.py                 # Shared: load_data(), apply_global_filters(), KPI calculations, constants
charts/
  __init__.py
  choropleth.py         # build_choropleth(), build_top15_table()
data/
  cleaned/
    reviews_consolidated.csv
```

**main.py** (~150 lines)
- Page config, title, header
- Sidebar filter controls
- Calls `apply_global_filters()` and `calculate_kpis()`
- Imports and calls chart functions: `build_choropleth()`, `build_top15_table()`
- Renders KPI metrics and charts

**utils.py**
- `load_data()` — cached CSV load + country name normalization
- `apply_global_filters()` — centralized filter logic
- `calculate_kpis()` — computes metrics for KPI strip
- Constants: `COUNTRY_NAME_MAP`, `METRIC_COL`

**charts/choropleth.py**
- `aggregate_for_choropleth(filtered_data)` — country-level aggregations
- `build_choropleth(filtered_data, metric)` — returns Plotly choropleth figure
- `build_top15_table(filtered_data)` — returns formatted DataFrame for display

## Phase 2 Roadmap (Not Yet Implemented)

The plan in `CHOROPLETH-PLAN.md` describes 5 additional charts to add:

1. **Top/Bottom-N Bar Chart** — best/worst entities by overall_rating
2. **Line Chart** — monthly/yearly rating trends, one line per review_type
3. **Heatmap** — sub-ratings by cabin class (airline reviews only, ~30 lines of code)
4. **Scatter** — overall_rating vs avg_sub_rating, colored by recommended
5. **Word Cloud** — split recommended=yes vs no (requires `wordcloud` package)

### Adding a Phase 2 Chart

Each chart module exports a `build_<chart_name>(filtered_data) → fig` function:

**1. Create `charts/new_chart.py`**
```python
import plotly.express as px

def build_bar_chart(filtered_data: pd.DataFrame) -> px.bar:
    """Build a bar chart showing top entities by overall_rating."""
    if len(filtered_data) == 0:
        return None
    
    agg = filtered_data.groupby("entity_name").agg({
        "overall_rating": "mean",
        "author_country": "count"
    }).rename(columns={"author_country": "count"}).reset_index()
    
    fig = px.bar(agg.nlargest(15, "overall_rating"), ...)
    return fig
```

**2. Update `main.py`**
```python
from charts.new_chart import build_bar_chart

# After choropleth section:
st.subheader("📊 Top Entities by Rating")
if len(filtered_data) > 0:
    fig = build_bar_chart(filtered_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
```

**Key points:**
- All chart functions receive pre-filtered `filtered_data` from main.py
- No filter duplication—filters are centralized in `apply_global_filters()`
- Return `None` for empty data; main.py handles rendering
- Keep aggregation logic inside the chart module

## Common Development Tasks

### Add a new sidebar filter
1. Create the `st.sidebar.multiselect()` or `st.sidebar.slider()` control in main.py
2. Add filter logic to `apply_global_filters()` in utils.py
3. Pass the filter variable to `apply_global_filters()` call
4. All chart functions automatically receive the updated `filtered_data`

### Add a new chart
1. Create a new file in `charts/` (e.g., `charts/bar_chart.py`)
2. Implement `build_<chart_name>(filtered_data)` function that returns a Plotly figure
3. Import and call the function in main.py, wrapping with `if len(filtered_data) > 0:`
4. No need to duplicate filter logic—chart receives pre-filtered data

### Debug a filter issue
- Add `st.write(filtered_data.head())` in main.py to inspect rows after filtering
- Check `filtered_data.shape` to see row count
- Verify filter values with `st.sidebar.write(filter_variable)`
- Test filter logic directly: `python -c "from utils import apply_global_filters; ..."`

### Optimize performance
- Main bottleneck: loading the 47 MB CSV. `@st.cache_data` on `load_data()` ensures it loads once per session.
- For heavy chart computation, add `@st.cache_data` to aggregation functions in chart modules, keyed on filter state
- Aggregate once in a chart function, reuse for multiple metrics if possible

## Known Gotchas

1. **Column availability** — `cabin_flown` and `type_traveller` don't exist in the consolidated CSV. Always check `if "column" in df.columns` before filtering on category-specific columns.

2. **Country name mismatches** — If a new country appears in the data that Plotly doesn't recognize, the choropleth will silently drop it. Add it to COUNTRY_NAME_MAP if needed.

3. **Year range quirk** — The data spans 1970–2015, but most reviews are 2004–2015. Early years have sparse data.

4. **Cached data stale on filter UI changes** — If you add a new filter, Streamlit may keep old cached data. Run `streamlit cache clear` to reset.

## CI/CD Pipeline

GitHub Actions runs a simple deployment check on every push to `main` or `chloropleth`, and on all pull requests:

1. Installs dependencies from `requirements.txt`
2. Creates minimal test data (stub CSV)
3. Attempts to load the Streamlit app

If the app loads without errors, deployment is safe. If it fails, the PR is blocked.

## File References

- **`CHOROPLETH-PLAN.md`** — Detailed implementation plan, Phase 2 chart blueprints, 27-point verification checklist
- **`DATASET-METADATA.md`** — Complete schema, null rates, column descriptions, known limitations
- **`README.md`** — Setup instructions (venv, installing dependencies)
- **`.github/workflows/ci.yml`** — GitHub Actions deployment check configuration
