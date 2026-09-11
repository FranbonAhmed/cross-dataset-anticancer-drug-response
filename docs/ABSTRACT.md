# Draft poster / preprint abstract

## Title

**Cross-dataset generalization of gene- and pathway-level anticancer drug-response models**

## Abstract

**Background:** Pharmacogenomic models often use high-dimensional baseline gene expression, but biologically defined pathway aggregation may improve interpretability and reduce dataset-specific noise. Whether such aggregation improves transfer across drug-screening platforms remains uncertain.

**Methods:** We trained drug-specific Elastic Net and Random Forest models using PRISM response and DepMap baseline expression. An exploratory trametinib analysis was followed by a prespecified five-drug extension comprising gemcitabine, docetaxel, talazoparib, vorinostat, and bortezomib. Gene models selected 1,000 features inside PRISM training; pathway models used 50 MSigDB Hallmark scores constructed from 4,374 matched genes. Final models were evaluated on strict held-out GDSC2 cohorts with Sanger-derived expression (347–352 cell lines per extension drug), with GDSC1 used as supporting cross-screen replication (191–339 cell lines). The primary comparison was the paired pathway-minus-gene Pearson correlation for GDSC2 `LN_IC50`, with 1,000 bootstrap resamples. GDSC outcomes were not used during training or preprocessing.

**Results:** In primary GDSC2 Elastic Net analyses, pathways were favored for gemcitabine (difference 0.414; 95% CI 0.294–0.540), talazoparib (0.284; 0.120–0.442), and bortezomib (0.272; 0.173–0.379). Genes were favored for vorinostat (-0.105; -0.226 to -0.002), while docetaxel was uncertain (0.086; -0.023 to 0.194). Across all 20 GDSC2 extension comparisons spanning two models and two correlations, eight favored pathways, six favored genes, and six were uncertain. In GDSC1, 12 comparisons favored genes and eight were uncertain; none favored pathways. The exploratory trametinib pilot favored genes for the primary Pearson comparison.

**Conclusions:** Pathway aggregation improved external performance for selected drug–model combinations but did not provide a stable advantage across drug screens. Gene-versus-pathway rankings appear sensitive to pharmacogenomic dataset shift. These preliminary cell-line results require independent methodological and biological review and do not imply patient-level utility.

## Suggested poster keywords

Pharmacogenomics; drug response; gene expression; Hallmark pathways; external validation; Elastic Net; Random Forest; dataset shift.
