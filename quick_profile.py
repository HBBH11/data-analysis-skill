"""
quick_profile.py
----------------
Instantly profile any data file from the command line.
Supports: CSV, Excel (.xlsx/.xls), JSON

Usage:
    python scripts/quick_profile.py path/to/file.csv
    python scripts/quick_profile.py path/to/file.xlsx
    python scripts/quick_profile.py path/to/data.json
"""

import sys
import json
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')


def load_file(path: str) -> pd.DataFrame:
    ext = path.rsplit('.', 1)[-1].lower()
    if ext == 'csv':
        return pd.read_csv(path)
    elif ext in ('xlsx', 'xls', 'xlsm'):
        return pd.read_excel(path)
    elif ext == 'json':
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            return pd.json_normalize(data)
        elif isinstance(data, dict):
            # Try to find the main array key
            for v in data.values():
                if isinstance(v, list):
                    return pd.json_normalize(v)
            return pd.DataFrame([data])
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def profile(df: pd.DataFrame) -> None:
    divider = "─" * 60

    print(f"\n{divider}")
    print(f"  SHAPE: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(divider)

    # Duplicate check
    dupes = df.duplicated().sum()
    if dupes:
        print(f"  ⚠  {dupes} duplicate rows detected")

    # Column-by-column breakdown
    print(f"\n{'Column':<25} {'Type':<12} {'Nulls':>6} {'Unique':>8}  Top / Stats")
    print("─" * 80)

    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        null_pct = null_count / len(df) * 100
        unique = df[col].nunique()
        null_str = f"{null_count} ({null_pct:.0f}%)" if null_count else "0"

        if pd.api.types.is_numeric_dtype(df[col]):
            s = df[col].dropna()
            stats_str = f"min={s.min():.2g}  mean={s.mean():.2g}  max={s.max():.2g}"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            stats_str = f"{df[col].min().date()} → {df[col].max().date()}"
        else:
            top = df[col].value_counts().head(3).index.tolist()
            stats_str = ", ".join([str(v) for v in top])

        col_display = (col[:23] + '…') if len(col) > 24 else col
        print(f"  {col_display:<23} {dtype:<12} {null_str:>8} {unique:>8}  {stats_str}")

    # Numeric summary
    numerics = df.select_dtypes(include=np.number)
    if not numerics.empty:
        print(f"\n{divider}")
        print("  NUMERIC SUMMARY")
        print(divider)
        print(numerics.describe().round(2).to_string())

    # Outlier scan
    print(f"\n{divider}")
    print("  OUTLIER SCAN  (IQR method, threshold = 1.5×)")
    print(divider)
    found_any = False
    for col in numerics.columns:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        n = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
        if n > 0:
            print(f"  {col:<25} {n} outliers")
            found_any = True
    if not found_any:
        print("  No outliers detected.")

    # Suggested analysis
    date_cols = [c for c in df.columns
                 if 'date' in c.lower() or 'time' in c.lower() or 'day' in c.lower()]
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    print(f"\n{divider}")
    print("  SUGGESTED NEXT STEPS")
    print(divider)
    if date_cols:
        print(f"  • Time series: group by {date_cols[0]} and plot trend")
    if numerics.shape[1] >= 2:
        print(f"  • Correlation: run .corr() across {numerics.shape[1]} numeric columns")
    if cat_cols:
        print(f"  • Aggregation: group by {cat_cols[0]} and compare metrics")
    if dupes:
        print(f"  • Clean: drop {dupes} duplicate rows before analysis")
    null_cols = [c for c in df.columns if df[c].isnull().any()]
    if null_cols:
        print(f"  • Handle nulls in: {', '.join(null_cols)}")

    print(f"\n{divider}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/quick_profile.py <file.csv|file.xlsx|file.json>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"\nLoading: {path}")

    try:
        df = load_file(path)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

    profile(df)


if __name__ == '__main__':
    main()
