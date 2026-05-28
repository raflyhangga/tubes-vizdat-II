# Plan: Analytical Dashboard with Global Filters (Streamlit)

## Context

This Skytrax (2015) review dataset project is a nearly blank Streamlit app (`main.py` is a 7-line placeholder). The goal is to build a multi-chart analytical dashboard centered around a **global filter architecture** that drives all visualizations reactively. The dashboard covers operational KPIs, strategic comparisons, and deep analytical insights across airlines, airports, lounges, and seat reviews.

**Data snapshot:**
- 62,633 total rows across all review types (airline, airport, lounge, seat)
- 167 unique reviewer countries
- 11.2% null rate on `author_country` (airport reviews highest at 27.9%)
- Top countries: UK (15,837), US (11,099), Australia (6,726)

**Vision:** A cohesive dashboard where every chart and card updates in response to a single sidebar filter panel, enabling users to drill down from global trends to specific airlines, cabins, traveller types, countries, or date ranges.

**Decisions:** 
- Plotly Express for interactive charts (choropleth, bar, line, scatter, heatmap)
- Global filter state managed in sidebar
- Reviews consolidated CSV as the primary data source
- Phase 1: Build choropleth + KPI strip + filter plumbing; Phase 2: Add remaining 5 charts

---

## Tech Stack

| Package | Version | Role |
|---|---|---|
| `streamlit` | 1.57.0 | App framework — already installed |
| `pandas` | 3.0.3 | Data loading and aggregation — already installed |
| `plotly` | ≥5.24.0 | Choropleth map — **must be added to requirements.txt** |

---

## Files to Modify

| File | Change |
|---|---|
| `requirements.txt` | Append `plotly>=5.24.0` |
| `main.py` | Full rewrite (~200+ lines for Phase 1) |

No new files or directories needed for Phase 1. Future phases may refactor into `utils/filters.py` and `components/charts.py` as complexity grows.

---

## Dashboard Architecture Overview

### Phase 1 (MVP) — This Plan
- ✅ Global filter sidebar (5 controls)
- ✅ KPI strip (4 metric cards)
- ✅ Choropleth map (reviewer countries)

### Phase 2+ (Future) - Don't implement this
- 📊 Top/Bottom-N bar chart (best/worst entities)
- 📈 Line chart (rating trends over time)
- 🔥 Heatmap (sub-rating dimensions)
- 🔷 Scatter (avg_sub_rating vs overall_rating)
- ☁️ Word cloud (recommended yes vs no)

All charts will share the same filter state from the sidebar. The filter logic is centralized, so adding new charts only requires a single aggregation + plot statement.

---

## Implementation Steps


### Step 2 — Country Name Normalization Dictionary

`px.choropleth` with `locationmode='country names'` uses Plotly's built-in name mapping. Most names in the dataset match Plotly's expected values directly, but ~12 edge cases need a rename before charting. Define this as a module-level constant at the top of `main.py`:

```python
COUNTRY_NAME_MAP = {
    "Russian Federation":      "Russia",
    "Trinidad & Tobago":       "Trinidad and Tobago",
    "Wallis & Futuna Islands": "Wallis and Futuna",
    "Macedonia":               "North Macedonia",
    "East Timor":              "Timor-Leste",
    "Palestinian Territories": "Palestine",
    "Hong Kong":               "China",           # territory, maps to China
    "Netherlands Antilles":    None,              # dissolved — will be dropped
}
```

Apply via `.replace()`, then drop rows where the value is `None` or empty.

---

### Step 3 — Data Loading (Cached)

Wrap the 47 MB CSV load in `@st.cache_data` so it only runs once per session:

```python
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(
        "data/cleaned/reviews_consolidated.csv",
        parse_dates=["date"]
    )
    df["author_country"] = df["author_country"].replace(COUNTRY_NAME_MAP)
    df = df[df["author_country"].notna() & (df["author_country"].str.strip() != "")]
    return df
```

Call this once at the top of the script: `df = load_data()`

