---
name: data-analysis
description: "Use this skill whenever the user wants to analyze, explore, summarize, visualize, or extract insights from data — regardless of format. Triggers include: uploading a CSV, Excel, JSON, or any tabular file and asking what it contains, what trends exist, what's unusual, or how to visualize it. Also triggers for: 'analyze my data', 'show me a chart of', 'find patterns in', 'summarize this dataset', 'what does this data tell me', 'clean this data', 'compare these numbers', 'what's the correlation between', 'build me a dashboard', 'detect anomalies', or any request where the primary deliverable is insight, a chart, a report, or a cleaned dataset. Do NOT use for pure spreadsheet creation (use xlsx skill), document generation (use docx), or PDF work (use pdf). Use alongside xlsx if the deliverable is both an analyzed chart AND an editable spreadsheet."
license: MIT
---

# Data Analysis & Visualization Skill

## Purpose
Turn raw data — CSV, Excel, JSON, SQL dumps, or plain numbers — into clear insights, charts, and reports that people can actually use and understand. The goal is always: **make the data tell its story**.

---

## Phase 1 — Understand Before You Touch

Before writing any code or producing any output, always:

1. **Profile the file first** — never assume the structure. Read a sample, check column names, dtypes, row count, and null rates.
2. **Identify what the user actually needs** — is it a chart? A summary? Anomaly detection? A cleaned file? A full report? If unclear, ask one focused question.
3. **Understand the domain** — sales data, trading data, health records, and web analytics each have different meaningful questions. Let the domain guide what's worth highlighting.

```python
import pandas as pd
import numpy as np

# Always start with a profile
df = pd.read_csv('/mnt/user-data/uploads/file.csv')

print(f"Shape: {df.shape}")
print(f"\nColumns:\n{df.dtypes}")
print(f"\nNull rates:\n{df.isnull().mean().round(3)}")
print(f"\nSample:\n{df.head()}")
print(f"\nNumerics:\n{df.describe()}")
```

For Excel files with multiple sheets:
```python
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
for name, sheet in all_sheets.items():
    print(f"\n--- {name} ({sheet.shape}) ---")
    print(sheet.head(3))
```

For JSON:
```python
import json
with open('file.json') as f:
    data = json.load(f)

# If it's a list of records
df = pd.json_normalize(data)
```

---

## Phase 2 — Clean Before You Analyze

**Never analyze dirty data.** Bad data = misleading insights.

### Checklist before analysis

```python
# 1. Fix column names — strip spaces, lowercase, snake_case
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^\w]', '', regex=True)

# 2. Parse dates correctly
date_cols = df.select_dtypes(include='object').columns
for col in date_cols:
    try:
        df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
    except:
        pass

# 3. Handle nulls — document the strategy, never silently drop
null_counts = df.isnull().sum()
print("Nulls:\n", null_counts[null_counts > 0])
# Options: df.dropna(), df.fillna(0), df.fillna(df.mean()), forward-fill for time series

# 4. Fix numeric columns stored as strings
for col in df.select_dtypes('object').columns:
    cleaned = df[col].str.replace(r'[,$%]', '', regex=True)
    try:
        df[col] = pd.to_numeric(cleaned)
    except:
        pass

# 5. Detect and flag (not silently remove) outliers
for col in df.select_dtypes(include=np.number).columns:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    outliers = df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)]
    if len(outliers) > 0:
        print(f"{col}: {len(outliers)} outliers (IQR method)")

# 6. Remove exact duplicates
dupes = df.duplicated().sum()
if dupes > 0:
    print(f"Found {dupes} duplicate rows")
    df = df.drop_duplicates()
```

---

## Phase 3 — Analysis Patterns by Question Type

Match the user's question to the right analysis pattern.

### "What's in this data?" → Profile report
```python
def profile_report(df):
    report = []
    for col in df.columns:
        info = {
            'column': col,
            'dtype': str(df[col].dtype),
            'null_pct': round(df[col].isnull().mean() * 100, 1),
            'unique': df[col].nunique(),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            info.update({
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': round(df[col].mean(), 2),
                'median': df[col].median(),
            })
        else:
            info['top_values'] = df[col].value_counts().head(3).to_dict()
        report.append(info)
    return pd.DataFrame(report)
```

