# Condensed research log

## Phase 1 — Reproducible baseline

Created a numbered Python pipeline for environment checks, synthetic-data verification, real-data inventory, drug filtering, PRISM/DepMap joining, cross-validated modeling, and saved metrics/predictions. The modeling unit was one cancer cell line; identifiers were excluded from predictors.

## Phase 2 — Trametinib internal validation

Matched 551 PRISM trametinib response records to DepMap expression. Compared a mean baseline, Elastic Net, and Random Forest using identical five-fold out-of-fold predictions. Added audits of uncertainty, residuals, response tails, and tissue-specific performance.

Random-fold Elastic Net achieved Pearson r=0.546 and Spearman rho=0.563. Under held-out-tissue folds, Elastic Net achieved Pearson r=0.458 and Spearman rho=0.472.

## Phase 3 — Internal representation comparison

Constructed training-only mean-z scores for 50 MSigDB Hallmark pathways and compared them with selected individual genes on the same internal splits. Pathway preprocessing was placed inside the validation pipeline.

## Phase 4 — GDSC data and identity audit

Filtered GDSC1 and GDSC2 fitted-dose-response tables to trametinib, audited the Sanger/Broad RNA-seq matrix, mapped DepMap ACH identifiers to Sanger SIDM identifiers, and created strict held-out cohorts. A secondary normalized-name audit found no additional overlap among the 106 training identities lacking direct Sanger mappings.

The primary strict cohort contained 351 GDSC2 models with Sanger-derived expression; GDSC1 provided a 319-model replication cohort.

## Phase 5 — External gene validation

Aligned 19,204 common gene symbols. Fitted complete gene pipelines on 551 PRISM/DepMap training rows, with 1,000-gene selection based only on PRISM outcomes, and generated GDSC predictions. GDSC outcomes were used only for evaluation.

In strict GDSC2 `LN_IC50` validation, Elastic Net achieved Pearson r=0.590 and Spearman rho=0.623. Random Forest achieved Pearson r=0.526 and Spearman rho=0.553.

## Phase 6 — External pathway comparison

Used 4,374 matched genes to construct 50 fixed Hallmark scores with PRISM-learned normalization. In primary GDSC2 testing, Elastic Net pathway Pearson r=0.512 versus 0.590 for genes. The pathway-minus-gene difference was -0.078 (95% paired-bootstrap CI -0.144 to -0.015). Across 32 paired metrics, 18 favored genes and 14 were uncertain; none significantly favored pathways.

## Phase 7 — Prespecified five-drug extension

Froze a mechanism-diverse panel containing gemcitabine, docetaxel, talazoparib, vorinostat, and bortezomib, then applied the same core gene, pathway, identity-audit, and external-validation procedures without selecting drugs by their results.

All five drugs completed successfully under the same panel hash. In the primary strict GDSC2 Elastic Net Pearson comparison, pathways were favored for gemcitabine, talazoparib, and bortezomib; genes were favored for vorinostat; and docetaxel was uncertain. GDSC1 did not reproduce the pathway advantage: four drugs favored genes and bortezomib was uncertain.

Across 20 GDSC2 extension comparisons spanning two models and two correlations, eight favored pathways, six favored genes, and six were uncertain. Across the corresponding GDSC1 comparisons, 12 favored genes, eight were uncertain, and none favored pathways. Feature audits confirmed 19,204 aligned gene symbols, 1,000 training-selected genes, 50 Hallmark pathways built from 4,374 member genes, and zero GDSC outcomes used during training.

## Current conclusion

The exploratory trametinib pathway-superiority hypothesis was not supported. The five-drug extension showed that pathway aggregation can improve some drug–dataset comparisons, but the advantage was not stable across models or GDSC screens. Representation rankings therefore appear to be part of the pharmacogenomic dataset-shift problem.

## Status

The pilot and prespecified five-drug extension are complete and frozen as version 1.0 pending expert methodological and biological review. Any secondary heterogeneity, batch-aware, or pathway-scoring analysis should be specified before it is run.
