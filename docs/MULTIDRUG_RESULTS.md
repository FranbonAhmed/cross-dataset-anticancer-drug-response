# Multi-drug results

## Analysis roles

- **Exploratory pilot:** trametinib.
- **Prespecified extension:** gemcitabine, docetaxel, talazoparib, vorinostat, and bortezomib.

The five-drug panel and primary comparison were frozen before the extension run. Trametinib is shown for context but is not silently pooled into the extension inference.

## Prespecified primary comparison

The primary comparison was Elastic Net pathway-minus-gene Pearson correlation for GDSC `LN_IC50` in strict held-out GDSC2 cohorts using Sanger-derived expression. Each interval used 1,000 paired bootstrap resamples of the same external cell lines.

| Drug | n | Gene r | Pathway r | Difference | 95% CI | Conclusion |
|---|---:|---:|---:|---:|---:|---|
| Gemcitabine | 349 | -0.194 | 0.221 | +0.414 | [+0.294, +0.540] | Pathways favored |
| Docetaxel | 351 | 0.134 | 0.220 | +0.086 | [-0.023, +0.194] | Uncertain |
| Talazoparib | 347 | 0.086 | 0.371 | +0.284 | [+0.120, +0.442] | Pathways favored |
| Vorinostat | 352 | 0.111 | 0.006 | -0.105 | [-0.226, -0.002] | Genes favored |
| Bortezomib | 348 | -0.112 | 0.160 | +0.272 | [+0.173, +0.379] | Pathways favored |

Positive differences favor Hallmark pathway scores. Negative differences favor selected individual genes.

The per-drug intervals were not adjusted for multiple comparisons. They should be read as drug-specific uncertainty estimates, not as proof of a universal representation effect.

## Supporting GDSC1 comparison

| Drug | n | Gene r | Pathway r | Difference | 95% CI | Conclusion |
|---|---:|---:|---:|---:|---:|---|
| Gemcitabine | 335 | 0.150 | -0.010 | -0.160 | [-0.312, -0.021] | Genes favored |
| Docetaxel | 336 | 0.354 | 0.091 | -0.263 | [-0.380, -0.144] | Genes favored |
| Talazoparib | 323 | 0.228 | 0.035 | -0.193 | [-0.335, -0.043] | Genes favored |
| Vorinostat | 339 | 0.091 | -0.064 | -0.155 | [-0.264, -0.051] | Genes favored |
| Bortezomib | 191 | 0.109 | 0.242 | +0.133 | [-0.034, +0.293] | Uncertain |

The pathway advantage observed for several GDSC2 drug comparisons did not reproduce in GDSC1. Because GDSC1 and GDSC2 share many biological models, this finding is best interpreted as sensitivity to the drug-screening dataset rather than as failure in a completely independent cohort.

## Model- and metric-level pattern

Across five drugs, two models, and two correlation metrics:

| Cohort | Pathways favored | Genes favored | Uncertain | Total |
|---|---:|---:|---:|---:|
| Primary GDSC2 | 8 | 6 | 6 | 20 |
| Supporting GDSC1 | 0 | 12 | 8 | 20 |

In GDSC2, nine of ten pathway learned-model/drug combinations showed a positive external signal by at least one reported correlation interval, compared with five of ten gene combinations. This did not produce a stable cross-screen representation ranking.

## Exploratory trametinib pilot

For strict GDSC2 `LN_IC50`, the trametinib Elastic Net gene model achieved Pearson `r=0.590` and Spearman `rho=0.623`. The corresponding pathway correlations were `0.512` and `0.581`. The pathway-minus-gene Pearson difference was `-0.078` with 95% CI `[-0.144, -0.015]`, favoring individual genes.

The pilot motivated the frozen multi-drug extension but remains exploratory.

## Scientific conclusion

> Baseline expression carried transferable drug-response information, but the relative performance of selected genes and simple Hallmark pathway averages changed across drugs, models, metrics, and GDSC screens. Representation choice is therefore part of the dataset-shift problem rather than a universally settled decision.

These results do not establish patient-level prediction, causal biomarkers, or clinical utility.