### "What's the trend?" → Time series analysis
```python
# Ensure datetime index
df = df.sort_values('date_col')
df = df.set_index('date_col')

# Resample by period
daily   = df['value'].resample('D').sum()
weekly  = df['value'].resample('W').sum()
monthly = df['value'].resample('ME').sum()

# Rolling average (smoothed trend)
df['rolling_7d'] = df['value'].rolling(7).mean()
df['rolling_30d'] = df['value'].rolling(30).mean()

# Growth rate
df['mom_growth'] = df['value'].pct_change() * 100
```

### "What's unusual?" → Anomaly detection
```python
# Z-score method (> 3 std devs from mean)
from scipy import stats
z_scores = np.abs(stats.zscore(df[numeric_col].dropna()))
anomalies = df[z_scores > 3]

# IQR method (more robust to skewed data)
Q1 = df[col].quantile(0.25)
Q3 = df[col].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]

# For time series: detect sudden spikes
df['change_pct'] = df['value'].pct_change().abs() * 100
spikes = df[df['change_pct'] > 50]  # adjust threshold as needed
```

### "What's the correlation?" → Relationship analysis
```python
# Correlation matrix
corr = df.select_dtypes(include=np.number).corr()

# Top correlations with a target variable
target = 'revenue'
top_corr = corr[target].drop(target).sort_values(key=abs, ascending=False)
print("Top correlations with", target)
print(top_corr.head(10))

# Scatter with regression line
from scipy.stats import pearsonr
r, p = pearsonr(df['x'].dropna(), df['y'].dropna())
print(f"r = {r:.3f}, p = {p:.4f}")
```

### "How are groups different?" → Aggregation and comparison
```python
# Group stats
summary = df.groupby('category')['metric'].agg(['mean', 'median', 'std', 'count'])
summary = summary.sort_values('mean', ascending=False)

# Share / contribution
summary['share_pct'] = (summary['mean'] / summary['mean'].sum() * 100).round(1)

# Top N
top5 = df.groupby('product')['revenue'].sum().nlargest(5)
```

### "How does X rank?" → Rankings and leaderboards
```python
df['rank'] = df['metric'].rank(ascending=False, method='dense').astype(int)
df['percentile'] = df['metric'].rank(pct=True).round(3) * 100
df_ranked = df.sort_values('metric', ascending=False)
```

---

## Phase 4 — Visualization

**Always use matplotlib + seaborn.** Install if needed: `pip install matplotlib seaborn --break-system-packages`

### Chart type selection guide

| User question | Chart type |
|---|---|
| Trend over time | Line chart |
| Compare categories | Bar chart (horizontal if many labels) |
| Distribution of values | Histogram + KDE |
| Relationship between 2 vars | Scatter plot |
| Correlation matrix | Heatmap |
| Part-of-whole (< 6 parts) | Pie or donut |
| Part-of-whole (> 6 parts) | Treemap or stacked bar |
| Distribution across groups | Box plot or violin |
| Many metrics at once | Dashboard (multi-panel) |

### Standard setup — use this for every chart
```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# Professional theme
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#F8F8F8',
    'axes.grid': True,
    'grid.color': 'white',
    'grid.linewidth': 1.2,
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
})

# Color palette (colorblind-friendly)
COLORS = ['#2563EB', '#16A34A', '#DC2626', '#D97706', '#7C3AED', '#0891B2']
```

### Line chart (trends)
```python
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(df.index, df['value'], color=COLORS[0], linewidth=2, label='Actual')
ax.plot(df.index, df['rolling_30d'], color=COLORS[1], linewidth=1.5,
        linestyle='--', label='30-day average')

ax.fill_between(df.index, df['value'], alpha=0.1, color=COLORS[0])

ax.set_title('Revenue over Time', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('')
ax.set_ylabel('Revenue ($)', fontsize=11)
ax.legend(frameon=False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/chart.png', dpi=150, bbox_inches='tight')
plt.close()
```

