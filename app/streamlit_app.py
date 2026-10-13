"""HeatCast NCR: will tomorrow be a dangerous heat day in Metro Manila?

Run it from the project folder:   streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app_logic as A  # noqa: E402

# The number of trees can be lowered for quick tests (HEATCAST_APP_TREES=30); the real app uses the 500 of Section 5.2.
N_TREES = int(os.environ.get("HEATCAST_APP_TREES", A.MODEL_CONFIG["n_estimators"]))

st.set_page_config(page_title="HeatCast NCR", page_icon="🌡️", layout="centered")


@st.cache_resource(show_spinner="Training the model on the 2021 to 2024 data (a few seconds, only once)...")
def load_app():
    train = A.load_training_data()
    return A.build_model(train, n_estimators=N_TREES), A.training_summary(train)


model, summary = load_app()

st.title("HeatCast NCR")
st.write("Enter **today's** weather for a city in Metro Manila. The app guesses how hot tomorrow will **feel**, "
         "as one of the official PAGASA heat levels. All five boxes are needed; the grey hint shows a typical value.")

with st.form("inputs"):
    city = st.selectbox("City", summary["cities"], index=summary["cities"].index("Manila"))
    cols = st.columns(2)
    raw = {"City": city}
    for i, (col, meta) in enumerate(A.INPUTS.items()):
        _, median, _ = summary["ranges"][col]
        # The boxes start empty (value=None) so that a forgotten field is reported, never silently filled in with a default.
        raw[col] = cols[i % 2].number_input(f"{meta['label']} ({meta['unit']})", value=None, step=meta["step"], format="%.2f",
                                            placeholder=f"typical: {median:g}", help=meta["help"], key=col)
    submitted = st.form_submit_button("Guess tomorrow's level", type="primary")

if submitted:
    check = A.validate_inputs(raw, summary)
    for message in check.errors:
        st.error(message)
    if check.ok:
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

with st.expander("About this model and its limits"):
    st.markdown(
        "- **Model:** Random Forest (many decision trees that vote), trained on 2021-01-01 to 2024-12-27 data for the 16 cities.\n"
        "- **It is a decision aid, not a PAGASA advisory.** The labels come from a heat index calculated from weather-model "
        "estimates (ERA5), not from station readings.\n"
        "- **It catches most Danger days but also raises false alarms.** In the group's tests it found about 3 in 4 real Danger "
        "days, and about 4 in 10 of its Danger warnings were real. It did not beat the simple rule 'tomorrow = today' on overall "
        "score; it only caught more Danger days (workspace doc, Section 5.2).\n"
        "- It only looks at **today's** weather, so it cannot see a storm that is still coming."
    )
st.caption("Weather data: Open-Meteo.com (CC BY 4.0), containing modified Copernicus Climate Change Service (ERA5) information.")
