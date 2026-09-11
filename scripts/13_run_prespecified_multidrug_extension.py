"""Run the locked multi-drug extension with logging and safe resume support.

By default, this script runs the five rows marked ``Confirmatory extension``
in ``config/prespecified_multidrug_panel.csv``. Trametinib remains the
exploratory pilot and is not silently pooled into confirmatory inference.

The runner does not change modeling choices. It orchestrates scripts 04-12,
skips steps whose complete output set already exists, stops on the first error
unless explicitly told otherwise, and writes cross-drug summary tables.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable

import pandas as pd


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the prespecified PRISM-to-GDSC multi-drug extension."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root; defaults to the parent of the scripts folder.",
    )
    parser.add_argument(
        "--panel-file",
        type=Path,
        default=Path("config/prespecified_multidrug_panel.csv"),
        help="Locked panel CSV, relative to project root unless absolute.",
    )
    parser.add_argument(
        "--mode",
        choices=("full", "external"),
        default="full",
        help=(
            "full runs internal audits and tissue/pathway checks plus external "
            "validation; external omits optional scripts 05-07."
        ),
    )
    parser.add_argument(
        "--include-pilot",
        action="store_true",
        help="Also rerun trametinib. The default runs confirmatory drugs only.",
    )
    parser.add_argument(
        "--bootstrap-repeats",
        type=int,
        default=1000,
        help="Bootstrap samples for scripts 05, 11, and 12 (default: 1000).",
    )
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rerun completed steps instead of resuming from existing outputs.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue to later drugs after a failed step; default is stop.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the plan and input warnings without running analyses.",
    )
    return parser.parse_args()


def safe_name(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", str(text).casefold()).strip("_")
    return value or "drug"


def resolve_path(project: Path, path: Path) -> Path:
    return path if path.is_absolute() else project / path


def read_panel(path: Path, include_pilot: bool) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Prespecified panel file not found: {path}")
    panel = pd.read_csv(path)
    required = {
        "panel_order",
        "drug_name",
        "study_role",
        "mechanism_class",
        "coverage_gate",
    }
    missing = required.difference(panel.columns)
    if missing:
        raise ValueError(f"Panel is missing required columns: {sorted(missing)}")
    if panel["drug_name"].astype(str).str.casefold().duplicated().any():
        raise ValueError("Panel contains duplicated drug names.")
    if not panel["coverage_gate"].astype(str).str.casefold().eq("pass").all():
        failed = panel.loc[
            ~panel["coverage_gate"].astype(str).str.casefold().eq("pass"),
            "drug_name",
        ].tolist()
        raise ValueError(f"Coverage gate is not PASS for: {failed}")

    roles = panel["study_role"].astype(str).str.casefold()
    if include_pilot:
        selected = panel.loc[
            roles.isin({"exploratory pilot", "confirmatory extension"})
        ].copy()
    else:
        selected = panel.loc[roles.eq("confirmatory extension")].copy()
    if selected.empty:
        raise ValueError("No eligible drugs were found in the panel.")
    return selected.sort_values("panel_order", kind="mergesort").reset_index(drop=True)


def required_raw_inputs(project: Path) -> list[Path]:
    return [
        project
        / "data/raw/depmap/OmicsExpressionProteinCodingGenesTPMLogp1.csv",
        project / "data/raw/depmap/Model.csv",
        project
        / "data/raw/prism/primary-screen-replicate-collapsed-logfold-change.csv",
        project
        / "data/raw/prism/primary-screen-replicate-collapsed-treatment-info.csv",
        project / "data/raw/prism/primary-screen-cell-line-info.csv",
        project / "data/raw/gdsc/GDSC1_fitted_dose_response_27Oct23.xlsx",
        project / "data/raw/gdsc/GDSC2_fitted_dose_response_27Oct23.xlsx",
        project / "data/raw/gdsc/rnaseq_merged_rsem_tpm_20260323.csv",
        project / "data/raw/msigdb/h.all.v2026.1.Hs.symbols.gmt",
    ]


def expected_outputs(project: Path, prefix: str, step: str) -> list[Path]:
    tables = project / "results/tables"
    figures = project / "results/figures"
    outputs = {
        "04": [
            tables / f"{prefix}_metrics.csv",
            tables / f"{prefix}_predictions.csv",
        ],
        "05": [
            tables / f"{prefix}_fold_metrics.csv",
            tables / f"{prefix}_bootstrap_intervals.csv",
            figures / f"{prefix}_residual_diagnostics.png",
            figures / f"{prefix}_fold_stability.png",
        ],
        "06": [
            tables / f"{prefix}_lineage_metrics.csv",
            tables / f"{prefix}_lineage_predictions.csv",
            tables / f"{prefix}_validation_comparison.csv",
            tables / f"{prefix}_lineage_fold_assignments.csv",
            figures / f"{prefix}_validation_comparison.png",
        ],
        "07": [
            tables / f"{prefix}_pathway_metrics.csv",
            tables / f"{prefix}_gene_vs_pathway_comparison.csv",
            figures / f"{prefix}_gene_vs_pathway_comparison.png",
        ],
        "08": [
            tables / f"gdsc_{prefix}_records.csv",
            tables / f"gdsc_{prefix}_inventory.csv",
            tables / f"gdsc_{prefix}_cross_screen_agreement.csv",
        ],
        "10": [
            tables / f"{prefix}_gdsc_external_validation_split_audit.csv",
            tables / f"{prefix}_gdsc_external_validation_split_manifest.csv",
            tables / f"{prefix}_prism_training_ids_without_sanger_mapping.csv",
        ],
        "11": [
            tables / f"{prefix}_gdsc_gene_external_metrics.csv",
            tables / f"{prefix}_gdsc_gene_external_predictions.csv",
            tables / f"{prefix}_gdsc_gene_external_feature_audit.csv",
            figures / f"{prefix}_gdsc2_strict_gene_external_validation.png",
        ],
        "12": [
            tables / f"{prefix}_gdsc_pathway_external_metrics.csv",
            tables / f"{prefix}_gdsc_gene_vs_pathway_external_comparison.csv",
            tables / f"{prefix}_gdsc_pathway_external_feature_audit.csv",
            figures / f"{prefix}_gdsc_gene_vs_pathway_external_comparison.png",
        ],
    }
    return outputs[step]


def step_command(
    project: Path,
    step: str,
    drug: str,
    bootstrap_repeats: int,
    random_state: int,
) -> list[str]:
    script_names = {
        "04": "04_run_one_drug_baseline.py",
        "05": "05_audit_one_drug_baseline.py",
        "06": "06_run_lineage_aware_validation.py",
        "07": "07_run_pathway_comparison.py",
        "08": "08_prepare_gdsc_response.py",
        "10": "10_audit_external_validation_split.py",
        "11": "11_run_gdsc_gene_external_validation.py",
        "12": "12_run_gdsc_pathway_external_comparison.py",
    }
    command = [sys.executable, str(project / "scripts" / script_names[step]), "--drug", drug]
    if step in {"05", "11", "12"}:
        command.extend(["--bootstrap-repeats", str(bootstrap_repeats)])
    if step in {"05", "06", "07", "11", "12"}:
        command.extend(["--random-state", str(random_state)])
    if step in {"08", "10", "11", "12"}:
        command.extend(["--project-root", str(project)])
    return command


def format_command(command: Iterable[str]) -> str:
    return subprocess.list2cmdline(list(command))


def run_logged(command: list[str], log_path: Path, project: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"RUN: {format_command(command)}")
    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"COMMAND: {format_command(command)}\n\n")
        process = subprocess.Popen(
            command,
            cwd=project,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log.write(line)
        return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)


def ensure_expression_manifest(
    project: Path,
    force: bool,
    dry_run: bool,
    bootstrap_repeats: int,
    random_state: int,
) -> None:
    manifest = project / "results/tables/gdsc_expression_model_manifest.csv"
    if manifest.exists() and not force:
        print(f"SKIP one-time expression audit: {manifest.name} already exists")
        return

    trametinib_records = project / "results/tables/gdsc_trametinib_records.csv"
    if not trametinib_records.exists() or force:
        command = step_command(
            project, "08", "trametinib", bootstrap_repeats, random_state
        )
        print(f"ONE-TIME PREREQUISITE: {format_command(command)}")
        if not dry_run:
            run_logged(
                command,
                project / "results/logs/multidrug/trametinib_step_08.log",
                project,
            )

    command = [
        sys.executable,
        str(project / "scripts/09_audit_gdsc_expression.py"),
        "--project-root",
        str(project),
    ]
    print(f"ONE-TIME PREREQUISITE: {format_command(command)}")
    if not dry_run:
        run_logged(
            command,
            project / "results/logs/multidrug/expression_step_09.log",
            project,
        )
        if not manifest.exists():
            raise FileNotFoundError(f"Step 09 did not create {manifest}")


def add_panel_metadata(frame: pd.DataFrame, row: pd.Series) -> pd.DataFrame:
    output = frame.copy()
    for column in ("panel_order", "drug_name", "study_role", "mechanism_class"):
        output.insert(len(output.columns), column, row[column])
    return output


def aggregate_results(project: Path, panel: pd.DataFrame, mode: str) -> list[Path]:
    tables = project / "results/tables"
    specifications = {
        "multidrug_gdsc_gene_external_metrics.csv": "{prefix}_gdsc_gene_external_metrics.csv",
        "multidrug_gdsc_pathway_external_metrics.csv": "{prefix}_gdsc_pathway_external_metrics.csv",
        "multidrug_gdsc_gene_vs_pathway_external_comparison.csv": (
            "{prefix}_gdsc_gene_vs_pathway_external_comparison.csv"
        ),
    }
    if mode == "full":
        specifications["multidrug_internal_gene_vs_pathway_comparison.csv"] = (
            "{prefix}_gene_vs_pathway_comparison.csv"
        )

    saved: list[Path] = []
    for destination_name, source_template in specifications.items():
        pieces = []
        for _, row in panel.iterrows():
            prefix = safe_name(row["drug_name"])
            source = tables / source_template.format(prefix=prefix)
            if source.exists():
                pieces.append(add_panel_metadata(pd.read_csv(source), row))
        if pieces:
            destination = tables / destination_name
            pd.concat(pieces, ignore_index=True).to_csv(destination, index=False)
            saved.append(destination)
    return saved


def write_run_status(
    project: Path,
    panel: pd.DataFrame,
    steps: list[str],
    panel_hash: str,
) -> Path:
    rows = []
    for _, row in panel.iterrows():
        prefix = safe_name(row["drug_name"])
        missing = [
            str(path.relative_to(project))
            for step in steps
            for path in expected_outputs(project, prefix, step)
            if not path.exists()
        ]
        rows.append(
            {
                "panel_order": row["panel_order"],
                "drug_name": row["drug_name"],
                "study_role": row["study_role"],
                "run_status": "complete" if not missing else "incomplete",
                "missing_output_count": len(missing),
                "missing_outputs": ";".join(missing),
                "panel_file_sha256": panel_hash,
            }
        )
    path = project / "results/tables/multidrug_run_status.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def main() -> None:
    arguments = parse_arguments()
    if arguments.bootstrap_repeats < 200:
        raise ValueError("Use at least 200 bootstrap repeats; 1000 is recommended.")

    project = arguments.project_root.resolve()
    panel_path = resolve_path(project, arguments.panel_file).resolve()
    panel = read_panel(panel_path, arguments.include_pilot)
    panel_hash = hashlib.sha256(panel_path.read_bytes()).hexdigest()
    steps = ["04", "08", "10", "11", "12"]
    if arguments.mode == "full":
        steps = ["04", "05", "06", "07", "08", "10", "11", "12"]

    missing_inputs = [path for path in required_raw_inputs(project) if not path.exists()]
    print("PRESPECIFIED MULTI-DRUG EXTENSION")
    print(f"Panel: {panel_path}")
    print(f"Panel SHA-256: {panel_hash}")
    print(f"Mode: {arguments.mode}")
    print("Drugs: " + ", ".join(panel["drug_name"].astype(str)))
    if missing_inputs:
        print("\nMISSING RAW INPUTS:")
        for path in missing_inputs:
            print(f"  {path}")
        if not arguments.dry_run:
            raise FileNotFoundError(
                "Place every required provider file before starting the batch."
            )

    ensure_expression_manifest(
        project,
        arguments.force,
        arguments.dry_run,
        arguments.bootstrap_repeats,
        arguments.random_state,
    )

    failures: list[str] = []
    for _, row in panel.iterrows():
        drug = str(row["drug_name"])
        prefix = safe_name(drug)
        print(f"\n{'=' * 72}\nDRUG: {drug}\n{'=' * 72}")
        for step in steps:
            outputs = expected_outputs(project, prefix, step)
            if not arguments.force and all(path.exists() for path in outputs):
                print(f"SKIP step {step}: all expected outputs already exist")
                continue
            command = step_command(
                project,
                step,
                drug,
                arguments.bootstrap_repeats,
                arguments.random_state,
            )
            if arguments.dry_run:
                print(f"PLAN step {step}: {format_command(command)}")
                continue
            try:
                run_logged(
                    command,
                    project / f"results/logs/multidrug/{prefix}_step_{step}.log",
                    project,
                )
                missing = [path for path in outputs if not path.exists()]
                if missing:
                    raise FileNotFoundError(
                        f"Step {step} finished but outputs are missing: {missing}"
                    )
            except Exception as exc:
                message = f"{drug} step {step}: {exc}"
                failures.append(message)
                print(f"ERROR: {message}")
                if not arguments.continue_on_error:
                    status_path = write_run_status(
                        project, panel, steps, panel_hash
                    )
                    print(f"Run status saved to {status_path}")
                    raise
                break

    if arguments.dry_run:
        print("\nDRY RUN COMPLETED — no analysis commands were executed.")
        return

    saved = aggregate_results(project, panel, arguments.mode)
    status_path = write_run_status(project, panel, steps, panel_hash)
    status = pd.read_csv(status_path)
    incomplete = status.loc[status["run_status"].ne("complete"), "drug_name"].tolist()

    print("\nMULTI-DRUG RUN SUMMARY")
    print(status[["drug_name", "run_status", "missing_output_count"]].to_string(index=False))
    print("\nSaved aggregate tables:")
    for path in [*saved, status_path]:
        print(path)
    if failures or incomplete:
        raise RuntimeError(
            "The extension is incomplete. Rerun the same command to resume. "
            f"Failures: {failures}; incomplete drugs: {incomplete}"
        )
    print("\nPRESPECIFIED MULTI-DRUG EXTENSION COMPLETED")


if __name__ == "__main__":
    main()