### Bar chart (comparisons)
```python
fig, ax = plt.subplots(figsize=(10, 6))

# Horizontal bars work better for many categories with long labels
bars = ax.barh(categories, values, color=COLORS[0], height=0.6)

# Add value labels on bars
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + max(values)*0.01, bar.get_y() + bar.get_height()/2,
            f'{val:,.0f}', va='center', fontsize=10)

ax.set_title('Sales by Category', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Sales', fontsize=11)
ax.invert_yaxis()  # Largest at top

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/chart.png', dpi=150, bbox_inches='tight')
plt.close()
```

### Histogram with KDE (distribution)
```python
fig, ax = plt.subplots(figsize=(10, 5))

ax.hist(df['value'].dropna(), bins=30, color=COLORS[0], alpha=0.7,
        edgecolor='white', linewidth=0.5, density=True)

df['value'].dropna().plot.kde(ax=ax, color=COLORS[1], linewidth=2)

ax.axvline(df['value'].mean(), color='red', linestyle='--',
           linewidth=1.5, label=f"Mean: {df['value'].mean():.1f}")
ax.axvline(df['value'].median(), color='orange', linestyle='--',
           linewidth=1.5, label=f"Median: {df['value'].median():.1f}")

ax.set_title('Distribution of Values', fontsize=14, fontweight='bold', pad=12)
ax.legend(frameon=False)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/chart.png', dpi=150, bbox_inches='tight')
plt.close()
```

### Correlation heatmap
```python
corr = df.select_dtypes(include=np.number).corr()

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))  # upper triangle

sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=-1, vmax=1, center=0, square=True, ax=ax,
            cbar_kws={'shrink': 0.8})

ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
```

### Multi-panel dashboard
```python
fig = plt.figure(figsize=(16, 10))
fig.suptitle('Data Dashboard', fontsize=16, fontweight='bold', y=1.01)

# 2x2 grid
ax1 = fig.add_subplot(2, 2, 1)  # Top left: trend
ax2 = fig.add_subplot(2, 2, 2)  # Top right: distribution
ax3 = fig.add_subplot(2, 2, 3)  # Bottom left: bar
ax4 = fig.add_subplot(2, 2, 4)  # Bottom right: scatter

# ... populate each ax ...

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/dashboard.png', dpi=150, bbox_inches='tight')
plt.close()
```

---

## Phase 5 — Narrative Report (HTML)

When the user wants a full report — not just a chart — generate a self-contained HTML file.

```python
def generate_html_report(title, summary_stats, insights, chart_paths):
    """
    summary_stats: dict of key metric names → values
    insights: list of plain-language strings (the story)
    chart_paths: list of PNG file paths to embed as base64
    """
    import base64

    def img_to_base64(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()

    charts_html = ''.join([
        f'<img src="data:image/png;base64,{img_to_base64(p)}" '
        f'style="width:100%;border-radius:8px;margin-bottom:1.5rem;" />'
        for p in chart_paths
    ])

    stats_html = ''.join([
        f'<div class="metric"><div class="val">{v}</div><div class="lbl">{k}</div></div>'
        for k, v in summary_stats.items()
    ])

    bullets_html = ''.join([f'<li>{i}</li>' for i in insights])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #F9FAFB; color: #111827; padding: 2rem; }}
  .container {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem; }}
  .subtitle {{ color: #6B7280; font-size: 0.9rem; margin-bottom: 2rem; }}
  .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
              gap: 1rem; margin-bottom: 2rem; }}
  .metric {{ background: white; border: 1px solid #E5E7EB; border-radius: 10px;
             padding: 1rem 1.25rem; text-align: center; }}
  .val {{ font-size: 1.5rem; font-weight: 700; color: #1D4ED8; }}
  .lbl {{ font-size: 0.75rem; color: #6B7280; margin-top: 4px; text-transform: uppercase;
          letter-spacing: 0.05em; }}
  .section {{ background: white; border: 1px solid #E5E7EB; border-radius: 10px;
              padding: 1.5rem; margin-bottom: 1.5rem; }}
  .section h2 {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;
                 padding-bottom: 0.5rem; border-bottom: 1px solid #F3F4F6; }}
  ul {{ padding-left: 1.25rem; }}
  li {{ margin-bottom: 0.5rem; line-height: 1.6; color: #374151; }}
  .footer {{ text-align: center; font-size: 0.8rem; color: #9CA3AF; margin-top: 2rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>{title}</h1>
  <p class="subtitle">Generated by Claude Data Analysis</p>

  <div class="metrics">{stats_html}</div>

  <div class="section">
    <h2>Key Insights</h2>
    <ul>{bullets_html}</ul>
  </div>

  <div class="section">
    <h2>Charts</h2>
    {charts_html}
  </div>

  <p class="footer">Report generated on {pd.Timestamp.now().strftime('%B %d, %Y')}</p>
</div>
</body>
</html>"""

    output_path = '/mnt/user-data/outputs/report.html'
    with open(output_path, 'w') as f:
        f.write(html)
    return output_path
```