---

### Step 4 — Global Filter Panel (Sidebar)

Five controls in the sidebar drive ALL charts and KPI cards. Centralize the filter logic so every chart references `st.session_state` or the returned filter dict.

#### 4a. Review Type Multiselect
```python
review_types = st.sidebar.multiselect(
    "Review Type",
    options=["All", "airline", "airport", "lounge", "seat"],
    default=["All"],
)
# When "All" is selected, include all types; otherwise use the selected list
if "All" in review_types or not review_types:
    review_type_filter = df["review_type"].unique().tolist()
else:
    review_type_filter = review_types
```

#### 4b. Year Range Slider
```python
year_min_data = int(df["review_year"].min())
year_max_data = int(df["review_year"].max())

year_range = st.sidebar.slider(
    "Year range",
    min_value=year_min_data,
    max_value=year_max_data,
    value=(year_min_data, year_max_data),
)
```

#### 4c. Cabin Flown (category filter — airline-specific)
```python
cabin_options = sorted([x for x in df["cabin_flown"].dropna().unique() if pd.notna(x)])
cabin_flown = st.sidebar.multiselect(
    "Cabin Class (applies to airline reviews only)",
    options=cabin_options,
    default=cabin_options,
)
```

#### 4d. Traveller Type (category filter — sparse across categories)
```python
traveller_options = sorted([x for x in df["type_traveller"].dropna().unique() if pd.notna(x)])
type_traveller = st.sidebar.multiselect(
    "Traveller Type",
    options=traveller_options,
    default=traveller_options,
)
```

#### 4e. Reviewer Country (geographic filter)
```python
country_options = sorted([x for x in df["author_country"].dropna().unique() if pd.notna(x)])
author_country = st.sidebar.multiselect(
    "Reviewer Country",
    options=country_options,
    default=country_options,
)
```

#### 4f. Choropleth Metric Radio (Phase 1 only — for the map)
```python
choropleth_metric = st.sidebar.radio(
    "Choropleth Color Metric",
    options=["Review Count", "Avg Overall Rating", "Recommendation Rate (%)"],
    help="Which metric to visualize on the map",
)
```

**Filter Encapsulation:** For Phase 1, it's fine to pass individual filter values to each chart function. For Phase 2+, consider bundling all filters into a single dict:
```python
filters = {
    "review_type": review_type_filter,
    "year_range": year_range,
    "cabin_flown": cabin_flown if review_types == ["airline"] or "All" in review_types else [],
    "type_traveller": type_traveller,
    "author_country": author_country,
}
```

---

### Step 5 — Centralized Filtering Function

This function encapsulates all global filter logic and is called before every chart aggregation. Create it once and reuse for all charts.

```python
def apply_global_filters(
    df: pd.DataFrame,
    review_type_list: list,
    year_range: tuple,
    cabin_flown_list: list,
    type_traveller_list: list,
    author_country_list: list,
) -> pd.DataFrame:
    """
    Apply all sidebar filters to the dataframe.
    Returns a filtered copy ready for aggregation into any chart.
    """
    filtered = df.copy()
    
    # Review type filter
    if review_type_list:
        filtered = filtered[filtered["review_type"].isin(review_type_list)]
    
    # Year range filter
    filtered = filtered[
        (filtered["review_year"] >= year_range[0]) &
        (filtered["review_year"] <= year_range[1])
    ]
    
    # Cabin flown filter (only applies to airline reviews)
    if cabin_flown_list and "airline" in review_type_list:
        filtered = filtered[filtered["cabin_flown"].isin(cabin_flown_list)]
    
    # Traveller type filter
    if type_traveller_list:
        filtered = filtered[filtered["type_traveller"].isin(type_traveller_list)]
    
    # Reviewer country filter
    if author_country_list:
        filtered = filtered[filtered["author_country"].isin(author_country_list)]
    
    return filtered
```

**Call this once after the sidebar:** `filtered_data = apply_global_filters(df, review_type_filter, year_range, cabin_flown, type_traveller, author_country)`

