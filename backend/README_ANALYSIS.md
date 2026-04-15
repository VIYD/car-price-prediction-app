# Dataset Analysis

This project includes a dataset analysis utility in `analyze_dataset.py`.

It generates:

- `summary.txt` (dataset shape and column overview)
- `missing_values.csv` (missing counts and percentages)
- `numeric_describe.csv` (descriptive stats for numeric columns)
- `top_categories.csv` (most frequent categorical values)
- `correlation_matrix.csv` (numeric feature correlation matrix)
- `price_correlations.csv` (feature correlations with `price`)
- `correlation_heatmap.png` (visual correlation matrix)

## Run

From `backend/`, run:

- `python analyze_dataset.py`

Optional flags:

- `--output-dir <path>`
- `--top-n-categories <int>`

By default, output is written to `backend/analysis/`.