---

## Phase 6 — Output Strategy

### What to deliver based on what was asked

| Request | Primary output | Secondary |
|---|---|---|
| "Analyze this CSV" | Summary in chat + 1–2 charts | Offer full report |
| "Show me a chart" | PNG chart file | Brief narrative |
| "Build a dashboard" | Multi-panel PNG or HTML report | Key metrics callout |
| "Clean this data" | Cleaned CSV/Excel file | Log of changes made |
| "What's the trend?" | Line chart + written insight | — |
| "Find anomalies" | Table of flagged rows + chart | Explanation of method |
| "Full report" | HTML report with all charts embedded | — |

### Always end your analysis with a narrative

Don't just dump numbers. After every analysis, write 3–5 plain-English sentences that:
1. State the most important finding first
2. Quantify the finding (with numbers, %, dates)
3. Note anything unusual or worth attention
4. Suggest one actionable next step if relevant

Example:
> "Revenue grew 34% year-over-year, driven almost entirely by Q4 (which contributed 58% of annual total). The top 3 customers account for 71% of revenue — a concentration risk worth monitoring. March and August show consistent dips across all 3 years, suggesting seasonality. Consider a promotional push in those months."

---

## Common Pitfalls — Avoid These

### Data issues
- **Never analyze without profiling first** — unknown nulls, wrong dtypes, and hidden duplicates invalidate results
- **Date columns often come as strings** — always parse with `pd.to_datetime()` before time-series analysis
- **Mixed-type columns** — a "revenue" column with "$1,200" strings will silently become NaN; always clean before numeric operations
- **Timezone-naive vs timezone-aware** — mixing these causes merge failures; standardize with `.dt.tz_localize()` or `.dt.tz_convert()`

### Analysis issues
- **Don't confuse correlation with causation** — state correlations as "associated with" not "causes"
- **Mean vs median** — for skewed data (income, prices), median tells a truer story; always show both
- **Small sample sizes** — flag when N < 30; avoid strong statistical claims
- **Survivorship bias** — if the data only shows active/successful records, say so

### Chart issues
- **Always label axes** — a chart with no axis labels is useless
- **Always include units** — "$", "%", "days", "users" etc.
- **Never use pie charts with > 6 slices** — use a bar chart instead
- **Color accessibility** — avoid red+green only; use the COLORS palette defined above which is colorblind-safe
- **Save at 150 dpi minimum** for clear output

---

## Quick Reference: Library Imports

```python
# Core
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# Statistics
from scipy import stats
from scipy.stats import pearsonr, spearmanr, ttest_ind

# Optional but useful
from datetime import datetime, timedelta
import json, os, re, warnings
warnings.filterwarnings('ignore')
```

Install anything missing:
```bash
pip install pandas numpy matplotlib seaborn scipy --break-system-packages
```

---

## Workflow Summary

```
1. Profile  →  understand structure, dtypes, nulls, shape
2. Clean    →  fix dtypes, handle nulls, flag outliers, drop dupes
3. Analyze  →  match user's question to the right analysis pattern
4. Visualize → pick the right chart type, apply standard theme
5. Narrate  →  write 3–5 plain-English sentences about findings
6. Deliver  →  chart PNG, cleaned file, or full HTML report
```

Every output should make the data tell its story — not just show the numbers.
