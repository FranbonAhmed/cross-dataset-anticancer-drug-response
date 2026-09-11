# Prespecified multi-drug extension: exact run instructions

This update runs the five locked confirmatory drugs: gemcitabine, docetaxel,
talazoparib, vorinostat, and bortezomib. Trametinib remains the exploratory
pilot and is not pooled silently into the confirmatory panel.

## 1. Install the update

Extract the update ZIP directly into:

```text
C:\Users\PC\Documents\franbon-drug-response-research
```

Allow Windows to replace the older copies of scripts 08, 10, 11, and 12. The
ZIP also adds script 13 and the locked panel under `config`.

## 2. Confirm the corrected GDSC1 filename

This exact file must exist:

```text
C:\Users\PC\Documents\franbon-drug-response-research\data\raw\gdsc\GDSC1_fitted_dose_response_27Oct23.xlsx
```

Use the complete replacement workbook you downloaded. Do not leave `(1)` in
the final filename, and do not use the earlier truncated copy.

Also confirm that these files are present:

```text
data\raw\gdsc\GDSC2_fitted_dose_response_27Oct23.xlsx
data\raw\gdsc\rnaseq_merged_rsem_tpm_20260323.csv
data\raw\depmap\OmicsExpressionProteinCodingGenesTPMLogp1.csv
data\raw\depmap\Model.csv
data\raw\prism\primary-screen-replicate-collapsed-logfold-change.csv
data\raw\prism\primary-screen-replicate-collapsed-treatment-info.csv
data\raw\prism\primary-screen-cell-line-info.csv
data\raw\msigdb\h.all.v2026.1.Hs.symbols.gmt
```

## 3. Activate the environment

Open Anaconda Prompt and run:

```bat
conda activate pharmacogenomics
```

```bat
cd /d "C:\Users\PC\Documents\franbon-drug-response-research"
```

## 4. Check the plan without fitting models

```bat
python scripts\13_run_prespecified_multidrug_extension.py --mode full --dry-run
```

If the command lists a missing input, place that exact file and rerun the dry
check. Do not begin the full run until the missing-input list is empty.

## 5. Run the complete extension

Keep the computer plugged in and prevent sleep, then run:

```bat
python scripts\13_run_prespecified_multidrug_extension.py --mode full
```

The run may take several hours because it repeatedly fits nested Elastic Net
models, Random Forests, pathway models, and bootstrap intervals. It is safe to
stop and later rerun the same command: completed steps are detected and
skipped. Do not add `--force` unless a completed stage genuinely needs to be
recomputed.

Each stage writes a log under:

```text
results\logs\multidrug
```

## 6. Verify completion

Wait for:

```text
PRESPECIFIED MULTI-DRUG EXTENSION COMPLETED
```

Then confirm that this status table says `complete` for all five drugs:

```text
results\tables\multidrug_run_status.csv
```

The main combined result is:

```text
results\tables\multidrug_gdsc_gene_vs_pathway_external_comparison.csv
```

Also retain:

```text
results\tables\multidrug_gdsc_gene_external_metrics.csv
results\tables\multidrug_gdsc_pathway_external_metrics.csv
results\tables\multidrug_internal_gene_vs_pathway_comparison.csv
```

Do not interpret only the drugs with favorable results. The five-drug panel
was locked before modeling, so all five must be reported, including null or
negative findings.