Then pass `filtered_data` to every chart function.

---

### Step 5b — Choropleth-Specific Aggregation

For the choropleth map specifically, aggregate the filtered data by country:

```python
def aggregate_for_choropleth(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare country-level aggregations for the choropleth map."""
    agg = filtered_df.groupby("author_country", as_index=False).agg(
        review_count=("author_country", "count"),
        avg_overall_rating=("overall_rating", "mean"),
        recommendation_rate=("recommended_int", "mean"),
    )
    agg["recommendation_rate"] = (agg["recommendation_rate"] * 100).round(1)
    agg["avg_overall_rating"] = agg["avg_overall_rating"].round(2)
    return agg

# After filtering
agg = aggregate_for_choropleth(filtered_data)

# Metric column mapping (for choropleth only)
METRIC_COL = {
    "Review Count":              "review_count",
    "Avg Overall Rating":        "avg_overall_rating",
    "Recommendation Rate (%)":   "recommendation_rate",
}
color_col = METRIC_COL[choropleth_metric]
```

---

### Step 6 — KPI Strip (Top Metrics Cards)

Display four key metrics in a horizontal row using `st.columns(4)`. These cards update whenever any filter changes.

```python
st.subheader("Dashboard Overview")
col1, col2, col3, col4 = st.columns(4)

# Metrics computed from filtered_data
total_reviews = len(filtered_data)
avg_rating = filtered_data["overall_rating"].mean()
pct_recommended = (filtered_data["recommended_int"].mean() * 100) if len(filtered_data) > 0 else 0
unique_airlines = filtered_data["entity_name"].nunique()  # or airlines/airports depending on review_type

with col1:
    st.metric("Total Reviews", f"{total_reviews:,}")
with col2:
    st.metric("Avg Overall Rating", f"{avg_rating:.2f}/10" if pd.notna(avg_rating) else "N/A")
with col3:
    st.metric("% Recommended", f"{pct_recommended:.1f}%")
with col4:
    st.metric("Entities Covered", f"{unique_airlines:,}")

st.divider()
```

These cards are pure derivatives of `filtered_data`, so they automatically update when filters change.

---

### Step 7 — Choropleth Map

```python
fig = px.choropleth(
    agg,
    locations="author_country",
    locationmode="country names",
    color=color_col,
    color_continuous_scale="Blues",
    labels={
        "review_count":          "Reviews",
        "avg_overall_rating":    "Avg Rating (1–10)",
        "recommendation_rate":   "Recommended (%)",
        "author_country":        "Country",
    },
    title=f"{selected_metric} by Reviewer Country",
    hover_name="author_country",
    hover_data={
        "review_count":        True,
        "avg_overall_rating":  True,
        "recommendation_rate": True,
        "author_country":      False,
    },
)
fig.update_layout(
    margin=dict(l=0, r=0, t=40, b=0),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type="natural earth",
    ),
)
st.plotly_chart(fig, use_container_width=True)
```

Key choices:
- `locationmode='country names'` — no ISO-3 lookup library needed
- `projection_type='natural earth'` — balanced appearance for global data
- `hover_data` includes all three metrics so users can inspect any country regardless of the active color metric

---

### Step 8 — Summary Stats Below Choropleth

Display the top-15 countries table to complement the map:

```python
st.subheader("Top 15 Reviewer Countries")
top15 = agg.nlargest(15, "review_count")[
    ["author_country", "review_count", "avg_overall_rating", "recommendation_rate"]
].rename(columns={
    "author_country":      "Country",
    "review_count":        "Reviews",
    "avg_overall_rating":  "Avg Rating",
    "recommendation_rate": "Recommended %",
})
st.dataframe(top15, hide_index=True, use_container_width=True)
```

---

## Complete `main.py` Structure (reading order)

