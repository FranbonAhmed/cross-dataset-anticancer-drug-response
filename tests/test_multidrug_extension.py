from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def load_script(filename: str, module_name: str):
    path = ROOT / "scripts" / filename
    specification = spec_from_file_location(module_name, path)
    assert specification is not None and specification.loader is not None
    module = module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_primary_gdsc_screen_is_chosen_by_coverage_only():
    module = load_script("08_prepare_gdsc_response.py", "prepare_gdsc_response")
    selected = pd.DataFrame(
        {
            "source_dataset": ["GDSC2"] * 5,
            "DRUG_ID": [100, 100, 100, 200, 200],
            "SANGER_MODEL_ID": ["SIDM1", "SIDM2", "SIDM3", "SIDM1", "SIDM2"],
            "CELL_LINE_NAME": ["A", "B", "C", "A", "B"],
            # The smaller screen has deliberately stronger-looking values.
            "LN_IC50": [1.0, 2.0, 3.0, -50.0, 50.0],
            "AUC": [0.2, 0.3, 0.4, 0.0, 1.0],
        }
    )

    chosen, audit = module.choose_primary_screen(selected, "GDSC2")

    assert chosen["DRUG_ID"].unique().tolist() == [100]
    assert audit["selected_primary_drug_id"] == 100
    assert audit["rows_excluded_from_nonprimary_drug_ids"] == 2


def test_within_screen_duplicate_outcomes_are_averaged():
    module = load_script("08_prepare_gdsc_response.py", "prepare_gdsc_response_dups")
    selected = pd.DataFrame(
        {
            "source_dataset": ["GDSC1", "GDSC1", "GDSC1"],
            "DRUG_ID": [10, 10, 10],
            "SANGER_MODEL_ID": ["SIDM1", "SIDM1", "SIDM2"],
            "CELL_LINE_NAME": ["A", "A", "B"],
            "LN_IC50": [1.0, 3.0, 4.0],
            "AUC": [0.2, 0.4, 0.8],
        }
    )

    collapsed, duplicate_rows = module.collapse_within_screen_duplicates(
        selected, "GDSC1"
    )
    row = collapsed.loc[collapsed["SANGER_MODEL_ID"].eq("SIDM1")].iloc[0]

    assert duplicate_rows == 2
    assert len(collapsed) == 2
    assert row["LN_IC50"] == 2.0
    assert np.isclose(row["AUC"], 0.3)
    assert row["SOURCE_ROW_COUNT"] == 2


def test_default_panel_is_confirmatory_and_preserves_order():
    module = load_script(
        "13_run_prespecified_multidrug_extension.py", "multidrug_runner"
    )
    panel = module.read_panel(
        ROOT / "config/prespecified_multidrug_panel.csv", include_pilot=False
    )

    assert panel["drug_name"].tolist() == [
        "gemcitabine",
        "docetaxel",
        "talazoparib",
        "vorinostat",
        "bortezomib",
    ]
    assert panel["study_role"].eq("Confirmatory extension").all()


def test_multidrug_manifests_are_drug_specific():
    module = load_script(
        "13_run_prespecified_multidrug_extension.py", "multidrug_runner_outputs"
    )
    outputs = module.expected_outputs(ROOT, "gemcitabine", "10")
    names = {path.name for path in outputs}

    assert "gemcitabine_gdsc_external_validation_split_manifest.csv" in names
    assert "gdsc_external_validation_split_manifest.csv" not in names
