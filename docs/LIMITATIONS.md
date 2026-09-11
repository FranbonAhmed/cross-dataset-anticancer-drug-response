# Limitations and responsible interpretation

## Scientific scope

- The project contains one exploratory pilot drug and five prespecified extension drugs. This remains too small a panel to generalize across all anticancer therapies or mechanism classes.
- Experiments involve immortalized or established cancer cell lines, not patients.
- Bulk RNA expression averages over cell populations and cannot describe intratumoral single-cell heterogeneity.
- Cell-line systems omit important pharmacokinetic, immune, stromal, microenvironmental, and treatment-history effects.
- Association does not establish that selected genes cause drug sensitivity.

## Cross-dataset comparability

- PRISM log-fold change and GDSC `LN_IC50`/`AUC` are different measurements. External RMSE and MAE would mix incompatible scales; correlations are therefore emphasized.
- DepMap and Sanger expression measurements can differ because of laboratory, library-preparation, sequencing, normalization, and processing effects.
- GDSC1 and GDSC2 share many cell-line identities. GDSC1 supports cross-screen replication but is not a completely independent set of biological models relative to GDSC2.
- Of 551 PRISM training models, 106 lacked a direct Sanger identifier. Normalized-name auditing found no additional GDSC matches, but unresolved mapping uncertainty remains.

## Modeling limitations

- The sample size is small relative to the number of genes.
- Univariate feature selection can miss multivariable patterns and does not identify causal biomarkers.
- Elastic Net represents additive linear effects after preprocessing.
- Random Forest can model nonlinearities but can overfit high-dimensional, modest-sample data and shrink extreme predictions through averaging.
- Mean-z Hallmark scoring assumes that averaging member-gene expression is a useful representation. It can cancel opposing signals, ignore gene directionality and interaction structure, and discard drug-specific effects.
- Hyperparameter exploration was limited to the documented grids/settings.
- Drug-specific 95% bootstrap intervals were not adjusted for multiple comparisons. Patterns across drugs should be interpreted descriptively and require replication.
- A performance-blind coverage rule resolved compounds with multiple GDSC screen identifiers. This avoids selecting by predictive performance but can still change which experimental screen defines a drug outcome.

## Interpretation rules

Appropriate overall claim:

> Baseline expression carried transferable drug-response information, but the relative performance of selected genes and simple Hallmark pathway averages depended on the drug, model, metric, and screening dataset.

Inappropriate claims include:

- “The model predicts whether a patient will respond.”
- “Pearson r=0.590 means 59% accuracy.”
- “The selected genes are trametinib biomarkers” without further validation.
- “Pathways are universally better than genes” based on selected GDSC2 comparisons.
- “Genes are universally better than pathways” based on the trametinib pilot or GDSC1 comparisons.
- “The model is clinically validated.”

## Needed next steps

1. Freeze the completed pilot and extension as version 1.0 without post-result tuning.
2. Obtain expert biological and statistical review of cross-screen heterogeneity and multiplicity.
3. Prespecify any secondary analyses before running them.
4. Evaluate stability of selected genes and pathway scores across training resamples.
5. Add batch-aware or domain-adaptation sensitivity analyses.
6. Validate findings in additional experiments and, only if justified, patient-relevant datasets.
