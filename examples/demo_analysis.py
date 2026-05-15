"""
demo_analysis.py
----------------
Demonstrates the full data analysis pipeline from the skill:
  1. Profile
  2. Clean
  3. Analyze
  4. Visualize
  5. Export HTML report

Run: python demo_analysis.py
Outputs to: outputs/ folder
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')

# ── Output directory ──────────────────────────────────────────────────────────
os.makedirs('outputs', exist_ok=True)

# ── Color palette (colorblind-safe) ───────────────────────────────────────────
COLORS = ['#2563EB', '#16A34A', '#DC2626', '#D97706', '#7C3AED', '#0891B2']

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

chart_paths = []


# ── PHASE 1: PROFILE ─────────────────────────────────────────────────────────
print("=" * 60)
print("PHASE 1 — PROFILE")
print("=" * 60)

df = pd.read_csv('examples/sample_sales.csv')

print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"\nColumn types:\n{df.dtypes.to_string()}")
print(f"\nNull rates:")
null_rates = (df.isnull().mean() * 100).round(1)
print(null_rates[null_rates > 0].to_string())
print(f"\nSample (3 rows):\n{df.head(3).to_string()}")


# ── PHASE 2: CLEAN ───────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 2 — CLEAN")
print("=" * 60)

# Standardize column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Parse dates
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.to_period('M')
df['quarter'] = df['date'].dt.to_period('Q')

# Fill missing unit_price with product median
df['unit_price'] = df.groupby('product')['unit_price'].transform(
    lambda x: x.fillna(x.median())
)

# Drop rows where salesperson is unknown (only 5 rows)
before = len(df)
df = df.dropna(subset=['salesperson'])
print(f"Dropped {before - len(df)} rows with missing salesperson")

# Flag outliers in revenue (IQR method)
q1, q3 = df['revenue'].quantile([0.25, 0.75])
iqr = q3 - q1
outlier_mask = (df['revenue'] < q1 - 1.5 * iqr) | (df['revenue'] > q3 + 1.5 * iqr)
print(f"Revenue outliers flagged: {outlier_mask.sum()}")

# Remove exact duplicates
dupes = df.duplicated().sum()
print(f"Duplicate rows: {dupes}")

print(f"\nClean shape: {df.shape}")


# ── PHASE 3: ANALYZE ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 3 — ANALYZE")
print("=" * 60)

# Profit
df['profit'] = df['revenue'] - df['cost']
df['margin_pct'] = (df['profit'] / df['revenue'] * 100).round(1)

# Key metrics
total_revenue = df['revenue'].sum()
total_profit = df['profit'].sum()
avg_margin = df['margin_pct'].mean()
return_rate = df['returned'].mean() * 100

print(f"Total revenue:  ${total_revenue:,.0f}")
print(f"Total profit:   ${total_profit:,.0f}")
print(f"Avg margin:     {avg_margin:.1f}%")
print(f"Return rate:    {return_rate:.1f}%")

# Revenue by product
by_product = df.groupby('product')['revenue'].sum().sort_values(ascending=False)
print(f"\nRevenue by product:\n{by_product.to_string()}")

# Revenue by region
by_region = df.groupby('region')['revenue'].sum().sort_values(ascending=False)
print(f"\nRevenue by region:\n{by_region.to_string()}")

# Monthly trend
monthly = df.groupby('month')['revenue'].sum().reset_index()
monthly['month_str'] = monthly['month'].astype(str)

# Top salesperson
top_sales = df.groupby('salesperson')['revenue'].sum().sort_values(ascending=False)
print(f"\nTop salesperson: {top_sales.index[0]} (${top_sales.iloc[0]:,.0f})")

# Correlation
corr_cols = ['quantity', 'unit_price', 'revenue', 'cost', 'profit', 'margin_pct']
corr = df[corr_cols].corr()
print(f"\nCorrelation with profit:")
print(corr['profit'].drop('profit').sort_values(key=abs, ascending=False).round(3).to_string())


# ── PHASE 4: VISUALIZE ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 4 — VISUALIZE")
print("=" * 60)

# Chart 1: Revenue by product (horizontal bar)
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(by_product.index, by_product.values, color=COLORS[0], height=0.55)
for bar, val in zip(bars, by_product.values):
    ax.text(bar.get_width() + by_product.max() * 0.01, bar.get_y() + bar.get_height() / 2,
            f'${val:,.0f}', va='center', fontsize=10)
ax.set_title('Revenue by Product', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Revenue ($)')
ax.invert_yaxis()
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
plt.tight_layout()
path = 'outputs/chart_revenue_by_product.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
plt.close()
chart_paths.append(path)
print(f"Saved: {path}")

# Chart 2: Monthly revenue trend
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(range(len(monthly)), monthly['revenue'], color=COLORS[0], linewidth=2.5, marker='o',
        markersize=5, markerfacecolor='white', markeredgewidth=2)
ax.fill_between(range(len(monthly)), monthly['revenue'], alpha=0.12, color=COLORS[0])
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly['month_str'], rotation=45, ha='right', fontsize=9)
ax.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Revenue ($)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
plt.tight_layout()
path = 'outputs/chart_monthly_trend.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
plt.close()
chart_paths.append(path)
print(f"Saved: {path}")

# Chart 3: Revenue by region (pie-style donut)
fig, ax = plt.subplots(figsize=(7, 6))
wedges, texts, autotexts = ax.pie(
    by_region.values, labels=by_region.index,
    colors=COLORS[:len(by_region)],
    autopct='%1.1f%%', startangle=90,
    wedgeprops={'width': 0.55, 'edgecolor': 'white', 'linewidth': 2}
)
for at in autotexts:
    at.set_fontsize(10)
ax.set_title('Revenue Split by Region', fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
path = 'outputs/chart_region_split.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
plt.close()
chart_paths.append(path)
print(f"Saved: {path}")

# Chart 4: Margin distribution (histogram + KDE)
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df['margin_pct'].dropna(), bins=25, color=COLORS[0], alpha=0.7,
        edgecolor='white', linewidth=0.5, density=True)
df['margin_pct'].dropna().plot.kde(ax=ax, color=COLORS[1], linewidth=2)
ax.axvline(df['margin_pct'].mean(), color='red', linestyle='--', linewidth=1.5,
           label=f"Mean: {df['margin_pct'].mean():.1f}%")
ax.axvline(df['margin_pct'].median(), color='orange', linestyle='--', linewidth=1.5,
           label=f"Median: {df['margin_pct'].median():.1f}%")
ax.set_title('Profit Margin Distribution', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Margin (%)')
ax.legend(frameon=False)
plt.tight_layout()
path = 'outputs/chart_margin_distribution.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
plt.close()
chart_paths.append(path)
print(f"Saved: {path}")

# Chart 5: Correlation heatmap
fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=-1, vmax=1, center=0, square=True, ax=ax,
            cbar_kws={'shrink': 0.8}, linewidths=0.5)
ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
path = 'outputs/chart_correlation.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
plt.close()
chart_paths.append(path)
print(f"Saved: {path}")


# ── PHASE 5: HTML REPORT ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 5 — HTML REPORT")
print("=" * 60)

import base64

def img_to_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

summary_stats = {
    'Total Revenue': f'${total_revenue:,.0f}',
    'Total Profit': f'${total_profit:,.0f}',
    'Avg Margin': f'{avg_margin:.1f}%',
    'Return Rate': f'{return_rate:.1f}%',
    'Orders': f'{len(df):,}',
    'Products': str(df['product'].nunique()),
}

insights = [
    f"Total revenue of <strong>${total_revenue:,.0f}</strong> was generated across {df['product'].nunique()} products and {df['region'].nunique()} regions.",
    f"<strong>{by_product.index[0]}</strong> is the top-selling product at ${by_product.iloc[0]:,.0f}, accounting for {by_product.iloc[0]/total_revenue*100:.1f}% of total revenue.",
    f"Average profit margin is <strong>{avg_margin:.1f}%</strong> (median: {df['margin_pct'].median():.1f}%), with significant variation across products.",
    f"The return rate stands at <strong>{return_rate:.1f}%</strong> — worth monitoring if it rises above 10%.",
    f"<strong>{top_sales.index[0]}</strong> leads all salespeople with ${top_sales.iloc[0]:,.0f} in revenue.",
]

stats_html = ''.join([
    f'<div class="metric"><div class="val">{v}</div><div class="lbl">{k}</div></div>'
    for k, v in summary_stats.items()
])
bullets_html = ''.join([f'<li>{i}</li>' for i in insights])
charts_html = ''.join([
    f'<img src="data:image/png;base64,{img_to_b64(p)}" '
    f'style="width:100%;border-radius:8px;margin-bottom:1.5rem;" />'
    for p in chart_paths
])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sales Analysis Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #F9FAFB; color: #111827; padding: 2rem; }}
  .container {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem; }}
  .subtitle {{ color: #6B7280; font-size: 0.9rem; margin-bottom: 2rem; }}
  .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
              gap: 1rem; margin-bottom: 2rem; }}
  .metric {{ background: white; border: 1px solid #E5E7EB; border-radius: 10px;
             padding: 1rem 1.25rem; text-align: center; }}
  .val {{ font-size: 1.4rem; font-weight: 700; color: #1D4ED8; }}
  .lbl {{ font-size: 0.72rem; color: #6B7280; margin-top: 4px;
          text-transform: uppercase; letter-spacing: 0.05em; }}
  .section {{ background: white; border: 1px solid #E5E7EB; border-radius: 10px;
              padding: 1.5rem; margin-bottom: 1.5rem; }}
  .section h2 {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;
                 padding-bottom: 0.5rem; border-bottom: 1px solid #F3F4F6; }}
  ul {{ padding-left: 1.25rem; }}
  li {{ margin-bottom: 0.6rem; line-height: 1.65; color: #374151; }}
  .footer {{ text-align: center; font-size: 0.8rem; color: #9CA3AF; margin-top: 2rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>Sales Analysis Report</h1>
  <p class="subtitle">Generated by Claude Data Analysis Skill · {pd.Timestamp.now().strftime('%B %d, %Y')}</p>
  <div class="metrics">{stats_html}</div>
  <div class="section">
    <h2>Key Insights</h2>
    <ul>{bullets_html}</ul>
  </div>
  <div class="section">
    <h2>Charts</h2>
    {charts_html}
  </div>
  <p class="footer">Built with the Claude data-analysis skill · github.com/your-repo</p>
</div>
</body>
</html>"""

report_path = 'outputs/sales_report.html'
with open(report_path, 'w') as f:
    f.write(html)

print(f"Report saved: {report_path}")
print("\n✓ Demo complete. Check the outputs/ folder.")
