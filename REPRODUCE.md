# Reproduction guide

## Fast verification without raw data

The repository includes small synthetic-data tests and checks of the committed public results:

```bash
conda env create -f environment.yml
conda activate pharmacogenomics
pytest -q
```

This verifies the software path and the reported result files. It does not refit the real-data models.

## Full real-data workflow

Download and place the source files as described in [data/README.md](data/README.md), then run the numbered scripts from the repository root:

```bash
python scripts/00_check_setup.py
python scripts/03_inventory_real_data.py
python scripts/04_run_one_drug_baseline.py --drug trametinib
python scripts/05_audit_one_drug_baseline.py --drug trametinib
python scripts/06_run_lineage_aware_validation.py --drug trametinib
python scripts/07_run_pathway_comparison.py --drug trametinib
python scripts/08_prepare_gdsc_response.py --drug trametinib
python scripts/09_audit_gdsc_expression.py
python scripts/10_audit_external_validation_split.py --drug trametinib
python scripts/11_run_gdsc_gene_external_validation.py --drug trametinib
python scripts/12_run_gdsc_pathway_external_comparison.py --drug trametinib
```

For the locked five-drug extension, script 13 safely orchestrates the same
stages, resumes after interruptions, and creates combined result tables:

```bash
python scripts/13_run_prespecified_multidrug_extension.py --mode full --dry-run
python scripts/13_run_prespecified_multidrug_extension.py --mode full
```

Scripts `01` and `02` are optional beginner exercises that generate and analyze synthetic data. They are not used to produce the reported scientific results.

## What each stage does

| Script | Purpose |
|---|---|
| `00` | Check Python packages and expected project directories |
| `01` | Generate synthetic expression and response data |
| `02` | Run the baseline on synthetic data |
| `03` | Inventory the real input files without modeling |
| `04` | Fit the one-drug PRISM/DepMap baseline with out-of-fold predictions |
| `05` | Audit saved predictions, uncertainty, tails, residuals, and tissues |
| `06` | Hold complete primary-tissue groups out of training |
| `07` | Compare gene and Hallmark-pathway representations internally |
| `08` | Extract one drug from GDSC1/GDSC2 and resolve multiple screen IDs by coverage |
| `09` | Audit GDSC expression orientation and create a reusable model manifest |
| `10` | Map identities and construct leakage-safe external cohorts |
| `11` | Fit PRISM gene models and evaluate their GDSC predictions |
| `12` | Fit pathway models and perform paired gene-versus-pathway comparisons |
| `13` | Run and resume the locked multi-drug extension; combine final tables |

## Reproducibility boundaries

- Keep training and external test outcomes separate.
- Learn imputation, feature selection, scaling, pathway normalization, and model parameters from PRISM training rows only.
- Never calculate feature selection scores using GDSC outcomes.
- Do not refit on GDSC before reporting external validation.
- Preserve the saved split manifest and audit tables.
- A new dataset release can change exact results; record it as a new version rather than silently replacing the original analysis.

## Expected pilot and extension checks

The original release should produce:

- 551 PRISM/DepMap training cell lines.
- 19,204 gene symbols common to DepMap and GDSC.
- 351 strict GDSC2 external models.
- 319 strict GDSC1 replication models.
- Elastic Net gene-model GDSC2 `LN_IC50` Pearson r approximately 0.590 and Spearman rho approximately 0.623.
- 50 retained Hallmark pathways based on 4,374 matched member genes.
- Zero GDSC outcomes used during training.
- All five extension drugs report `complete` with zero missing outputs under one frozen panel hash.
- Extension strict GDSC2 cohort sizes are 349, 351, 347, 352, and 348 in panel order.
- Primary Elastic Net GDSC2 pathway-minus-gene Pearson differences are approximately +0.414, +0.086, +0.284, -0.105, and +0.272.
- Across the 20 primary GDSC2 extension comparisons, eight favor pathways, six favor genes, and six are uncertain.
- Across the corresponding GDSC1 comparisons, none favors pathways.
