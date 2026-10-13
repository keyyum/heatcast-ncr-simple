# The Streamlit app (workspace Section 7)

You type **today's** weather for one of the 16 cities; the app shows the guessed level for **tomorrow** (one of the PAGASA levels) and
the probability of each level.

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py        # opens http://localhost:8501
python -m unittest tests.test_app -v      # the app's tests (about 5 seconds)
```

The first start trains the model on the training days (2021-01-01 to 2024-12-27, about 5 seconds), then keeps it in memory.

## Which model is inside

The Random Forest selected in workspace Section 6.3 (depth 12, 5 days per leaf, balanced class weights, 500 trees; Section 5.2), built with the
same `make_preprocess(scale=False)` as the notebooks. It is fitted on the **training days only**, like the model that was scored, so the test
days are still untouched. This is the model the group selected; its one check on the test days is in `notebooks/05_final_test.ipynb`. To swap in another
model, change `MODEL_CONFIG` / `build_model` in `app/app_logic.py`: the screen and the checks do not change.

## How the inputs are checked (`app/app_logic.py`)

| Situation | Example | What the app does |
|---|---|---|
| Valid | heat index 38, min temp 26, rain 0, pressure 1010, sun 5000 | shows the level and the 5 probabilities |
| Missing (box left empty) | rain empty | error naming the field, no prediction |
| Not a number / infinity | "hot", `inf` | error, no prediction |
| Impossible (outside the hard limit) | rain -5 mm, heat index 200 | error with the accepted range, no prediction |
| On a hard limit | rain 0 or 500 mm | accepted (zero rain is a value, not an empty box) |
| Possible but outside the training days' range | heat index 55 (data maximum 47.63) | prediction **and** a warning that it is less reliable |
| Unknown city | "Cebu" | error |

Hard limits: heat index 10 to 60 °C, minimum temperature 10 to 40 °C, rain 0 to 500 mm, pressure 950 to 1050 hPa, sunshine 0 to 10,000 Wh/m².
All problems are shown at once, never as a crash.

## The map

Above the form, a map shows the **real outline of Metro Manila** with the boundary of each city (`app/ncr_cities.geojson`).
* **Choosing a city** (the picker sits above the map, outside the form) highlights it in **blue** with a dark outline at once; Manila is chosen
  at the start.
* **Clicking "Guess tomorrow's level"** fills that city with the colour of its guessed level (yellow Caution, orange Extreme Caution, red Danger)
  and writes the level under its name. Hover over a city for its probabilities.
* **The other cities always stay grey.** The model only knows the weather that was typed in for the chosen city, so the app does not invent a
  level for the others. Choosing another city clears the previous result.
* **Pateros** (pale) is the 17th local government of NCR. It is not one of the 16 cities in the data, so it is only drawn, never coloured.

The outlines are the Philippine Statistics Authority PSGC (2023) administrative boundaries as published by
[faeldon/philippines-json-maps](https://github.com/faeldon/philippines-json-maps) (MIT; made from
[altcoder/philippines-psgc-shapefiles](https://github.com/altcoder/philippines-psgc-shapefiles)), at 10 % detail, merged and renamed to the names used in
the data by `app/make_ncr_map.py` (`python app/make_ncr_map.py` rebuilds the file; it needs internet). `app/city_locations.csv` has the 16 population-weighted
city points from `data/original`. The street map under the outlines needs an internet connection; the outlines do not.

## Tests (`tests/test_app.py`, 48 tests)

* **Valid**: normal input, numbers typed as text, all 16 cities, probabilities add up to 1, a very hot day is more dangerous than a cool rainy day.
* **Invalid**: missing (empty, spaces, NaN), text, infinity, impossible values, unknown city, several errors at once.
* **Boundary**: every hard limit accepted and just beyond it refused, training-range edges (no warning) and just outside (warning),
  zero rain, the PAGASA level boundaries for today's level (26.99 / 27 / 32.99 / 33 / 41.99 / 42), the extreme corners of the input space.
* **The map**: the outline file has the 16 cities plus Pateros, closed polygons inside Metro Manila, label points near each city's location, a
  plausible total area and a small size; grey with nothing chosen, blue for the chosen city before the guess, its level colour and a dark outline
  after it, the other cities unchanged; one distinct colour per level; every city can be chosen; an unknown city is refused; on the real page the
  highlight follows the picker and changes colour when the guess is made.
* **The real page** (run headless): empty page, empty form (5 errors, no prediction), one missing value named, valid input (5 probabilities),
  impossible value (error), value on the limit, unusual value (warning and prediction).

Screenshots from a real browser run are in `app/screenshots/`: `01_start`, `02_normal_day`, `03_danger_day`, `04_impossible_value`,
`05_missing_values`, `06_unusual_value` (taken with the map; the background map tiles are missing only because the test machine had no access to them).

## Putting it online (Streamlit Community Cloud)

1. Merge the app into `main` (it lives on the branch of the pull request until then).
2. At [share.streamlit.io](https://share.streamlit.io) sign in with GitHub, choose **New app**, repository `keyyum/heatcast-ncr-simple`, branch `main`,
   main file path `app/streamlit_app.py`. It installs `requirements.txt` by itself.
3. Copy the app link into workspace Section 7.

## If the live app shows an error right after an update

Streamlit Community Cloud pulls new code without restarting Python, so an old copy of a module can stay in memory (this once showed
`AttributeError ... 'load_city_locations'`). `streamlit_app.py` now re-reads its modules on every run and retrains the model when the code or data
file changes. If an error still appears after an update, open the app, then **Manage app, ⋮, Reboot app**, and wait about a minute.

## What the app does not do

It is a decision aid, not a PAGASA advisory, and it only sees today's five numbers. In the group's tests the model found about 3 in 4 real
Danger days, but only about 4 in 10 of its Danger warnings were real, and it did not beat the "copy today" rule on overall score. The
"About this model" box in the app says this too.
