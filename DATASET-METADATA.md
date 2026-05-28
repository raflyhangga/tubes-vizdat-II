# Skytrax Reviews Dataset — Cleaned Data Documentation

## Overview

This dataset originates from user reviews scraped from [Skytrax (airlinequality.com)](http://www.airlinequality.com) as of **August 2, 2015**. The raw data spans four review categories — airlines, airports, lounges, and seats.

A data preparation pipeline was applied to produce **6 output files**: four category-specific cleaned CSVs that retain all original detail columns, one consolidated long-format CSV that stacks all reviews into a single table with shared columns, and a Parquet copy of the consolidated file for faster downstream loading.

---

## Data Acquisition

### a. Dataset Source

The dataset was published on [Skytrax (www.airlinequality.com)](http://www.airlinequality.com), a UK-based consultancy firm and airline/airport review platform. Skytrax hosts user-submitted reviews covering airlines, airports, airport lounges, and aircraft seats. Reviews are publicly accessible to any visitor through a standard web browser without requiring authentication or account registration.

### b. How the Data Was Obtained

The data was collected via **web scraping** — an automated process that programmatically extracted review content from the Skytrax website. The scrape was performed on **August 2, 2015**, capturing all user reviews available on the platform up to that date. The extracted content was organized into four separate CSV files corresponding to the four review categories on the site (airline, airport, lounge, seat). The scraping methodology and resulting dataset were showcased in the following articles:

- [Exploring Reviews of Airline Services](http://www.quangn.com/exploring-reviews-of-airline-services/) — Quang Nguyen
- [What Are the Worst Airports in the World?](http://priceonomics.com/what-are-the-worst-airports-in-the-world/) — Priceonomics

### c. Licensing and Ethical Considerations

**Dataset license:** The dataset repository includes a **CC0 1.0 Universal (Public Domain Dedication)** license. Under CC0, the dataset creator has waived all copyright and related rights to the fullest extent permitted by law. This means the dataset may be freely used, modified, and redistributed for any purpose — including commercial use — without requiring attribution or permission.

**Original content license:** The CC0 license applies to the **dataset as a compiled work** (i.e., the structured CSV files published by the scraper's author). It does not necessarily reflect the licensing terms under which Skytrax originally published the individual reviews on its website. The license under which Skytrax makes its user reviews available is unknown.

**robots.txt compliance:** The Skytrax website's `robots.txt` file did not specifically prohibit the scraping of user review pages at the time the data was collected. This means the scraping did not violate the site's machine-readable access policy as it stood at that point.

**Ethical considerations to be aware of:**

- **User consent** — the reviews were voluntarily submitted by users to a public platform, and they are readable by anyone with a browser. However, the reviewers did not explicitly consent to their content being redistributed as a structured dataset.
- **Personal information** — the dataset contains author display names and self-reported countries of origin. While these are publicly visible on the Skytrax website, aggregating them into a downloadable dataset increases their exposure and potential for misuse.
- **Temporal context** — the `robots.txt` policy and Skytrax's terms of service may have changed since August 2015. Current compliance should not be assumed based on the conditions at the time of scraping.

---

## Output File Inventory

| File                           | Purpose                                                                   |
| ------------------------------ | ------------------------------------------------------------------------- |
| `airline_clean.csv`            | Full-detail airline reviews with all sub-ratings and route/cabin metadata |
| `airport_clean.csv`            | Full-detail airport reviews with terminal and service ratings             |
| `lounge_clean.csv`             | Full-detail lounge reviews with comfort, catering, and facility ratings   |
| `seat_clean.csv`               | Full-detail seat reviews with physical dimension and amenity ratings      |
| `reviews_consolidated.csv`     | All four categories stacked into one table using shared columns only      |
| `reviews_consolidated.parquet` | Binary copy of the consolidated CSV for faster read performance           |

> Row counts may be slightly lower than the raw data after duplicate removal.

---

## Cleaning Operations Applied

The following transformations were applied uniformly across all four datasets before export:

1. **Duplicate removal** — exact duplicate rows dropped.
2. **Date parsing** — `date` column converted from string to `datetime64`; auxiliary date columns (`date_visit`, `date_flown`) parsed where present.
3. **Type coercion** — all rating columns forced to numeric; `recommended` cast to boolean; low-cardinality text fields (`type_traveller`, `cabin_flown`, `lounge_type`) cast to categorical.
4. **Text normalization** — name/country columns stripped of leading/trailing whitespace and collapsed internal whitespace; `content` field stripped of residual HTML tags, HTML entities, and emoji-like characters.
5. **Rating clamping** — any rating value outside the valid `[1, 10]` range clamped to that range.
6. **Sparse column removal** — columns with more than 95% missing values dropped.
7. **Non-analytical column removal** — `link` column dropped from all datasets.
8. **Feature engineering** — new columns derived: `review_year`, `review_month`, `avg_sub_rating`, `review_word_count`, `recommended_int`, and normalized name keys for joins.

---

## File 1 — `airline_clean.csv`

Full-detail airline service reviews. Best used for airline-specific analysis: comparing carriers, analyzing cabin class differences, tracking service quality trends over time.

### Column Reference

| Column                          | Type     | Description                                                                                               |
| ------------------------------- | -------- | --------------------------------------------------------------------------------------------------------- |
| `airline_name`                  | string   | Name of the reviewed airline                                                                              |
| `title`                         | string   | Review headline written by the author                                                                     |
| `author`                        | string   | Reviewer's display name                                                                                   |
| `author_country`                | string   | Reviewer's self-reported country of origin (nullable)                                                     |
| `date`                          | datetime | Date the review was published on Skytrax                                                                  |
| `content`                       | string   | Full review text body (HTML-cleaned)                                                                      |
| `aircraft`                      | string   | Aircraft type flown, e.g., "Boeing 777" (sparse)                                                          |
| `type_traveller`                | category | Traveller type: Business, Couple Leisure, Family Leisure, Solo Leisure (sparse)                           |
| `cabin_flown`                   | category | Cabin class: Economy, Premium Economy, Business, First Class                                              |
| `route`                         | string   | Flight route, e.g., "London to New York" (sparse)                                                         |
| `overall_rating`                | float    | Author's overall score for the airline, scale 1–10                                                        |
| `seat_comfort_rating`           | float    | Seat comfort sub-rating, scale 1–5                                                                        |
| `cabin_staff_rating`            | float    | Cabin crew service sub-rating, scale 1–5                                                                  |
| `food_beverages_rating`         | float    | Food and drink quality sub-rating, scale 1–5                                                              |
| `inflight_entertainment_rating` | float    | IFE system sub-rating, scale 1–5                                                                          |
| `value_money_rating`            | float    | Value for money sub-rating, scale 1–5                                                                     |
| `recommended`                   | bool     | Whether the reviewer recommends the airline                                                               |
| `review_year`                   | int      | Year extracted from `date`                                                                                |
| `review_month`                  | int      | Month (1–12) extracted from `date`                                                                        |
| `avg_sub_rating`                | float    | Mean of the available sub-ratings for this review (seat comfort, cabin staff, food, IFE, value for money) |
| `review_word_count`             | int      | Number of words in the `content` field                                                                    |
| `recommended_int`               | int      | Integer encoding of `recommended` (1 = yes, 0 = no)                                                       |
| `airline_name_clean`            | string   | Lowercase, punctuation-stripped version of `airline_name` for joining across datasets                     |

> **Dropped during cleaning:** `link`, `ground_service_rating` (>95% missing), `wifi_connectivity_rating` (>95% missing).

---

## File 2 — `airport_clean.csv`

Full-detail airport facility reviews. Best used for comparing airports by region or size, analyzing terminal service quality, and identifying pain points in the passenger ground experience.

### Column Reference

| Column                        | Type     | Description                                                         |
| ----------------------------- | -------- | ------------------------------------------------------------------- |
| `airport_name`                | string   | Name of the reviewed airport                                        |
| `title`                       | string   | Review headline                                                     |
| `author`                      | string   | Reviewer's display name                                             |
| `author_country`              | string   | Reviewer's country (nullable)                                       |
| `date`                        | datetime | Review publication date                                             |
| `content`                     | string   | Full review text (HTML-cleaned)                                     |
| `experience_airport`          | string   | Type of airport experience reviewed (sparse)                        |
| `date_visit`                  | datetime | Date the reviewer visited the airport (sparse)                      |
| `type_traveller`              | category | Traveller type (sparse)                                             |
| `overall_rating`              | float    | Overall airport score, scale 1–10                                   |
| `queuing_rating`              | float    | Queue/wait time sub-rating, scale 1–5                               |
| `terminal_cleanliness_rating` | float    | Terminal cleanliness sub-rating, scale 1–5                          |
| `terminal_seating_rating`     | float    | Terminal seating comfort sub-rating, scale 1–5 (sparse)             |
| `food_beverages_rating`       | float    | Airport food/drink sub-rating, scale 1–5 (sparse)                   |
| `airport_shopping_rating`     | float    | Shopping facilities sub-rating, scale 1–5                           |
| `wifi_connectivity_rating`    | float    | Wi-Fi quality sub-rating, scale 1–5 (sparse)                        |
| `recommended`                 | bool     | Whether the reviewer recommends the airport                         |
| `review_year`                 | int      | Year extracted from `date`                                          |
| `review_month`                | int      | Month extracted from `date`                                         |
| `avg_sub_rating`              | float    | Mean of queuing, terminal cleanliness, and airport shopping ratings |
| `review_word_count`           | int      | Word count of `content`                                             |
| `recommended_int`             | int      | Integer encoding of `recommended`                                   |
| `airport_name_clean`          | string   | Normalized airport name for joins                                   |

> **Dropped during cleaning:** `link`, `terminal_signs_rating` (>95% missing), `airport_staff_rating` (>95% missing).

---

## File 3 — `lounge_clean.csv`

Full-detail airport lounge reviews. Best used for comparing lounge quality by airline or airport, analyzing the impact of lounge type (pay-in vs. airline-operated), and benchmarking facility standards.

### Column Reference

| Column                     | Type     | Description                                                   |
| -------------------------- | -------- | ------------------------------------------------------------- |
| `airline_name`             | string   | Airline operating or associated with the lounge               |
| `title`                    | string   | Review headline                                               |
| `author`                   | string   | Reviewer's display name                                       |
| `author_country`           | string   | Reviewer's country (nullable)                                 |
| `date`                     | datetime | Review publication date                                       |
| `content`                  | string   | Full review text (HTML-cleaned)                               |
| `lounge_name`              | string   | Name of the specific lounge                                   |
| `airport`                  | string   | Airport where the lounge is located                           |
| `lounge_type`              | category | Type of lounge access: e.g., Airline, Independent, Pay-in     |
| `date_visit`               | datetime | Date the reviewer visited the lounge (sparse)                 |
| `type_traveller`           | category | Traveller type (sparse)                                       |
| `overall_rating`           | float    | Overall lounge score, scale 1–10                              |
| `comfort_rating`           | int      | Seating/space comfort rating, scale 1–5                       |
| `cleanliness_rating`       | int      | Cleanliness rating, scale 1–5                                 |
| `bar_beverages_rating`     | float    | Bar and drinks quality, scale 1–5                             |
| `catering_rating`          | float    | Food/catering quality, scale 1–5                              |
| `washrooms_rating`         | float    | Washroom quality, scale 1–5                                   |
| `wifi_connectivity_rating` | float    | Wi-Fi quality, scale 1–5                                      |
| `staff_service_rating`     | float    | Staff service quality, scale 1–5                              |
| `recommended`              | bool     | Whether the reviewer recommends the lounge                    |
| `review_year`              | int      | Year extracted from `date`                                    |
| `review_month`             | int      | Month extracted from `date`                                   |
| `avg_sub_rating`           | float    | Mean of all seven sub-ratings (comfort through staff service) |
| `review_word_count`        | int      | Word count of `content`                                       |
| `recommended_int`          | int      | Integer encoding of `recommended`                             |
| `airline_name_clean`       | string   | Normalized airline name for joins                             |

> **Dropped during cleaning:** `link`. No columns exceeded the 95% sparsity threshold in this dataset.

---

## File 4 — `seat_clean.csv`

Full-detail aircraft seat reviews. Best used for comparing physical seat quality across airlines and cabin classes, analyzing the relationship between seat dimensions and satisfaction, and identifying aircraft-specific comfort patterns.

### Column Reference

| Column                | Type     | Description                                              |
| --------------------- | -------- | -------------------------------------------------------- |
| `airline_name`        | string   | Airline operating the aircraft                           |
| `title`               | string   | Review headline                                          |
| `author`              | string   | Reviewer's display name                                  |
| `author_country`      | string   | Reviewer's country                                       |
| `date`                | datetime | Review publication date                                  |
| `content`             | string   | Full review text (HTML-cleaned)                          |
| `aircraft`            | string   | Aircraft type, e.g., "Airbus A380"                       |
| `seat_layout`         | string   | Seat configuration, e.g., "3-4-3"                        |
| `date_flown`          | datetime | Date the flight was taken (sparse)                       |
| `cabin_flown`         | category | Cabin class (Economy, Business, etc.)                    |
| `type_traveller`      | category | Traveller type (sparse)                                  |
| `overall_rating`      | float    | Overall seat score, scale 1–10                           |
| `seat_legroom_rating` | int      | Legroom rating, scale 1–5                                |
| `seat_recline_rating` | int      | Recline rating, scale 1–5                                |
| `seat_width_rating`   | int      | Seat width rating, scale 1–5                             |
| `aisle_space_rating`  | int      | Aisle space rating, scale 1–5                            |
| `viewing_tv_rating`   | float    | In-seat screen visibility rating, scale 1–5              |
| `seat_storage_rating` | float    | Personal storage space rating, scale 1–5 (sparse)        |
| `recommended`         | bool     | Whether the reviewer recommends the seat                 |
| `review_year`         | int      | Year extracted from `date`                               |
| `review_month`        | int      | Month extracted from `date`                              |
| `avg_sub_rating`      | float    | Mean of legroom, recline, width, and aisle space ratings |
| `review_word_count`   | int      | Word count of `content`                                  |
| `recommended_int`     | int      | Integer encoding of `recommended`                        |
| `airline_name_clean`  | string   | Normalized airline name for joins                        |

> **Dropped during cleaning:** `link`, `power_supply_rating` (>95% missing).

---

## File 5 — `reviews_consolidated.csv` / `.parquet`

A single long-format table that vertically stacks all four review categories using only their shared columns. Best used for cross-category comparisons (e.g., "do airports or airlines get rated more harshly?"), global trend analysis over time, geographic reviewer distribution, and any visualization that needs the full corpus in one table.

### Column Reference

| Column              | Type     | Description                                                                                           |
| ------------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| `review_type`       | string   | Source category: `"airline"`, `"airport"`, `"lounge"`, or `"seat"`                                    |
| `entity_name`       | string   | The reviewed entity — airline name, airport name, or lounge name depending on `review_type`           |
| `author`            | string   | Reviewer's display name                                                                               |
| `author_country`    | string   | Reviewer's country (nullable)                                                                         |
| `date`              | datetime | Review publication date                                                                               |
| `content`           | string   | Full review text (HTML-cleaned)                                                                       |
| `title`             | string   | Review headline                                                                                       |
| `overall_rating`    | float    | Overall score on a 1–10 scale (nullable)                                                              |
| `recommended`       | bool     | Whether the reviewer recommends the entity                                                            |
| `recommended_int`   | int      | Integer encoding: 1 = recommended, 0 = not recommended                                                |
| `review_year`       | int      | Year extracted from `date`                                                                            |
| `review_month`      | int      | Month (1–12) extracted from `date`                                                                    |
| `avg_sub_rating`    | float    | Mean of category-specific sub-ratings for this review (nullable; composition varies by `review_type`) |
| `review_word_count` | int      | Number of words in `content`                                                                          |

### What `avg_sub_rating` Means Per Category

Because each review type has different sub-rating dimensions, the `avg_sub_rating` column is computed from different source columns depending on the value of `review_type`:

| review_type | Sub-ratings averaged                                                                       |
| ----------- | ------------------------------------------------------------------------------------------ |
| `airline`   | seat_comfort, cabin_staff, food_beverages, inflight_entertainment, value_money             |
| `airport`   | queuing, terminal_cleanliness, airport_shopping                                            |
| `lounge`    | comfort, cleanliness, bar_beverages, catering, washrooms, wifi_connectivity, staff_service |
| `seat`      | seat_legroom, seat_recline, seat_width, aisle_space                                        |

> This column is useful for within-category comparisons but should be interpreted with care when comparing across categories, since the underlying dimensions differ.

---

## Engineered Columns Summary

These columns do not exist in the raw data and were created during the transformation step:

| Column               | Present In            | How It Was Created                                                               |
| -------------------- | --------------------- | -------------------------------------------------------------------------------- |
| `review_year`        | all files             | Extracted from `date` using `.dt.year`                                           |
| `review_month`       | all files             | Extracted from `date` using `.dt.month`                                          |
| `avg_sub_rating`     | all files             | Row-wise mean of available sub-rating columns (NaN-tolerant)                     |
| `review_word_count`  | all files             | Word count of the `content` field via whitespace split                           |
| `recommended_int`    | all files             | Integer cast of `recommended` boolean (1 = yes, 0 = no)                          |
| `airline_name_clean` | airline, lounge, seat | Lowercased, punctuation-stripped `airline_name` for cross-file joins             |
| `airport_name_clean` | airport               | Lowercased, punctuation-stripped `airport_name` for cross-file joins             |
| `review_type`        | consolidated only     | Label identifying the source dataset                                             |
| `entity_name`        | consolidated only     | Unified name column mapped from `airline_name`, `airport_name`, or `lounge_name` |

---

## Usage Guidance

**For category-specific deep dives**, use the individual cleaned CSVs. They retain all sub-rating columns and category-specific metadata (e.g., `route` and `cabin_flown` for airlines, `seat_layout` and `aircraft` for seats) that are not present in the consolidated file.

**For cross-category or corpus-wide analysis**, use `reviews_consolidated.csv` (or the `.parquet` variant). Filter on `review_type` to isolate categories as needed.

**For joining datasets**, use the `*_name_clean` columns as join keys. For example, to combine airline review ratings with seat review ratings for the same carrier, join `airline_clean.csv` and `seat_clean.csv` on `airline_name_clean`.

---

## Known Limitations

1. **Temporal coverage** — data was scraped on a single date (August 2, 2015), so all reviews predate mid-2015. No updates after that date are included.
2. **Sparse columns** — several columns have very low fill rates even after cleaning (e.g., `aircraft` in airline, `type_traveller` across multiple files). Analysis on these columns will have limited statistical power.
3. **Rating scale inconsistency** — `overall_rating` uses a 1–10 scale while sub-ratings use 1–5. The `avg_sub_rating` column is on the 1–5 scale. Normalize before combining with `overall_rating`.
4. **Self-reported data** — `author_country` is self-reported and unvalidated. Country names may have minor inconsistencies even after text cleaning.
5. **Recommendation bias** — the `recommended` field is binary and was present for all reviews, but the strength of recommendation is not captured.