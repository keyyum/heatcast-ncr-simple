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