```
1.  Imports: streamlit, pandas, plotly.express
2.  st.set_page_config(page_title="...", layout="wide")
3.  COUNTRY_NAME_MAP constant
4.  @st.cache_data def load_data() → DataFrame
5.  def apply_global_filters(...) → DataFrame
6.  def aggregate_for_choropleth(...) → DataFrame
7.  df = load_data()
8.  st.title() + st.caption() (brief description of the dashboard)
9.  ── Global Filters (Sidebar) ────────────────
    st.sidebar.header("Filters")
    review_types multiselect
    year_range slider
    cabin_flown multiselect
    type_traveller multiselect
    author_country multiselect
    choropleth_metric radio
10. ── Apply Global Filters ───────────────────
    filtered_data = apply_global_filters(...)
11. ── KPI Strip (4 metric cards) ─────────────
    st.columns(4) with st.metric() × 4
12. ── Choropleth Map ────────────────────────
    agg = aggregate_for_choropleth(filtered_data)
    fig = px.choropleth(...)
    st.plotly_chart(fig, use_container_width=True)
13. ── Summary Table ─────────────────────────
    st.dataframe(top15)
```

Estimated total for Phase 1: ~200 lines (including filter + KPI logic).

**Scaling note:** Phase 2 adds the 5 remaining charts (bar, line, heatmap, scatter, word cloud). Each will follow the pattern:
```
agg_data = filtered_data.groupby(...).agg(...)
fig = px.<chart_type>(...)
st.plotly_chart(fig)
```
They all consume the same `filtered_data`, so no filter duplication.

---

## Known Data Edge Cases

| Author Country in dataset | Issue | Resolution |
|---|---|---|
| `Russian Federation` | Plotly maps `"Russia"` | Normalize → `"Russia"` |
| `Trinidad & Tobago` | Ampersand vs. "and" | Normalize → `"Trinidad and Tobago"` |
| `Hong Kong` | Not a sovereign state on world maps | Map to `"China"` |
| `Netherlands Antilles` | Dissolved in 2010; absent from modern map data | Set to `None` — dropped |
| `Palestinian Territories` | Geopolitically ambiguous | Map to `"Palestine"` |
| `Macedonia` | Renamed in 2019 | Normalize → `"North Macedonia"` |
| `East Timor` | Formal name differs | Normalize → `"Timor-Leste"` |

Rows where `author_country` is `None` after normalization are excluded from both the map and the table.

---

## Future Charts (Phase 2+) — Filter Architecture

The global filter function you build in Phase 1 enables rapid chart additions in Phase 2. Here's how each future chart plugs in:

### Chart 1: Top/Bottom-N Entities (Horizontal Bar)
```python
# After filtering
entity_rating = filtered_data.groupby("entity_name").agg({
    "overall_rating": "mean",
    "author": "count"  # review count
}).reset_index()
entity_rating.columns = ["entity", "avg_rating", "reviews"]
entity_rating = entity_rating[entity_rating["reviews"] >= 10]  # min n reviews

fig = px.bar(
    entity_rating.nlargest(10, "avg_rating").append(
        entity_rating.nsmallest(10, "avg_rating")
    ),
    x="avg_rating", y="entity", color="reviews", orientation="h"
)
st.plotly_chart(fig, use_container_width=True)
```
Uses: `filtered_data` → no filter change needed.

### Chart 2: Rating Trend Over Time (Line)
```python
# Monthly trend, one line per review_type
trend = filtered_data.groupby(["review_year", "review_month", "review_type"]).agg({
    "overall_rating": "mean"
}).reset_index()
trend["date"] = pd.to_datetime(
    trend[["review_year", "review_month"]].assign(day=1)
)

fig = px.line(
    trend, x="date", y="overall_rating", color="review_type",
    markers=True, title="Rating Trends Over Time"
)
st.plotly_chart(fig, use_container_width=True)
```
Uses: `filtered_data` → no filter change needed.

### Chart 3: Heatmap of Sub-Ratings
**Important caveat:** Sub-rating dimensions differ by `review_type`. The heatmap is most meaningful for airline reviews (has seat_comfort, cabin_staff, food, IFE, value). 

