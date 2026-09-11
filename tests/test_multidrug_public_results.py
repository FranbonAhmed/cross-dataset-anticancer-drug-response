from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"


def test_extension_completed_under_one_frozen_panel():
    status = pd.read_csv(TABLES / "multidrug_run_status.csv")
    assert status["drug_name"].tolist() == [
        "gemcitabine",
        "docetaxel",
        "talazoparib",
        "vorinostat",
        "bortezomib",
    ]
    assert status["run_status"].eq("complete").all()
    assert status["missing_output_count"].eq(0).all()
    assert status["panel_file_sha256"].nunique() == 1


def test_primary_extension_results_and_conclusions():
    summary = pd.read_csv(TABLES / "all_drugs_primary_elasticnet_summary.csv")
    rows = summary.loc[
        summary["dataset"].eq("GDSC2")
        & summary["study_role"].eq("Confirmatory extension")
    ].sort_values("panel_order")
    assert rows["n"].tolist() == [349, 351, 347, 352, 348]
    expected = np.array([0.414491, 0.086030, 0.284398, -0.104929, 0.272088])
    assert np.allclose(
        rows["pearson_difference_pathway_minus_gene"], expected, atol=1e-6
    )
    assert rows["pearson_conclusion"].tolist() == [
        "pathway favored",
        "difference uncertain",
        "pathway favored",
        "individual genes favored",
        "pathway favored",
    ]


def test_all_external_comparison_counts():
    comparison = pd.read_csv(
        TABLES / "multidrug_gdsc_gene_vs_pathway_external_comparison.csv"
    )
    assert len(comparison) == 80
    primary = comparison.loc[
        comparison["cohort"].eq("GDSC2_strict_sanger_heldout")
        & comparison["outcome"].eq("LN_IC50")
    ]
    conclusions = pd.concat(
        [primary["pearson_conclusion"], primary["spearman_conclusion"]],
        ignore_index=True,
    )
    assert len(conclusions) == 20
    assert (conclusions == "pathway favored").sum() == 8
    assert (conclusions == "individual genes favored").sum() == 6
    assert (conclusions == "difference uncertain").sum() == 6
    assert comparison["successful_paired_bootstraps"].eq(1000).all()


def test_consolidated_quality_control():
    audit = pd.read_csv(TABLES / "all_drugs_quality_control_summary.csv")
    assert len(audit) == 6
    assert audit["common_gene_symbols"].eq(19204).all()
    assert audit["genes_selected_inside_training"].eq(1000).all()
    assert audit["pathway_member_genes"].eq(4374).all()
    assert audit["hallmark_pathways"].eq(50).all()
    assert audit["gdsc_outcomes_used_during_training"].eq(0).all()
