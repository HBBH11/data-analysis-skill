# 📊 Data Analysis & Visualization Skill for Claude

A production-ready skill that teaches Claude how to turn raw data — CSV, Excel, JSON, SQL dumps — into clear insights, professional charts, and shareable reports.

## What it does

When this skill is loaded, Claude will:

- **Profile** any uploaded data file before touching it
- **Clean** the data (fix dtypes, handle nulls, detect outliers, remove dupes)
- **Analyze** using the right pattern for the user's question
- **Visualize** with professional, colorblind-safe charts
- **Narrate** findings in plain English — not just numbers
- **Deliver** PNG charts, cleaned files, or full HTML reports

## Skill triggers

Claude will use this skill when users say things like:

- *"Analyze this CSV"*
- *"Show me a chart of sales by month"*
- *"Find anomalies in my data"*
- *"What's the trend in this dataset?"*
- *"Build me a dashboard"*
- *"Clean this data and summarize it"*
- *"What's the correlation between X and Y?"*

## Repo structure

```
data-analysis-skill/
├── SKILL.md                     ← The skill itself (Claude reads this)
├── README.md                    ← This file
├── requirements.txt             ← Python dependencies
├── examples/
│   ├── sample_sales.csv         ← Example dataset (retail sales)
│   ├── sample_timeseries.csv    ← Example dataset (time series with anomalies)
│   └── demo_analysis.py         ← Standalone demo: runs the full pipeline
├── tests/
│   └── test_prompts.md          ← Eval prompts for verifying the skill
└── scripts/
    └── quick_profile.py         ← Utility: instantly profile any data file
```

## Installation

1. Clone or download this repo
2. Copy `SKILL.md` into your Claude skills directory:
   ```
   /mnt/skills/public/data-analysis/SKILL.md
   ```
3. That's it — Claude will auto-detect and apply the skill

## Python dependencies

```bash
pip install -r requirements.txt
```

## Testing the skill

Use the prompts in `tests/test_prompts.md` to verify Claude applies the skill correctly.
Upload one of the sample CSVs from `examples/` alongside each test prompt.

## License

MIT — free to use, modify, and share.
