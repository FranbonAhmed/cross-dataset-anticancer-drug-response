# Methods

## Objective and analysis roles

This study asked whether baseline cancer cell-line expression carries a drug-response signal that transfers between pharmacogenomic platforms, and whether 50 Hallmark pathway scores transfer better than 1,000 selected individual genes.

Trametinib was analyzed first as an exploratory pilot. A five-drug extension—gemcitabine, docetaxel, talazoparib, vorinostat, and bortezomib—was frozen before the extension results were run. The prespecified primary comparison was Elastic Net pathway-minus-gene Pearson correlation for GDSC2 `LN_IC50` in strict held-out cohorts with Sanger-derived expression.

PRISM response and DepMap expression formed the training domain. GDSC response and Sanger-derived expression formed the external domain. GDSC outcomes were not used for model fitting, preprocessing, feature selection, pathway normalization, or hyperparameter selection.

## Training cohort construction

For each drug:

1. The PRISM replicate-collapsed response matrix was reshaped from treatment-by-cell-line format to one treatment–cell-line record per row.
2. Treatment metadata mapped a treatment key to the drug name.
3. Records were filtered to the exact case-insensitive requested drug name.
4. Multiple retained records for one DepMap model, if present, were averaged to one response per `depmap_id`.
5. DepMap protein-coding RNA expression was loaded with `ModelID` standardized to `depmap_id`.
6. Response and expression were inner-joined on `depmap_id`.

The predictor matrix `X` contained numeric baseline expression values. The target vector `y` contained PRISM replicate-collapsed log-fold change. Identifiers and tissue labels were used for matching and auditing, not as model predictors.

| Drug | PRISM/DepMap training rows |
|---|---:|
| Trametinib pilot | 551 |
| Gemcitabine | 532 |
| Docetaxel | 556 |
| Talazoparib | 553 |
| Vorinostat | 522 |
| Bortezomib | 552 |

## Internal validation

Random cell-line validation used five folds with shuffling and `random_state=42`. Every cell line received one out-of-fold prediction from a model that had not trained on that row.

The complete preprocessing and model pipeline was fitted separately inside each training fold:

- Median imputation.
- Univariate `f_regression` scoring.
- Selection of at most 1,000 genes.
- Standardization for Elastic Net.
- Model fitting.

This placement prevents held-out responses from influencing imputation, selection, or scaling. A stricter grouped sensitivity analysis used five `GroupKFold` splits defined by `primary_tissue`, so each test-fold tissue was absent from that fold's training rows.

## Models

### Mean baseline

`DummyRegressor` predicted the training-fold mean response. Its constant external predictions produce undefined correlations, recorded as missing values rather than as model failures.

### Elastic Net

Elastic Net fitted a linear combination of selected standardized genes while penalizing coefficient size. `ElasticNetCV` tested `l1_ratio` values `0.1`, `0.5`, `0.9`, and `1.0` and 40 alpha values from `10^-3` to `10^1`, using inner three-fold cross-validation. Maximum iterations were 50,000 with tolerance `10^-3`.

### Random Forest

The Random Forest used 300 regression trees, `max_features="sqrt"`, a minimum of three samples per terminal leaf, parallel execution, and `random_state=42`. It was preceded by the same fold-specific imputation and 1,000-gene selection.

## Pathway representation

The human MSigDB Hallmark gene-symbol collection defined pathway membership. DepMap labels such as `BRAF (673)` were reduced to uppercase gene symbols. Pathways required at least ten matched genes.

Within training data, the pathway transformer:

1. Estimated per-gene medians and imputed missing values.
2. Estimated per-gene means and standard deviations.
3. Converted expression to z-scores using stored training parameters.
4. Averaged member-gene z-scores into one value per pathway.

Every drug analysis used 50 Hallmark scores constructed from 4,374 unique member genes shared with the aligned expression matrix. Training-derived medians, means, and standard deviations were applied unchanged to external GDSC expression.

## GDSC response-screen resolution

GDSC1 and GDSC2 workbooks were filtered to the requested drug name. When one name corresponded to multiple `DRUG_ID` values, the pipeline selected the screen with the greatest number of unique Sanger models. Ties were resolved using nonmissing outcomes, then row count, then lexical `DRUG_ID`. This rule did not inspect model performance.

The response key was `dataset + SANGER_MODEL_ID`. `LN_IC50` was the primary external outcome and `AUC` was secondary.

## External-cohort construction

The Cell Model Passports RNA-seq matrix was transposed so one row represented one Sanger model and one column represented one gene. Response and expression were joined on `SANGER_MODEL_ID`.

DepMap `Model.csv` mapped PRISM/DepMap `ModelID` values to `SangerModelID`. Directly mapped training identities were excluded. Training identities without a Sanger mapping were also audited using normalized cell-line names.

The primary strict cohort required:

- GDSC2 response.
- A valid expression profile.
- No mapped identity seen in PRISM training.
- Sanger-derived expression.

The parallel GDSC1 strict cohort was used as supporting cross-screen replication. GDSC1 and GDSC2 share biological models, so they are not treated as fully independent cell-line cohorts.

| Drug | Strict GDSC2 n | Strict GDSC1 n |
|---|---:|---:|
| Trametinib pilot | 351 | 319 |
| Gemcitabine | 349 | 335 |
| Docetaxel | 351 | 336 |
| Talazoparib | 347 | 323 |
| Vorinostat | 352 | 339 |
| Bortezomib | 348 | 191 |

## Cross-platform gene alignment

DepMap and GDSC feature names were reduced to gene symbols. Duplicate GDSC rows for an overlapping symbol were averaged. Every analysis used 19,204 common symbols in the same order in training and external matrices.

For gene models, the entire preprocessing pipeline was refit on the drug-specific PRISM cohort and selected 1,000 genes using PRISM outcomes only. For pathway models, pathway preprocessing and model parameters were learned from the same drug-specific PRISM cohort. Final fitted pipelines generated GDSC predictions without refitting on GDSC outcomes.

## Evaluation and uncertainty

Internal validation used Pearson correlation, Spearman rank correlation, root mean squared error, and mean absolute error because predictions and outcomes shared the PRISM scale.

External validation used Pearson and Spearman correlations. Cross-platform RMSE and MAE were not interpreted because PRISM log-fold change, GDSC `LN_IC50`, and GDSC `AUC` are different response quantities with different scales.

Nonparametric bootstrap sampling with replacement over external cell lines generated 95% intervals for correlations. Paired bootstrap intervals compared pathway and gene correlations on identical rows. One thousand successful resamples were targeted per learned-model comparison. The reported per-drug intervals were not adjusted for multiple comparisons.

## Reproducibility controls

- The extension panel and analysis role were recorded before the extension run.
- Identical mapped training models were excluded from strict external cohorts.
- GDSC outcomes used during training were audited as zero for every gene and pathway analysis.
- Preprocessing and feature construction were fitted only on PRISM training rows.
- Gene and pathway models were evaluated on identical external rows.
- Random seeds were fixed where supported.
- All five extension drugs, including null or unfavorable comparisons, were retained in aggregate reports.
- Split, feature, inventory, and screen-selection audits were saved with the derived results.