```python
# If airline in review_types, use airline-specific sub-ratings
if "airline" in filtered_data["review_type"].unique():
    airline_data = filtered_data[filtered_data["review_type"] == "airline"]
    
    # Group by cabin_flown × sub-rating columns
    heatmap_data = airline_data.groupby("cabin_flown")[
        ["seat_comfort_rating", "cabin_staff_rating", "food_beverages_rating", 
         "inflight_entertainment_rating", "value_money_rating"]
    ].mean()
    
    fig = px.imshow(
        heatmap_data, color_continuous_scale="RdYlGn", 
        title="Airline Sub-Ratings by Cabin Class",
        labels={"index": "Cabin Class", "value": "Avg Rating (1-5)"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Heatmap is only available for airline reviews.")
```
Uses: `filtered_data` → filter by `review_type` server-side (optional: add heatmap filter toggle).

### Chart 4: Scatter — Overall vs Sub-Rating
```python
# Airlines only
airline_data = filtered_data[filtered_data["review_type"] == "airline"]

scatter_data = airline_data.dropna(subset=["overall_rating", "avg_sub_rating"])
fig = px.scatter(
    scatter_data,
    x="avg_sub_rating", y="overall_rating", color="recommended",
    hover_data=["airline_name", "title"],
    title="Overall Rating vs Sub-Rating Mean (Airline Reviews)"
)
st.plotly_chart(fig, use_container_width=True)
```
Uses: `filtered_data` → filters automatically.

### Chart 5: Word Cloud (Recommended Yes / No)
Requires `wordcloud` package (not in current requirements.txt).

```python
# Split content into two groups
recommended_yes = " ".join(
    filtered_data[filtered_data["recommended"] == True]["content"].dropna()
)
recommended_no = " ".join(
    filtered_data[filtered_data["recommended"] == False]["content"].dropna()
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Recommended ✓")
    # Generate word cloud for recommended_yes
with col2:
    st.subheader("Not Recommended ✗")
    # Generate word cloud for recommended_no
```
Uses: `filtered_data` → filters automatically.

---

## Design Decision: Category-Agnostic Sub-Ratings

**The tension:** Sub-rating dimensions differ across review types:
- **Airline:** seat_comfort, cabin_staff, food, IFE, value_money
- **Airport:** queuing, terminal_cleanliness, airport_shopping
- **Lounge:** comfort, cleanliness, bar_beverages, catering, washrooms, wifi, staff_service
- **Seat:** seat_legroom, seat_recline, seat_width, aisle_space

The heatmap and some analysis require type-specific columns. Options:

1. **Default to airline reviews** (recommended for MVP)
   - Make the dashboard a "Skytrax Airline Analytics" tool initially
   - Show message "Select airline reviews to view heatmap"
   - Expand to other categories in Phase 3

2. **Render different panels per category**
   - Complex but more complete
   - Requires category detection and conditional rendering

3. **Use only consolidated shared columns** (limited)
   - Lose the rich sub-rating insights
   - Fast but less analytical power

**Recommendation:** Start with **option 1**. Build a cohesive airline-focused dashboard in Phase 1, then expand to multi-category analysis in Phase 2+.

---

## Verification Checklist — Phase 1

After implementation, verify each of the following in order:

### Installation & Launch
1. `pip install -r requirements.txt` completes without errors (plotly installs cleanly)
2. `streamlit run main.py` opens in browser with no import errors
3. No red exception box appears on first load

### Sidebar Filters Exist
4. Sidebar renders with 6 filter controls: review_type, year_range, cabin_flown, type_traveller, author_country, choropleth_metric
5. All multiselect lists populate with correct unique values
6. Year slider spans 2004–2015 (or the actual min/max from the data)

### KPI Strip Works
7. 4 metric cards appear at the top: "Total Reviews", "Avg Overall Rating", "% Recommended", "Entities Covered"
8. KPI values are non-zero and sensible (e.g., Total Reviews ≈ 62,633 on first load)

