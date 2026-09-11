"""Extract one drug from the GDSC1 and GDSC2 fitted-response workbooks.

The source workbooks are retained unchanged. This script creates a combined
analysis table, a dataset-level inventory, and a cross-screen agreement audit
under ``results/tables``. The detailed extracted record table is ignored by
Git because it is derived directly from provider data.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re

import pandas as pd
from scipy.stats import spearmanr


REQUIRED_COLUMNS = {
    "CELL_LINE_NAME",
    "SANGER_MODEL_ID",
    "DRUG_ID",
    "DRUG_NAME",
    "LN_IC50",
    "AUC",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract and audit one drug from GDSC1 and GDSC2."
    )
    parser.add_argument("--drug", default="trametinib")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root; defaults to the parent of the scripts folder.",
    )
    return parser.parse_args()


def safe_name(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", str(text).casefold()).strip("_")
    return value or "drug"


def require_columns(frame: pd.DataFrame, path: Path) -> None:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {sorted(missing)}")


def choose_primary_screen(
    selected: pd.DataFrame, dataset: str
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Choose one GDSC drug ID without looking at model performance.

    A named compound can occur under more than one GDSC ``DRUG_ID``. Mixing
    those screens can combine different concentration ranges, while keeping
    all rows creates duplicate dataset/model keys. We therefore choose the
    screen with the widest model coverage. Ties are resolved by the number of
    non-missing outcomes, then row count, then the lexical drug ID. This rule
    uses coverage only and never examines correlations or downstream results.
    """

    if selected["DRUG_ID"].isna().any():
        raise ValueError(f"{dataset} contains missing DRUG_ID values for the drug.")

    candidates = (
        selected.groupby("DRUG_ID", dropna=False)
        .agg(
            source_rows=("SANGER_MODEL_ID", "size"),
            unique_sanger_models=("SANGER_MODEL_ID", "nunique"),
            nonmissing_ln_ic50=("LN_IC50", "count"),
            nonmissing_auc=("AUC", "count"),
        )
        .reset_index()
    )
    candidates["drug_id_sort"] = candidates["DRUG_ID"].astype(str)
    candidates = candidates.sort_values(
        [
            "unique_sanger_models",
            "nonmissing_ln_ic50",
            "nonmissing_auc",
            "source_rows",
            "drug_id_sort",
        ],
        ascending=[False, False, False, False, True],
        kind="mergesort",
    )
    chosen_id = candidates.iloc[0]["DRUG_ID"]
    chosen = selected.loc[selected["DRUG_ID"].eq(chosen_id)].copy()
    candidate_text = ";".join(candidates["DRUG_ID"].astype(str))

    audit = {
        "candidate_drug_id_count": int(len(candidates)),
        "candidate_drug_ids_ranked": candidate_text,
        "selected_primary_drug_id": chosen_id,
        "primary_screen_source_rows": int(len(chosen)),
        "primary_screen_unique_sanger_models": int(
            chosen["SANGER_MODEL_ID"].nunique(dropna=True)
        ),
        "rows_excluded_from_nonprimary_drug_ids": int(len(selected) - len(chosen)),
        "screen_selection_rule": (
            "maximum unique Sanger-model coverage; ties by nonmissing outcomes, "
            "row count, then lexical DRUG_ID"
        ),
    }
    return chosen, audit


def collapse_within_screen_duplicates(
    selected: pd.DataFrame, dataset: str
) -> tuple[pd.DataFrame, int]:
    """Create one row per dataset/model after primary-screen selection."""

    missing_ids = selected["SANGER_MODEL_ID"].isna()
    if missing_ids.any():
        selected = selected.loc[~missing_ids].copy()

    duplicate_mask = selected.duplicated("SANGER_MODEL_ID", keep=False)
    duplicate_rows = int(duplicate_mask.sum())
    if not duplicate_rows:
        selected["SOURCE_ROW_COUNT"] = 1
        return selected, 0

    collapsed_rows: list[pd.Series] = []
    for model_id, group in selected.groupby("SANGER_MODEL_ID", sort=False):
        names = group["CELL_LINE_NAME"].dropna().astype(str).str.strip().unique()
        if len(names) > 1:
            raise ValueError(
                f"{dataset} primary screen maps {model_id} to conflicting names: "
                f"{sorted(names)}"
            )
        row = group.iloc[0].copy()
        row["LN_IC50"] = group["LN_IC50"].mean()
        row["AUC"] = group["AUC"].mean()
        row["SOURCE_ROW_COUNT"] = int(len(group))
        collapsed_rows.append(row)

    collapsed = pd.DataFrame(collapsed_rows).reset_index(drop=True)
    return collapsed, duplicate_rows


