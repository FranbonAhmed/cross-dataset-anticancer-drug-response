# Publish the completed version 1.0 update

Repository:

```text
https://github.com/FranbonAhmed/trametinib-cross-dataset-drug-response
```

This package updates the existing repository from the trametinib pilot to the completed pilot plus prespecified five-drug extension.

## Recommended: Git command line

1. Extract the package on your computer.
2. Open a terminal inside the extracted `trametinib-cross-dataset-drug-response` folder.
3. Confirm that `README.md`, `docs`, `results`, `scripts`, `src`, and `tests` are at that folder's root.
4. Run:

```bash
git status
git add README.md CITATION.cff REPRODUCE.md MULTIDRUG_RUN_INSTRUCTIONS.md UPLOAD_TO_GITHUB.md config docs results scripts src tests environment.yml requirements.txt .gitignore LICENSE
git status
git commit -m "Complete prespecified five-drug external-validation extension"
git push origin main
```

If your local folder is not yet connected to GitHub, run this once before the push:

```bash
git init
git branch -M main
git remote add origin https://github.com/FranbonAhmed/trametinib-cross-dataset-drug-response.git
```

Do not use `git push --force`.

## Website-only alternative

GitHub's browser uploader may not reliably replace nested folders. If it is your only option:

1. Open the repository.
2. Select **Add file → Upload files**.
3. Drag the **contents inside** the extracted project folder, not the outer folder itself.
4. Confirm that `README.md` is at the repository root.
5. Commit with `Complete prespecified five-drug external-validation extension`.

If the browser refuses the folder tree, use the command-line method instead of manually flattening folders.

## Public-page checks

- The README title is **Cross-dataset anticancer drug-response modeling**.
- The forest plot is visible in the README.
- `docs/MULTIDRUG_RESULTS.md` and `docs/ABSTRACT.md` open correctly.
- `results/tables/multidrug_run_status.csv` reports all five drugs as `complete`.
- `pytest -q` passes locally.
- No `data/raw` directory, source workbooks, row-level provider outcomes, tokens, email screenshots, CVs, or application materials are present.
- The About section links to the README and uses topics such as `bioinformatics`, `pharmacogenomics`, `machine-learning`, `cancer`, `external-validation`, and `dataset-shift`.

## Create the stable release

After the updated repository renders correctly:

1. Open **Releases → Draft a new release**.
2. Create tag `v1.0.0`.
3. Use title `Prespecified five-drug cross-dataset extension`.
4. Use this release note:

> Completed a prespecified five-drug extension of the exploratory trametinib analysis. The release includes strict GDSC2 external validation, supporting GDSC1 cross-screen replication, gene-versus-Hallmark comparisons, aggregate quality-control audits, and reproducibility tests. Results are preliminary, non-peer-reviewed cell-line research and do not imply clinical utility.

5. Publish the release.
