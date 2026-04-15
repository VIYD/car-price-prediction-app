from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import model


def _write_text_summary(df_raw: pd.DataFrame, df_clean: pd.DataFrame, output_dir: Path) -> None:
    numeric_cols = df_clean.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in df_clean.columns if col not in numeric_cols]

    summary = [
        "================ Dataset Analysis Summary ================",
        f"Raw shape: {df_raw.shape}",
        f"Clean shape: {df_clean.shape}",
        f"Rows removed during cleaning: {len(df_raw) - len(df_clean)}",
        f"Numeric columns ({len(numeric_cols)}): {', '.join(numeric_cols)}",
        f"Categorical columns ({len(categorical_cols)}): {', '.join(categorical_cols)}",
        "==========================================================",
    ]

    (output_dir / "summary.txt").write_text("\n".join(summary), encoding="utf-8")


def _save_missing_values(df_raw: pd.DataFrame, output_dir: Path) -> None:
    missing = df_raw.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = (missing["missing_count"] / len(df_raw) * 100).round(2)
    missing.sort_values("missing_count", ascending=False).to_csv(output_dir / "missing_values.csv")


def _save_numeric_describe(df_clean: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    numeric_df = df_clean.select_dtypes(include=["number"])
    describe_df = numeric_df.describe().T
    describe_df.to_csv(output_dir / "numeric_describe.csv")
    return numeric_df


def _save_top_categories(df_clean: pd.DataFrame, output_dir: Path, top_n: int) -> None:
    rows: list[dict[str, object]] = []
    categorical_cols = df_clean.select_dtypes(exclude=["number"]).columns.tolist()

    for col in categorical_cols:
        counts = df_clean[col].astype(str).value_counts().head(top_n)
        for category, count in counts.items():
            rows.append(
                {
                    "column": col,
                    "category": category,
                    "count": int(count),
                    "percent": round(float(count) / len(df_clean) * 100, 2),
                }
            )

    pd.DataFrame(rows).to_csv(output_dir / "top_categories.csv", index=False)


def _save_correlation_artifacts(numeric_df: pd.DataFrame, output_dir: Path) -> None:
    if numeric_df.shape[1] < 2:
        pd.DataFrame().to_csv(output_dir / "correlation_matrix.csv", index=False)
        return

    corr = numeric_df.corr(numeric_only=True)
    corr.to_csv(output_dir / "correlation_matrix.csv")

    if "price" in corr.columns:
        price_corr = corr["price"].drop(labels=["price"], errors="ignore")
        price_corr.reindex(price_corr.abs().sort_values(ascending=False).index).to_frame("corr_with_price").to_csv(
            output_dir / "price_correlations.csv"
        )

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True, cbar=True)
    plt.title("Numeric Feature Correlation Matrix")
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_heatmap.png", dpi=150)
    plt.close()


def run_analysis(output_dir: Path, top_n_categories: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    df_raw = model.get_dataset()
    df_clean = model.clean_data(df_raw)

    _write_text_summary(df_raw, df_clean, output_dir)
    _save_missing_values(df_raw, output_dir)
    numeric_df = _save_numeric_describe(df_clean, output_dir)
    _save_top_categories(df_clean, output_dir, top_n=top_n_categories)
    _save_correlation_artifacts(numeric_df, output_dir)

    print(f"Analysis completed. Artifacts saved to: {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run dataset analysis and generate correlation artifacts.")
    parser.add_argument(
        "--output-dir",
        default=Path(__file__).resolve().parent / "analysis",
        type=Path,
        help="Directory where analysis artifacts will be written.",
    )
    parser.add_argument(
        "--top-n-categories",
        default=10,
        type=int,
        help="Top N category values per categorical column to include in the report.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_analysis(output_dir=args.output_dir, top_n_categories=max(1, args.top_n_categories))