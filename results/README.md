# Derived results

These files are analysis outputs, not raw source datasets.

## Figures

| File | Contents |
|---|---|
| `trametinib_gdsc2_strict_gene_external_validation.png` | Primary strict GDSC2 gene-model validation |
| `trametinib_gdsc_gene_vs_pathway_external_comparison.png` | External gene-versus-pathway comparisons |
| `trametinib_gene_vs_pathway_comparison.png` | Internal representation comparison |
| `multidrug_primary_elasticnet_forest_plot.png` | Prespecified GDSC2 primary comparisons with GDSC1 supporting results |
| `all_drugs_gdsc2_representation_heatmap.png` | GDSC2 pathway-minus-gene differences across both learned models and correlations |

## Central tables

| File | Contents |
|---|---|
| `trametinib_validation_comparison.csv` | Random-fold and held-out-tissue internal metrics |
| `trametinib_gdsc_gene_external_metrics.csv` | Gene-model external metrics and bootstrap intervals |
| `trametinib_gdsc_pathway_external_metrics.csv` | Pathway-model external metrics and bootstrap intervals |
| `trametinib_gdsc_gene_vs_pathway_external_comparison.csv` | Paired representation differences and conclusions |
| `trametinib_gdsc_gene_external_feature_audit.csv` | Gene alignment, training rows, selected features, and leakage audit |
| `trametinib_gdsc_pathway_external_feature_audit.csv` | Pathway coverage, training rows, and leakage audit |
| `multidrug_run_status.csv` | Completion status and frozen panel hash for all five extension drugs |
| `multidrug_gdsc_gene_external_metrics.csv` | Extension gene-model external metrics |
| `multidrug_gdsc_pathway_external_metrics.csv` | Extension pathway-model external metrics |
| `multidrug_gdsc_gene_vs_pathway_external_comparison.csv` | All paired external representation comparisons for the extension |
| `multidrug_internal_gene_vs_pathway_comparison.csv` | Internal gene-versus-pathway metrics for the extension |
| `all_drugs_primary_elasticnet_summary.csv` | Primary Elastic Net summary for the pilot and extension |
| `all_drugs_quality_control_summary.csv` | Consolidated cohort, feature, and leakage audit |

Aggregate per-drug quality-control files are stored under `results/audits/`.

The numbered scripts generate row-level prediction and split-manifest files during a local full-data run. Those files are intentionally ignored by Git because they contain provider-derived row-level outcomes. The public aggregate audits preserve the reported cohort counts and inclusion checks. None of these outputs should be interpreted as patient data or clinical predictions.

Provider-controlled raw files are excluded. Users reproducing the analysis must obtain them from the sources listed in [data/README.md](../data/README.md).
