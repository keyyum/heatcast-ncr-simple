"""Sample inputs and what the app answers (paper Appendix D, technical documentation).

    python app/sample_inputs_outputs.py      # writes documentation/sample_inputs_outputs.csv

Every case goes through the same validate_inputs and predict_level as the page, with the saved model.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app_logic as A  # noqa: E402

OUT = A.ROOT / "documentation" / "sample_inputs_outputs.csv"
NORMAL = {"HeatIndex_Max_Today": 38.0, "Temp_Min": 26.0, "Rainfall_Total": 0.0, "Pressure_Mean": 1010.0,
          "SolarRadiation_Total": 5000.0}
CASES = [
    ("Valid", "A normal dry day", {"City": "Manila", **NORMAL}),
    ("Valid", "A very hot sunny day", {"City": "Manila", "HeatIndex_Max_Today": 45.5, "Temp_Min": 29.0, "Rainfall_Total": 0.0,
                                       "Pressure_Mean": 1008.0, "SolarRadiation_Total": 7000.0}),
    ("Valid", "A cool rainy day", {"City": "Quezon", "HeatIndex_Max_Today": 29.0, "Temp_Min": 24.0, "Rainfall_Total": 90.0,
                                   "Pressure_Mean": 1003.0, "SolarRadiation_Total": 1500.0}),
    ("Valid", "A hot day in a hot city", {"City": "Malabon", **NORMAL, "HeatIndex_Max_Today": 42.0, "Temp_Min": 27.5,
                                          "SolarRadiation_Total": 6500.0}),
    ("Boundary", "Rain exactly 0 mm (lower limit)", {"City": "Pasig", **NORMAL, "Rainfall_Total": 0.0}),
    ("Boundary", "Rain exactly 500 mm (upper limit)", {"City": "Pasig", **NORMAL, "Rainfall_Total": 500.0}),
    ("Boundary", "Heat index 55 °C (above the data maximum)", {"City": "Manila", **NORMAL, "HeatIndex_Max_Today": 55.0}),
    ("Invalid", "Rain -5 mm", {"City": "Manila", **NORMAL, "Rainfall_Total": -5.0}),
    ("Invalid", "Heat index 200 °C", {"City": "Manila", **NORMAL, "HeatIndex_Max_Today": 200.0}),
    ("Invalid", "Pressure left empty", {"City": "Manila", **NORMAL, "Pressure_Mean": None}),
    ("Invalid", "Text instead of a number", {"City": "Manila", **NORMAL, "Temp_Min": "warm"}),
    ("Invalid", "A city outside the data", {"City": "Cebu", **NORMAL}),
]


def main() -> pd.DataFrame:
    train = A.load_training_data()
    summary = A.training_summary(train)
    model, note = A.load_app_model(train)
    assert note is None, note
    rows = []
    for kind, case, raw in CASES:
        check = A.validate_inputs(raw, summary)
        if check.ok:
            p = A.predict_level(model, check.clean)
            output = f"{p.level} ({p.probabilities[p.level]:.0%})"
            message = " ".join(check.warnings) or "none"
        else:
            output = "no prediction"
            message = " ".join(check.errors)
        rows.append({"type": kind, "case": case, **{k: raw.get(k) for k in ["City", *A.WEATHER_COLUMNS]},
                     "output": output, "message": message})
    table = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False)
    return table


if __name__ == "__main__":
    print(main().to_string(index=False))