def load_one_dataset(path: Path, dataset: str, drug: str) -> tuple[pd.DataFrame, dict]:
    if not path.exists():
        raise FileNotFoundError(f"Required GDSC workbook not found: {path}")

    frame = pd.read_excel(path, engine="openpyxl")
    require_columns(frame, path)

    drug_names = frame["DRUG_NAME"].astype("string").str.strip()
    selected = frame.loc[drug_names.str.casefold() == drug.casefold()].copy()
    if selected.empty:
        raise ValueError(f"No exact case-insensitive match for {drug!r} in {path.name}")

    selected.insert(0, "source_dataset", dataset)
    selected["SANGER_MODEL_ID"] = (
        selected["SANGER_MODEL_ID"].astype("string").str.strip()
    )
    selected["CELL_LINE_NAME"] = selected["CELL_LINE_NAME"].astype("string").str.strip()
    selected["LN_IC50"] = pd.to_numeric(selected["LN_IC50"], errors="coerce")
    selected["AUC"] = pd.to_numeric(selected["AUC"], errors="coerce")

    all_matching_rows = int(len(selected))
    all_matching_models = int(selected["SANGER_MODEL_ID"].nunique(dropna=True))
    selected, screen_audit = choose_primary_screen(selected, dataset)
    selected, duplicate_key_rows = collapse_within_screen_duplicates(
        selected, dataset
    )

    inventory = {
        "source_dataset": dataset,
        "source_file": path.name,
        "source_rows": int(len(frame)),
        "drug_name_requested": drug,
        "matching_drug_rows_all_ids": all_matching_rows,
        "unique_sanger_models_all_ids": all_matching_models,
        **screen_audit,
        "analysis_rows_after_resolution": int(len(selected)),
        "unique_sanger_models": int(selected["SANGER_MODEL_ID"].nunique(dropna=True)),
        "missing_sanger_model_id": int(selected["SANGER_MODEL_ID"].isna().sum()),
        "within_primary_screen_duplicate_rows_collapsed": duplicate_key_rows,
        "missing_ln_ic50": int(selected["LN_IC50"].isna().sum()),
        "missing_auc": int(selected["AUC"].isna().sum()),
        "ln_ic50_min": float(selected["LN_IC50"].min()),
        "ln_ic50_median": float(selected["LN_IC50"].median()),
        "ln_ic50_max": float(selected["LN_IC50"].max()),
        "auc_min": float(selected["AUC"].min()),
        "auc_median": float(selected["AUC"].median()),
        "auc_max": float(selected["AUC"].max()),
    }
    return selected, inventory


def cross_screen_agreement(combined: pd.DataFrame) -> pd.DataFrame:
    columns = ["SANGER_MODEL_ID", "LN_IC50", "AUC"]
    first = combined.loc[combined["source_dataset"] == "GDSC1", columns].copy()
    second = combined.loc[combined["source_dataset"] == "GDSC2", columns].copy()
    shared = first.merge(second, on="SANGER_MODEL_ID", suffixes=("_GDSC1", "_GDSC2"))

    rows = []
    for outcome in ["LN_IC50", "AUC"]:
        values = shared[[f"{outcome}_GDSC1", f"{outcome}_GDSC2"]].dropna()
        if (
            len(values) < 3
            or values.iloc[:, 0].nunique() < 2
            or values.iloc[:, 1].nunique() < 2
        ):
            rho = float("nan")
        else:
            rho = float(spearmanr(values.iloc[:, 0], values.iloc[:, 1]).statistic)
        rows.append(
            {
                "outcome": outcome,
                "shared_models": int(len(values)),
                "spearman_rho": rho,
                "note": "Cross-screen agreement; shared models are not independent cohorts.",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_arguments()
    project = args.project_root.resolve()
    source_folder = project / "data" / "raw" / "gdsc"
    output_folder = project / "results" / "tables"
    output_folder.mkdir(parents=True, exist_ok=True)

    sources = {
        "GDSC1": source_folder / "GDSC1_fitted_dose_response_27Oct23.xlsx",
        "GDSC2": source_folder / "GDSC2_fitted_dose_response_27Oct23.xlsx",
    }

    frames = []
    inventory_rows = []
    for dataset, path in sources.items():
        selected, inventory = load_one_dataset(path, dataset, args.drug)
        frames.append(selected)
        inventory_rows.append(inventory)

    combined = pd.concat(frames, ignore_index=True)
    if combined.duplicated(["source_dataset", "SANGER_MODEL_ID"]).any():
        raise ValueError(
            "Duplicate dataset/model keys remain after drug filtering. "
            "Inspect technical replicates before external validation."
        )

    slug = safe_name(args.drug)
    records_path = output_folder / f"gdsc_{slug}_records.csv"
    inventory_path = output_folder / f"gdsc_{slug}_inventory.csv"
    agreement_path = output_folder / f"gdsc_{slug}_cross_screen_agreement.csv"

    combined.to_csv(records_path, index=False)
    pd.DataFrame(inventory_rows).to_csv(inventory_path, index=False)
    cross_screen_agreement(combined).to_csv(agreement_path, index=False)

    print(f"Saved {len(combined):,} filtered records to {records_path}")
    print(f"Saved dataset inventory to {inventory_path}")
    print(f"Saved cross-screen audit to {agreement_path}")


if __name__ == "__main__":
    main()
