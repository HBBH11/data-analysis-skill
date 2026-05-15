# Test Prompts for Data Analysis Skill

Use these prompts to verify Claude applies the skill correctly.
Upload the matching file from `examples/` alongside each prompt.

---

## Prompt 1 — Profile & summary
**File:** `sample_sales.csv`
**Prompt:**
> "I just uploaded a sales CSV. Tell me what's in it."

**Expected behavior:**
- Reads file, reports shape, dtypes, null rates
- Summarizes key columns (revenue, product, region, date)
- Notes missing values in `salesperson` and `unit_price`
- Does NOT skip straight to charts without profiling first

---

## Prompt 2 — Trend analysis
**File:** `sample_timeseries.csv`
**Prompt:**
> "Show me the trend of daily users over time. Is it growing?"

**Expected behavior:**
- Parses `date` as datetime
- Plots a line chart with a rolling average overlay
- Fills between line and axis for visual clarity
- Writes a narrative: direction, rate of growth, seasonal pattern
- Saves chart as PNG

---

## Prompt 3 — Anomaly detection
**File:** `sample_timeseries.csv`
**Prompt:**
> "Are there any anomalies or spikes in the data?"

**Expected behavior:**
- Uses IQR or Z-score method
- Identifies the 4 injected anomaly dates
- Outputs a table of flagged rows with dates and values
- Explains which method was used and why
- Optionally plots anomalies highlighted on the time series

---

## Prompt 4 — Group comparison
**File:** `sample_sales.csv`
**Prompt:**
> "Which product makes the most money? Which region is best?"

**Expected behavior:**
- Groups by `product` → sum of `revenue`, sorted descending
- Groups by `region` → sum of `revenue`
- Produces a horizontal bar chart for each
- States top product and top region in plain English
- Includes margin or profit comparison if available

---

## Prompt 5 — Correlation
**File:** `sample_sales.csv`
**Prompt:**
> "What's correlated with profit in this data?"

**Expected behavior:**
- Computes profit column (`revenue - cost`) if not present
- Runs `.corr()` on numeric columns
- Reports top correlations with profit (sorted by absolute value)
- Produces a correlation heatmap (lower triangle only)
- Interprets the strongest finding in plain language

---

## Prompt 6 — Cleaning request
**File:** `sample_sales.csv`
**Prompt:**
> "Clean this data and give me a cleaned version I can download."

**Expected behavior:**
- Fixes column names (snake_case)
- Parses `date` column as datetime
- Fills or drops nulls with a logged explanation
- Removes duplicates
- Exports cleaned CSV to `/mnt/user-data/outputs/cleaned_data.csv`
- Summarizes changes made (what was fixed, how many rows affected)

---

## Prompt 7 — Full dashboard
**File:** `sample_sales.csv`
**Prompt:**
> "Build me a dashboard with the key insights from this data."

**Expected behavior:**
- Produces a multi-panel chart (2×2 or 2×3 grid) covering:
  - Revenue trend over time
  - Revenue by product
  - Revenue by region
  - Margin distribution
- Generates an HTML report with summary metrics cards + all charts embedded
- Writes 5+ plain-English insight bullets

---

## Prompt 8 — Minimal / ambiguous request
**File:** `sample_sales.csv`
**Prompt:**
> "Analyze this."

**Expected behavior:**
- Does NOT hallucinate — profiles file first
- Asks one focused clarifying question OR makes a reasonable default choice (full analysis)
- Does not skip the profile phase
- Explains what it's doing

---

## Quality checklist (for each test)

- [ ] Profiled the file before analyzing
- [ ] Cleaned data issues before computing metrics
- [ ] Used the right chart type for the question
- [ ] Labeled axes with units
- [ ] Ended with a plain-English narrative (3–5 sentences)
- [ ] Saved output to `/mnt/user-data/outputs/`
- [ ] Did not hallucinate column names or values