### Choropleth Map Renders
9. World map appears with colored country fills
10. UK, US, Australia visibly darkest (highest review count on initial load)
11. Hovering over UK shows ~15,837 reviews in the tooltip

### Filter Reactivity — Global Filters
12. **Review Type filter:** Unselect "airline", map updates and KPI card shrinks (fewer reviews)
13. **Year range filter:** Change slider to 2014–2015 only, KPI total reviews drops significantly
14. **Cabin flown filter:** Only affects display if "airline" is in review_type selection
15. **Traveller type filter:** Reduces review count proportionally
16. **Reviewer country filter:** Selecting only "United Kingdom" shows ~15,837 reviews (all from UK reviewers)

### Choropleth Metric Toggle
17. Toggle metric radio from "Review Count" → "Avg Overall Rating" → "Recommendation Rate (%)"
18. Map color scale updates each time; tooltip shows the new metric

### Edge Cases & Data Quality
19. Hovering Russia, Trinidad & Tobago, South Korea — tooltips display correctly (not blank or error)
20. No crash when `author_country` is filtered to an empty set
21. Top-15 table refreshes when filters change

### Top-15 Table
22. Table shows correct order with UK at position 1 (or top selected country if geography filtered)
23. Table columns: Country, Reviews, Avg Rating, Recommended % — all formatted correctly
24. Avg Rating shows 2 decimals; Recommended % shows 1 decimal

### Overall Look & Feel
25. Layout is clean: KPI strip → Divider → Choropleth map → Table
26. Choropleth map renders full-width (use_container_width=True)
27. No layout shifts or excessive whitespace

**Phase 1 is complete when all 27 checks pass.**

---

## Summary: Phased Implementation

### Phase 1 (This Plan) — MVP Dashboard
**Scope:** Global filter plumbing + KPI strip + Choropleth map  
**Deliverable:** A working dashboard where every control in the sidebar cascades to the KPI cards and map  
**Estimated effort:** 200 lines of Python  
**Why this scope:** Establishes the filter architecture and verifies data flow before adding 5 more charts  
**Output:** `main.py` fully implemented, requirements.txt updated

### Phase 2 — 5 Analytical Charts
**Scope:** Add bar, line, heatmap, scatter, word cloud charts  
**Dependency:** Filters from Phase 1 already work; just call `apply_global_filters()` and aggregate  
**Effort per chart:** ~15–30 lines (copy the `filtered_data.groupby(...).agg(...); px.<chart>(...); st.plotly_chart(...)` pattern)  
**Effort for word cloud:** +1 import (`wordcloud`), +50 lines  
**Estimated total:** ~200 additional lines

### Phase 3 — Multi-Category Expansion
**Scope:** Handle sub-rating heatmaps for airport/lounge/seat categories (currently airline-only)  
**Dependency:** Conditional rendering per `review_type`; may refactor heatmap logic into a helper function

---

## Key Implementation Constraints

1. **Data is pre-cleaned:** `reviews_consolidated.csv` has nulls but is otherwise ready to aggregate. No extra scrubbing needed.
2. **Filter dependencies:** `cabin_flown` and sub-rating columns only exist for specific review types. The filter function checks this.
3. **Country name normalization is essential:** Plotly's `locationmode='country names'` expects exact matches. The COUNTRY_NAME_MAP dict handles ~12 edge cases.
4. **Sub-ratings differ by category:** Don't try to show a universal heatmap. Either default to airline or detect the user's selection and render conditionally.
5. **No pagination needed:** 62K rows is fine for `st.dataframe()` with lazy rendering; Streamlit handles this.

---

## Success Criteria

- ✅ All 27 verification checks pass
- ✅ KPI cards update instantly when any sidebar filter changes
- ✅ Choropleth map is interactive (click, zoom, hover)
- ✅ Top-15 table is sortable and stays in sync with filters
- ✅ No data crashes (null handling is transparent)
- ✅ Color palette is readable (Blues for the default metric)
