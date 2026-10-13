"""The logic behind the Streamlit app (no screen code here, so it can be tested without a browser).

    check the inputs   ->   validate_inputs(raw, ranges)    (missing / not a number / impossible / unusual)
    train the model    ->   build_model(train)              (the Random Forest of workspace Section 5.2, fitted on the training days)
    guess tomorrow     ->   predict_level(model, clean)     (level + probability of every level)

The model is the one proposed in workspace Section 6.3 (Random Forest: depth 12, 5 days per leaf, balanced class weights,
500 trees). It is fitted here on the TRAINING days only, exactly like the model that was scored in Section 5.2, so the
untouched test days stay untouched until the group has run final_test(). To switch to another model, change MODEL_CONFIG
(or build_model) and nothing else in the app needs to change.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import common as C  # noqa: E402  (shared split and preprocessing, so the app uses the same steps as the notebooks)
from make_dataset import LEVELS, WEATHER_COLUMNS, to_level  # noqa: E402

MODEL_CONFIG = dict(n_estimators=500, max_depth=12, min_samples_leaf=5, class_weight="balanced",
                    random_state=C.RANDOM_STATE, n_jobs=-1)

# What each input is, in plain words, and the limits of what the app will accept.
#   hard limit : outside it the value is impossible or a typing mistake -> the app refuses to predict
#   data range : the range of the training days; outside it the model is guessing beyond what it has seen -> the app warns
INPUTS = {
    "HeatIndex_Max_Today": dict(label="Today's highest heat index", unit="°C", hard=(10.0, 60.0), step=0.1,
                                help="The highest 'feels-like' temperature of today in that city."),
    "Temp_Min": dict(label="Today's lowest temperature", unit="°C", hard=(10.0, 40.0), step=0.1,
                     help="Roughly how warm last night was."),
    "Rainfall_Total": dict(label="Rain today", unit="mm", hard=(0.0, 500.0), step=0.1,
                           help="Total rain during the day. 0 means a dry day."),
    "Pressure_Mean": dict(label="Average air pressure today", unit="hPa", hard=(950.0, 1050.0), step=0.1,
                          help="Average pressure at sea level. Low values go with storms."),
    "SolarRadiation_Total": dict(label="Sunshine today", unit="Wh/m²", hard=(0.0, 10000.0), step=10.0,
                                 help="Total sunshine energy received during the day."),
}
assert list(INPUTS) == WEATHER_COLUMNS

DANGER = C.DANGER

# ----------------------------------------------------------------------------------------------------------------------
# The map (one dot per city; the city that was asked about is coloured by its guessed level for tomorrow)
# ----------------------------------------------------------------------------------------------------------------------
LOCATIONS_FILE = Path(__file__).resolve().parent / "city_locations.csv"      # City, Latitude, Longitude (from data/original)
SHAPES_FILE = Path(__file__).resolve().parent / "ncr_cities.geojson"         # outlines of the 16 cities + Pateros (app/make_ncr_map.py)
LEVEL_COLORS = {                     # RGB, close to the usual heat-warning colours
    "Not Hazardous": (46, 160, 67),
    "Caution": (240, 200, 0),
    "Extreme Caution": (240, 130, 20),
    "Danger": (215, 30, 30),
    "Extreme Danger": (110, 0, 0),
}
LEVEL_SQUARES = {"Not Hazardous": "🟩", "Caution": "🟨", "Extreme Caution": "🟧", "Danger": "🟥", "Extreme Danger": "🟫"}
NEUTRAL_COLOR = (170, 170, 170)
OUTSIDE_COLOR = (225, 225, 225)       # Pateros: part of NCR, but not one of the 16 cities of the data
LINE_COLOR = (255, 255, 255)          # outline between cities
SELECTED_LINE_COLOR = (20, 20, 20)    # outline of the chosen city
LABEL_OFFSETS = {"Navotas": (-30, 16), "Pasig": (24, 8)}  # (pixels right, pixels down) for names that would sit on top of a neighbour's name
HIGHLIGHT_COLOR = (35, 105, 225)      # the chosen city before its level is guessed (blue is not used by any level)


def load_training_data() -> pd.DataFrame:
    """The training days (2021-01-01 to 2024-12-27). The test days are not loaded into the app."""
    train, _ = C.split_train_test(C.load_data())
    return train


def training_summary(train: pd.DataFrame) -> dict:
    """What the app needs from the data: the city list, the min / median / max of each input."""
    cols = {c: (float(train[c].min()), float(train[c].median()), float(train[c].max())) for c in WEATHER_COLUMNS}
    return {"cities": sorted(train["City"].unique()), "ranges": cols}


def build_model(train: pd.DataFrame, **overrides):
    """Same pipeline as notebooks/03_random_forest.ipynb: make_preprocess(scale=False) + Random Forest, fitted on the training days."""
    rf = RandomForestClassifier(**{**MODEL_CONFIG, **overrides})
    return make_pipeline(C.make_preprocess(scale=False), rf).fit(train[C.FEATURES], train[C.TARGET])


# ----------------------------------------------------------------------------------------------------------------------
# Checking the inputs
# ----------------------------------------------------------------------------------------------------------------------
@dataclass
class Validation:
    clean: dict | None                      # the checked values (floats + City), or None if there is any error
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _to_number(value):
    """A float, or None when the value is missing, or a string describing the problem."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "not a number"
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
        try:
            value = float(value)
        except ValueError:
            return "not a number"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "not a number"
    if math.isnan(value):
        return None                         # an empty number box can arrive as NaN
    if math.isinf(value):
        return "not a finite number"
    return value


