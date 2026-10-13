"""Tests for the Streamlit app (workspace Section 7): valid, invalid and boundary inputs.
Run from the project folder:  python -m unittest tests.test_app -v      (about 1 minute; needs `pip install streamlit`)
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
os.environ["HEATCAST_APP_TREES"] = "20"        # a small forest keeps the tests quick; the logic is the same

import app_logic as A  # noqa: E402

VALID = {"City": "Manila", "HeatIndex_Max_Today": 38.0, "Temp_Min": 26.0, "Rainfall_Total": 0.0,
         "Pressure_Mean": 1010.0, "SolarRadiation_Total": 5000.0}


class Inputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = A.load_training_data()
        cls.summary = A.training_summary(cls.train)

    def check(self, **change):
        return A.validate_inputs({**VALID, **change}, self.summary)

    # ---- valid
    def test_valid_input_is_accepted(self):
        v = self.check()
        self.assertTrue(v.ok)
        self.assertEqual(v.warnings, [])
        self.assertEqual(v.clean["HeatIndex_Max_Today"], 38.0)

    def test_numbers_typed_as_text_are_accepted(self):
        v = self.check(HeatIndex_Max_Today=" 38.5 ", Rainfall_Total="0")
        self.assertTrue(v.ok)
        self.assertEqual(v.clean["HeatIndex_Max_Today"], 38.5)

    def test_every_city_is_accepted(self):
        self.assertEqual(len(self.summary["cities"]), 16)
        for city in self.summary["cities"]:
            self.assertTrue(self.check(City=city).ok, city)

    # ---- invalid
    def test_missing_values_are_errors(self):
        for missing in (None, "", "   ", float("nan")):
            v = self.check(Temp_Min=missing)
            self.assertFalse(v.ok, repr(missing))
            self.assertIsNone(v.clean)
            self.assertIn("please enter a value", v.errors[0])

    def test_text_and_infinity_are_errors(self):
        for bad in ("hot", "12,5", True, float("inf"), float("-inf"), [1]):
            v = self.check(Pressure_Mean=bad)
            self.assertFalse(v.ok, repr(bad))
            self.assertIn("Average air pressure", v.errors[0])

    def test_impossible_values_are_errors(self):
        for col, value in [("Rainfall_Total", -5), ("HeatIndex_Max_Today", 200), ("HeatIndex_Max_Today", -3),
                           ("Pressure_Mean", 0), ("SolarRadiation_Total", 50000), ("Temp_Min", 99)]:
            v = self.check(**{col: value})
            self.assertFalse(v.ok, (col, value))
            self.assertIn("is not possible", v.errors[0])

    def test_unknown_city_is_an_error(self):
        for city in ("Cebu", "", None, "manila"):
            self.assertFalse(self.check(City=city).ok, repr(city))

    def test_every_problem_is_reported_at_once(self):
        v = A.validate_inputs({"City": "Cebu", "HeatIndex_Max_Today": None, "Temp_Min": "x", "Rainfall_Total": -1,
                               "Pressure_Mean": 1010, "SolarRadiation_Total": 5000}, self.summary)
        self.assertEqual(len(v.errors), 4)

    # ---- boundary
    def test_hard_limits_themselves_are_accepted_and_just_beyond_is_refused(self):
        for col, meta in A.INPUTS.items():
            lo, hi = meta["hard"]
            for inside in (lo, hi):
                self.assertTrue(self.check(**{col: inside}).ok, (col, inside))
            for outside in (lo - 0.01, hi + 0.01):
                self.assertFalse(self.check(**{col: outside}).ok, (col, outside))

    def test_training_range_edges_do_not_warn_but_just_outside_does(self):
        for col in A.INPUTS:
            dmin, _, dmax = self.summary["ranges"][col]
            self.assertEqual(self.check(**{col: dmin}).warnings, [], col)
            self.assertEqual(self.check(**{col: dmax}).warnings, [], col)
            beyond = self.check(**{col: dmax + 0.5})
            self.assertTrue(beyond.ok, col)                  # still possible, so still predicted ...
            self.assertEqual(len(beyond.warnings), 1, col)   # ... but with a warning

    def test_unusual_but_possible_value_warns_and_still_predicts(self):
        v = self.check(HeatIndex_Max_Today=55.0)            # possible, but the data's highest is 47.63
        self.assertTrue(v.ok)
        self.assertEqual(len(v.warnings), 1)
        self.assertIsNotNone(v.clean)

    def test_zero_rain_is_a_value_not_a_missing_entry(self):
        self.assertTrue(self.check(Rainfall_Total=0).ok)
        self.assertTrue(self.check(Rainfall_Total=0.0).ok)


class Prediction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = A.load_training_data()
        cls.summary = A.training_summary(cls.train)
        cls.model = A.build_model(cls.train, n_estimators=20)

    def test_probabilities_cover_the_five_levels_and_add_up_to_one(self):
        p = A.predict_level(self.model, A.validate_inputs(VALID, self.summary).clean)
        self.assertEqual(list(p.probabilities.index), A.LEVELS)
        self.assertAlmostEqual(float(p.probabilities.sum()), 1.0, places=6)
        self.assertEqual(p.probabilities["Extreme Danger"], 0.0)       # never happens in the data
        self.assertEqual(p.level, p.probabilities.idxmax())

    def test_a_very_hot_day_is_more_dangerous_than_a_cool_rainy_day(self):
        hot = {**VALID, "HeatIndex_Max_Today": 46.0, "Temp_Min": 29.0, "SolarRadiation_Total": 7000.0}
        cool = {**VALID, "HeatIndex_Max_Today": 29.0, "Temp_Min": 24.0, "Rainfall_Total": 90.0, "Pressure_Mean": 1003.0,
                "SolarRadiation_Total": 1500.0}
        ph = A.predict_level(self.model, A.validate_inputs(hot, self.summary).clean)
        pc = A.predict_level(self.model, A.validate_inputs(cool, self.summary).clean)
        self.assertGreater(ph.probabilities["Danger"], pc.probabilities["Danger"])

    def test_today_level_follows_the_pagasa_boundaries(self):
        for heat_index, level in [(26.99, "Not Hazardous"), (27.0, "Caution"), (32.99, "Caution"), (33.0, "Extreme Caution"),
                                  (41.99, "Extreme Caution"), (42.0, "Danger"), (47.63, "Danger")]:
            p = A.predict_level(self.model, A.validate_inputs({**VALID, "HeatIndex_Max_Today": heat_index}, self.summary).clean)
            self.assertEqual(p.today_level, level, heat_index)

    def test_every_city_and_the_hard_limit_corners_give_a_prediction(self):
        for city in self.summary["cities"]:
            p = A.predict_level(self.model, A.validate_inputs({**VALID, "City": city}, self.summary).clean)
            self.assertIn(p.level, A.LEVELS)
        for col, meta in A.INPUTS.items():
            for edge in meta["hard"]:
                v = A.validate_inputs({**VALID, col: edge}, self.summary)
                p = A.predict_level(self.model, v.clean)
                self.assertTrue(np.isfinite(p.probabilities.to_numpy()).all(), (col, edge))

    def test_the_app_model_uses_the_training_days_only(self):
        self.assertEqual(str(self.train["Date"].max().date()), "2024-12-27")
        self.assertEqual(len(self.train), 23312)


class MapData(unittest.TestCase):
    """The map: where the 16 cities are, and how the chosen city is coloured."""

    @classmethod
    def setUpClass(cls):
        cls.locations = A.load_city_locations()
        cls.summary = A.training_summary(A.load_training_data())
        cls.model = A.build_model(A.load_training_data(), n_estimators=20)

    def prediction(self, **change):
        return A.predict_level(self.model, A.validate_inputs({**VALID, **change}, self.summary).clean)

    def test_locations_cover_exactly_the_16_cities_of_the_data(self):
        self.assertEqual(sorted(self.locations["City"]), self.summary["cities"])
        self.assertTrue(self.locations["City"].is_unique)

    def test_locations_are_inside_metro_manila_and_match_the_original_file(self):
        import pandas as pd
        self.assertTrue(self.locations["Latitude"].between(14.3, 14.8).all())
        self.assertTrue(self.locations["Longitude"].between(120.9, 121.2).all())
        original = pd.read_csv(ROOT / "data" / "original" / "ph_heat_index_next_day_16cities.csv",
                               usecols=["City", "Latitude", "Longitude"]).drop_duplicates().set_index("City")
        for _, row in self.locations.iterrows():
            self.assertAlmostEqual(row["Latitude"], original.loc[row["City"], "Latitude"], places=5, msg=row["City"])
            self.assertAlmostEqual(row["Longitude"], original.loc[row["City"], "Longitude"], places=5, msg=row["City"])

    def test_before_a_guess_every_city_is_a_small_grey_dot(self):
        m = A.build_map_data(self.locations)
        self.assertEqual(len(m), 16)
        self.assertTrue(all(tuple(c) == A.NEUTRAL_COLOR for c in m["color"]))
        self.assertFalse(m["selected"].any())
        self.assertEqual(list(m["label"]), list(m["City"]))

    def test_choosing_a_city_highlights_it_in_blue_before_any_guess(self):
        m = A.build_map_data(self.locations, "Manila").set_index("City")
        self.assertEqual(tuple(m.loc["Manila", "color"]), A.HIGHLIGHT_COLOR)
        self.assertNotIn(A.HIGHLIGHT_COLOR, A.LEVEL_COLORS.values())        # blue never means a level
        self.assertTrue(m.loc["Manila", "selected"] and not m.drop("Manila")["selected"].any())
        self.assertTrue(all(tuple(c) == A.NEUTRAL_COLOR for c in m.drop("Manila")["color"]))
        self.assertIn("selected", m.loc["Manila", "tooltip"])

    def test_the_guess_changes_the_colour_of_the_chosen_city_only(self):
        before = A.build_map_data(self.locations, "Pasig").set_index("City")
        after = A.build_map_data(self.locations, "Pasig", self.prediction()).set_index("City")
        self.assertNotEqual(list(before.loc["Pasig", "color"]), list(after.loc["Pasig", "color"]))
        for city in before.index.drop("Pasig"):                              # the other 15 are identical before and after
            self.assertEqual(list(before.loc[city, "color"]), list(after.loc[city, "color"]))
            self.assertEqual(before.loc[city, "selected"], after.loc[city, "selected"])

    def test_after_a_guess_only_the_chosen_city_is_coloured_and_bigger(self):
        p = self.prediction()
        m = A.build_map_data(self.locations, "Manila", p).set_index("City")
        self.assertEqual(tuple(m.loc["Manila", "color"]), A.LEVEL_COLORS[p.level])
        self.assertTrue(m.loc["Manila", "selected"] and not m.drop("Manila")["selected"].any())
        self.assertTrue(all(tuple(c) == A.NEUTRAL_COLOR for c in m.drop("Manila")["color"]))
        self.assertIn(p.level, m.loc["Manila", "label"])
        self.assertIn("Manila", m.loc["Manila", "tooltip"])

    def test_every_level_has_a_valid_distinct_colour(self):
        self.assertEqual(set(A.LEVEL_COLORS), set(A.LEVELS))
        self.assertEqual(len(set(A.LEVEL_COLORS.values())), 5)
        for rgb in A.LEVEL_COLORS.values():
            self.assertTrue(len(rgb) == 3 and all(0 <= v <= 255 for v in rgb))

    def test_the_colour_follows_the_guessed_level(self):
        hot = self.prediction(HeatIndex_Max_Today=46.0, Temp_Min=29.0, SolarRadiation_Total=7000.0)
        cool = self.prediction(HeatIndex_Max_Today=29.0, Temp_Min=24.0, Rainfall_Total=90.0, Pressure_Mean=1003.0,
                               SolarRadiation_Total=1500.0)
        self.assertNotEqual(hot.level, cool.level)
        for city, p in (("Malabon", hot), ("Muntinlupa", cool)):
            m = A.build_map_data(self.locations, city, p).set_index("City")
            self.assertEqual(tuple(m.loc[city, "color"]), A.LEVEL_COLORS[p.level])

    def test_every_city_can_be_the_chosen_one(self):
        p = self.prediction()
        for city in self.locations["City"]:
            m = A.build_map_data(self.locations, city, p)
            self.assertEqual(int(m["selected"].sum()), 1, city)

    def test_an_unknown_city_is_refused_and_the_input_is_not_changed(self):
        before = self.locations.copy()
        with self.assertRaises(ValueError):
            A.build_map_data(self.locations, "Cebu", self.prediction())
        with self.assertRaises(ValueError):
            A.build_map_data(self.locations, "Cebu")
        self.assertTrue(before.equals(self.locations))


class MapShapes(unittest.TestCase):
    """The real outlines of the NCR cities (app/ncr_cities.geojson) and how they are coloured."""

    @classmethod
    def setUpClass(cls):
        cls.shapes = A.load_city_shapes()
        cls.locations = A.load_city_locations()
        cls.summary = A.training_summary(A.load_training_data())
        cls.model = A.build_model(A.load_training_data(), n_estimators=20)

    def prediction(self):
        return A.predict_level(self.model, A.validate_inputs(VALID, self.summary).clean)

    def by_city(self, geojson):
        return {f["properties"]["City"]: f["properties"] for f in geojson["features"]}

    def test_the_file_has_the_16_cities_of_the_data_plus_pateros(self):
        names = [f["properties"]["City"] for f in self.shapes["features"]]
        self.assertEqual(sorted(names), sorted(self.summary["cities"] + ["Pateros"]))
        flags = self.by_city(self.shapes)
        self.assertTrue(all(flags[c]["in_data"] for c in self.summary["cities"]))
        self.assertFalse(flags["Pateros"]["in_data"])

    def test_every_outline_is_a_closed_polygon_inside_metro_manila(self):
        for f in self.shapes["features"]:
            g = f["geometry"]
            self.assertIn(g["type"], ("Polygon", "MultiPolygon"))
            polygons = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for poly in polygons:
                for ring in poly:
                    self.assertGreaterEqual(len(ring), 4, f["properties"]["City"])
                    self.assertEqual(ring[0], ring[-1], f["properties"]["City"])
                    for lon, lat in ring:
                        self.assertTrue(120.88 <= lon <= 121.2 and 14.3 <= lat <= 14.8, (f["properties"]["City"], lon, lat))

    def test_label_points_lie_near_the_cities_locations_and_the_area_is_plausible(self):
        loc = self.locations.set_index("City")
        for city, p in self.by_city(self.shapes).items():
            self.assertTrue(120.88 <= p["cx"] <= 121.2 and 14.3 <= p["cy"] <= 14.8, city)
            if city in loc.index:
                self.assertLess(abs(p["cx"] - loc.loc[city, "Longitude"]), 0.05, city)
                self.assertLess(abs(p["cy"] - loc.loc[city, "Latitude"]), 0.05, city)
        total = sum(p["area_km2"] for p in self.by_city(self.shapes).values())
        self.assertTrue(500 <= total <= 700, total)                       # Metro Manila is about 620 km2

    def test_the_file_stays_small_and_names_its_source(self):
        self.assertLess(A.SHAPES_FILE.stat().st_size, 300_000)
        self.assertIn("faeldon", self.shapes["attribution"])

    def test_before_a_guess_all_cities_are_grey_and_pateros_is_pale(self):
        g, labels = A.build_map_shapes(self.shapes, self.locations)
        props = self.by_city(g)
        self.assertTrue(all(tuple(props[c]["fill_color"][:3]) == A.NEUTRAL_COLOR for c in self.summary["cities"]))
        self.assertEqual(tuple(props["Pateros"]["fill_color"][:3]), A.OUTSIDE_COLOR)
        self.assertEqual(len(labels), 16)

    def test_the_chosen_city_is_blue_then_level_coloured_and_outlined_the_others_never_change(self):
        grey, _ = A.build_map_shapes(self.shapes, self.locations)
        blue, _ = A.build_map_shapes(self.shapes, self.locations, "Pasig")
        done, labels = A.build_map_shapes(self.shapes, self.locations, "Pasig", self.prediction())
        p_grey, p_blue, p_done = self.by_city(grey), self.by_city(blue), self.by_city(done)
        self.assertEqual(tuple(p_blue["Pasig"]["fill_color"][:3]), A.HIGHLIGHT_COLOR)
        self.assertEqual(tuple(p_done["Pasig"]["fill_color"][:3]), A.LEVEL_COLORS[self.prediction().level])
        for p in (p_blue, p_done):
            self.assertGreater(p["Pasig"]["line_width"], p_grey["Pasig"]["line_width"])
            self.assertEqual(tuple(p["Pasig"]["line_color"]), A.SELECTED_LINE_COLOR)
        for city in p_grey:
            if city != "Pasig":
                self.assertEqual(p_blue[city]["fill_color"], p_grey[city]["fill_color"], city)
                self.assertEqual(p_done[city]["fill_color"], p_grey[city]["fill_color"], city)
        self.assertIn(self.prediction().level, labels.set_index("label").index[labels["selected"]][0])

    def test_building_the_layers_does_not_change_the_loaded_shapes(self):
        import copy
        before = copy.deepcopy(self.shapes)
        A.build_map_shapes(self.shapes, self.locations, "Manila", self.prediction())
        self.assertEqual(before, self.shapes)

    def test_an_unknown_city_is_refused(self):
        with self.assertRaises(ValueError):
            A.build_map_shapes(self.shapes, self.locations, "Cebu")


class Screen(unittest.TestCase):
    """The real Streamlit page, run without a browser."""

    NORMAL_DAY = {"HeatIndex_Max_Today": 38.0, "Temp_Min": 26.0, "Rainfall_Total": 0.0, "Pressure_Mean": 1010.0,
                  "SolarRadiation_Total": 5000.0}

    @classmethod
    def setUpClass(cls):
        try:
            from streamlit.testing.v1 import AppTest
        except ImportError:                               # pragma: no cover
            raise unittest.SkipTest("streamlit is not installed")
        cls.AppTest = AppTest

    def app(self):
        at = self.AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=180)
        at.run()
        self.assertFalse(at.exception, at.exception)
        return at

    def submit(self, at, **values):
        for col, value in {**self.NORMAL_DAY, **values}.items():
            at.number_input(key=col).set_value(value)
        at.button[0].click().run()
        self.assertFalse(at.exception, at.exception)
        return at

    def messages(self, at):
        return [m.value for m in [*at.error, *at.warning, *at.success]]

    def test_page_opens_with_empty_inputs_and_no_result_yet(self):
        at = self.app()
        self.assertEqual(len(at.number_input), 5)
        self.assertTrue(all(n.value is None for n in at.number_input))      # nothing is silently pre-filled
        self.assertEqual(len(at.selectbox), 1)
        self.assertEqual(len(at.error), 0)
        self.assertEqual(len(at.get("progress")), 0)

    def maps(self, at):
        return at.get("deck_gl_json_chart")

    def test_an_old_copy_of_the_logic_still_in_memory_does_not_break_the_page(self):
        """Streamlit Cloud pulls new code without restarting Python, so app_logic from the previous deploy can still be in memory
        (this crashed the live app with AttributeError: no attribute 'load_city_locations'). The page must re-read it."""
        for name in ("load_city_locations", "load_city_shapes", "build_map_shapes"):
            delattr(A, name)                                   # the old version did not have these
        at = self.app()
        self.assertEqual(len(self.maps(at)), 1)
        self.assertTrue(hasattr(A, "build_map_shapes"))        # re-read from the file

    def test_the_map_is_on_the_page_from_the_start(self):
        self.assertEqual(len(self.maps(self.app())), 1)

    def test_manila_is_highlighted_at_the_start_and_the_other_city_when_chosen(self):
        at = self.app()
        self.assertIn("Manila (selected)", str(self.maps(at)[0].proto.json))
        at.selectbox[0].select("Malabon").run()                  # the picker is outside the form: the map reacts at once
        self.assertFalse(at.exception, at.exception)
        text = str(self.maps(at)[0].proto.json)
        self.assertIn("Malabon (selected)", text)
        self.assertNotIn("Manila (selected)", text)
        self.assertEqual(len(at.get("progress")), 0)             # no guess yet

    def test_the_chosen_city_changes_colour_when_the_guess_is_made(self):
        at = self.app()
        at.selectbox[0].select("Marikina").run()
        before = str(self.maps(at)[0].proto.json)
        self.assertIn("Marikina (selected)", before)
        self.assertNotIn("tomorrow", before)
        self.submit(at)
        after = str(self.maps(at)[0].proto.json)
        self.assertIn("Marikina: tomorrow", after)
        self.assertNotIn("(selected)", after)

    def test_map_stays_neutral_when_the_input_has_errors(self):
        at = self.submit(self.app(), Rainfall_Total=-5.0)
        self.assertEqual(len(self.maps(at)), 1)
        self.assertNotIn("tomorrow", str(self.maps(at)[0].proto.json))

    def test_map_shows_the_chosen_city_after_a_guess(self):
        at = self.submit(self.app())
        self.assertEqual(len(self.maps(at)), 1)
        self.assertIn("Manila: tomorrow", str(self.maps(at)[0].proto.json))

    def test_empty_form_reports_every_missing_value_and_gives_no_prediction(self):
        at = self.app()
        at.button[0].click().run()
        self.assertFalse(at.exception, at.exception)
        self.assertEqual(len(at.error), 5)
        self.assertTrue(all("please enter a value" in e.value for e in at.error))
        self.assertEqual(len(at.get("progress")), 0)

    def test_one_missing_value_is_reported_by_name(self):
        at = self.app()
        for col, value in self.NORMAL_DAY.items():
            if col != "Pressure_Mean":
                at.number_input(key=col).set_value(value)
        at.button[0].click().run()
        self.assertEqual([e.value for e in at.error], ["Average air pressure today: please enter a value."])
        self.assertEqual(len(at.get("progress")), 0)

    def test_valid_input_shows_a_level_and_five_probabilities(self):
        at = self.submit(self.app())
        self.assertEqual(len(at.get("progress")), 5)
        self.assertEqual(len(at.error) + len([w for w in at.warning]) + len(at.success), 1)
        self.assertIn("Tomorrow in Manila", " ".join(self.messages(at)))

    def test_impossible_value_shows_an_error_and_no_prediction(self):
        at = self.submit(self.app(), Rainfall_Total=-5.0)
        self.assertEqual(len(at.get("progress")), 0)
        self.assertTrue(any("not possible" in e.value for e in at.error))

    def test_value_at_the_hard_limit_is_accepted(self):
        at = self.submit(self.app(), Rainfall_Total=0.0)           # zero rain is a value, not an empty box
        self.assertEqual(len(at.get("progress")), 5)
        at = self.submit(self.app(), Rainfall_Total=500.0)
        self.assertEqual(len(at.get("progress")), 5)

    def test_unusual_value_shows_a_warning_and_still_predicts(self):
        at = self.submit(self.app(), HeatIndex_Max_Today=55.0)
        self.assertEqual(len(at.get("progress")), 5)
        self.assertTrue(any("outside" in w.value for w in at.warning))


if __name__ == "__main__":
    unittest.main()
