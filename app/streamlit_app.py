"""HeatCast NCR: will tomorrow be a dangerous heat day in Metro Manila?

Run it from the project folder:   streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pydeck as pdk
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))
import app_logic as A  # noqa: E402

# On Streamlit Community Cloud a new version of the code is pulled without restarting Python, so the modules imported by an earlier
# version can stay in memory and no longer match this file (AttributeError on a new function). Re-reading them on every run prevents that.
for _name in ("make_dataset", "common", "app_logic"):
    if _name in sys.modules:
        importlib.reload(sys.modules[_name])

# The number of trees can be lowered for quick tests (HEATCAST_APP_TREES=30); the real app uses the 500 of Section 5.2.
N_TREES = int(os.environ.get("HEATCAST_APP_TREES", A.MODEL_CONFIG["n_estimators"]))

st.set_page_config(page_title="HeatCast NCR", page_icon="🌡️", layout="centered")


def code_version() -> tuple:
    """Changes whenever the code or the data file is replaced, so a new deploy trains a fresh model instead of reusing the old one."""
    files = [APP_DIR / "app_logic.py", APP_DIR.parent / "src" / "common.py", APP_DIR.parent / "src" / "make_dataset.py", A.C.DATA_FILE]
    return tuple((f.name, f.stat().st_mtime_ns, f.stat().st_size) for f in files)


@st.cache_resource(show_spinner="Training the model on the 2021 to 2024 data (a few seconds, only once)...")
def load_app(version: tuple):
    train = A.load_training_data()
    return A.build_model(train, n_estimators=N_TREES), A.training_summary(train)


model, summary = load_app(code_version())
LOCATIONS = A.load_city_locations()
SHAPES = A.load_city_shapes()


def show_map(selected=None, result=None):
    """The real outline of Metro Manila with its cities. Only the city that was asked about is coloured: blue when chosen,
    the colour of tomorrow's guessed level once the guess is made. The other cities stay grey."""
    shapes, labels = A.build_map_shapes(SHAPES, LOCATIONS, selected, result)
    cities = pdk.Layer("GeoJsonLayer", shapes, stroked=True, filled=True, pickable=True, get_fill_color="properties.fill_color",
                       get_line_color="properties.line_color", get_line_width="properties.line_width", line_width_units="'pixels'")
    names = pdk.Layer("TextLayer", labels, get_position=["cx", "cy"], get_text="label", get_size=12, character_set="'auto'",
                      get_color=[30, 30, 30], get_text_anchor="'middle'", get_alignment_baseline="'center'",
                      get_pixel_offset=["ox", "oy"],
                      background=True, get_background_color=[255, 255, 255, 190], background_padding=[3, 1])
    view = pdk.ViewState(latitude=14.575, longitude=121.03, zoom=9.7)
    st.pydeck_chart(pdk.Deck(layers=[cities, names], initial_view_state=view, map_style="light",
                             tooltip={"text": "{tooltip}"}), height=620)
    legend = "  ".join(f"{A.LEVEL_SQUARES[lv]} {lv}" for lv in ["Caution", "Extreme Caution", "Danger"])
    if result is None:
        st.caption(f"🟦 {selected} is selected. Fill in today's weather and click the button: the city will take the colour of "
                   f"tomorrow's guessed level ({legend}). The other cities stay grey.")
    else:
        st.caption(f"{legend}. Only {selected} is coloured, because the model uses the weather typed in for that city. "
                   "The grey cities are the others. Hover over a city for its name. Pateros (pale) is part of NCR but not in the data.")


# The city picker is outside the form so that the map reacts as soon as another city is chosen.
city = st.selectbox("City", summary["cities"], index=summary["cities"].index("Manila"))
map_slot = st.container()                        # the map sits here, above the form, and is filled in once the result is known

with st.form("inputs"):
    cols = st.columns(2)
    raw = {"City": city}
    for i, (col, meta) in enumerate(A.INPUTS.items()):
        _, median, _ = summary["ranges"][col]
        # The boxes start empty (value=None) so that a forgotten field is reported, never silently filled in with a default.
        raw[col] = cols[i % 2].number_input(f"{meta['label']} ({meta['unit']})", value=None, step=meta["step"], format="%.2f",
                                            placeholder=f"typical: {median:g}", help=meta["help"], key=col)
    submitted = st.form_submit_button("Guess tomorrow's level", type="primary")

check = A.validate_inputs(raw, summary) if submitted else None
for message in (check.errors if check else []):
    st.error(message)
result = None

if check and check.ok:
    for message in check.warnings:
        st.warning(message)
    result = A.predict_level(model, check.clean)
    danger_p = result.probabilities[A.DANGER]

    if result.level == A.DANGER:
        st.error(f"**Tomorrow in {city}: Danger** (heat index 42 °C or more). Consider precautions: move outdoor activities, "
                 "prepare drinking water and cooling spaces, and warn vulnerable people.")
    elif result.level == "Extreme Caution":
        st.warning(f"**Tomorrow in {city}: Extreme Caution** (heat index 33 to below 42 °C).")
    else:
        st.success(f"**Tomorrow in {city}: {result.level}.**")

    st.subheader("How sure is the model?")
    for level, p in result.probabilities.items():
        st.progress(float(p), text=f"{level}: {p:.1%}")
    st.caption(f"Today's heat index is already in **{result.today_level}**. "
               f"The model puts {danger_p:.1%} on Danger tomorrow. Extreme Danger never happened in the 2021 to 2025 data, "
               "so the model cannot predict it.")

with map_slot:
    show_map(city, result)                       # blue = chosen city; its level colour once the guess is made

with st.expander("About this model and its limits"):
    st.markdown(
        "- **Model:** Random Forest (many decision trees that vote), trained on 2021-01-01 to 2024-12-27 data for the 16 cities.\n"
        "- **It is a decision aid, not a PAGASA advisory.** The labels come from a heat index calculated from weather-model "
        "estimates (ERA5), not from station readings.\n"
        "- **It catches most Danger days but also raises false alarms.** On the 2025 test days, which it never saw while it was "
        "built, it found 293 of the 347 real Danger days (84%), but only 293 of its 816 Danger warnings (36%) were real. It did "
        "not beat the simple rule 'tomorrow = today' on overall score; it only caught more Danger days (workspace doc, "
        "Sections 5.2 and 6.4).\n"
        "- It only looks at **today's** weather, so it cannot see a storm that is still coming."
    )
st.caption("Weather data: Open-Meteo.com (CC BY 4.0), containing modified Copernicus Climate Change Service (ERA5) information. "
           "City outlines: Philippine Statistics Authority PSGC boundaries via faeldon/philippines-json-maps (MIT).")