def validate_inputs(raw: dict, summary: dict) -> Validation:
    """Check one set of inputs. Never raises: every problem becomes a message the user can read.

    * missing value, text instead of a number, infinity            -> error (no prediction)
    * outside the hard limit (impossible, e.g. rain -5 mm)          -> error (no prediction)
    * a limit value itself (e.g. rain 0 mm or 500 mm)               -> accepted
    * inside the limits but outside the training days' range        -> warning (prediction shown, with the warning)
    * unknown city                                                  -> error
    """
    errors, warnings, clean = [], [], {}
    city = raw.get("City")
    if city not in summary["cities"]:
        errors.append("Choose one of the 16 cities.")
    else:
        clean["City"] = city

    for col, meta in INPUTS.items():
        name, unit = meta["label"], meta["unit"]
        value = _to_number(raw.get(col))
        if value is None:
            errors.append(f"{name}: please enter a value.")
            continue
        if isinstance(value, str):
            errors.append(f"{name}: {value}. Enter a number in {unit}.")
            continue
        lo, hi = meta["hard"]
        if not lo <= value <= hi:
            errors.append(f"{name}: {value:g} {unit} is not possible here. Accepted values are {lo:g} to {hi:g} {unit}.")
            continue
        clean[col] = value
        dmin, _, dmax = summary["ranges"][col]
        if not dmin <= value <= dmax:
            warnings.append(f"{name}: {value:g} {unit} is outside the {dmin:g} to {dmax:g} {unit} seen in the 2021 to 2024 "
                            f"training days, so the guess is less reliable.")
    return Validation(clean if not errors else None, errors, warnings)


# ----------------------------------------------------------------------------------------------------------------------
# Guessing tomorrow
# ----------------------------------------------------------------------------------------------------------------------
@dataclass
class Prediction:
    level: str                              # the most probable level for tomorrow
    probabilities: pd.Series                # probability of each of the 5 levels (a level the model never saw has 0)
    today_level: str                        # the level today's heat index is already in (the "copy today" guess)


def predict_level(model, clean: dict) -> Prediction:
    X = pd.DataFrame([clean])[C.FEATURES]
    proba = pd.Series(model.predict_proba(X)[0], index=model.classes_).reindex(LEVELS).fillna(0.0)
    return Prediction(level=str(proba.idxmax()), probabilities=proba,
                      today_level=str(to_level(pd.Series([clean["HeatIndex_Max_Today"]])).iloc[0]))


def load_city_locations() -> pd.DataFrame:
    return pd.read_csv(LOCATIONS_FILE)


def load_city_shapes() -> dict:
    """GeoJSON FeatureCollection with the outline of every NCR city (properties: City, cx, cy = middle point for the label, in_data)."""
    return json.loads(SHAPES_FILE.read_text(encoding="utf-8"))


def build_map_data(locations: pd.DataFrame, selected: str | None = None, prediction: Prediction | None = None) -> pd.DataFrame:
    """One row per city for the map. Three states:
      * nothing chosen                -> every city is grey
      * a city chosen, no guess yet   -> that city is highlighted in blue, the others stay grey
      * a city chosen and guessed     -> that city has the colour of its guessed level, the others stay grey
    (Only the chosen city is ever coloured: the model only knows the weather that was typed in for that city.)
    Columns: City, Latitude, Longitude, color (R, G, B), selected (bool), label (name on the map), tooltip (hover text)."""
    df = locations.copy()
    df["color"] = [list(NEUTRAL_COLOR)] * len(df)
    df["selected"] = False
    df["label"] = df["City"]
    df["tooltip"] = df["City"]
    if selected is None:
        return df
    if selected not in set(df["City"]):
        raise ValueError(f"unknown city {selected!r}")
    i = df.index[df["City"] == selected][0]
    df.at[i, "selected"] = True
    if prediction is None:
        df.at[i, "color"] = list(HIGHLIGHT_COLOR)
        df.at[i, "tooltip"] = f"{selected} (selected)"
    else:
        top = prediction.probabilities.sort_values(ascending=False)
        top = top[top >= 0.005]
        df.at[i, "color"] = list(LEVEL_COLORS[prediction.level])
        df.at[i, "label"] = f"{selected}\n{prediction.level}"
        df.at[i, "tooltip"] = f"{selected}: tomorrow {prediction.level} ({', '.join(f'{k} {v:.0%}' for k, v in top.items())})"
    return df


def build_map_shapes(shapes: dict, locations: pd.DataFrame, selected: str | None = None,
                     prediction: Prediction | None = None) -> tuple[dict, pd.DataFrame]:
    """The map layers: a copy of the NCR outlines with the colour, outline and hover text of every city in its properties
    (fill_color is RGBA), and a table of name labels (one per city at the middle of its outline)."""
    table = build_map_data(locations, selected, prediction).set_index("City")
    features, labels = [], []
    for f in shapes["features"]:
        props = dict(f["properties"])
        city = props["City"]
        if city in table.index:
            row = table.loc[city]
            props.update(fill_color=[*row["color"], 235 if row["selected"] else 215],
                         line_color=list(SELECTED_LINE_COLOR if row["selected"] else LINE_COLOR),
                         line_width=4 if row["selected"] else 1, tooltip=row["tooltip"], label=row["label"])
            ox, oy = LABEL_OFFSETS.get(city, (0, 0))
            labels.append({"label": row["label"], "cx": props["cx"], "cy": props["cy"], "ox": ox, "oy": oy,
                           "selected": bool(row["selected"])})
        else:                                               # Pateros: on the map, but not in the data
            props.update(fill_color=[*OUTSIDE_COLOR, 200], line_color=list(LINE_COLOR), line_width=1,
                         tooltip=f"{city} (part of NCR, not one of the 16 cities in the data)", label="")
        features.append({"type": "Feature", "geometry": f["geometry"], "properties": props})
    return {"type": "FeatureCollection", "features": features}, pd.DataFrame(labels)
