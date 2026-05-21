"""
Tests for ydrinks_file_merge: year_week_from_filename, load_data, merge_dataframes.
"""

import os
import tempfile
import unittest
import pandas as pd

from ydrinks_file_merge import (
    year_week_from_filename,
    load_data,
    merge_dataframes,
)


class TestYearWeekFromFilename(unittest.TestCase):
    def test_valid_typical(self):
        # Real format: 4 segments then YYYYWW (e.g. Casa_Dragones_Activity_Report_202529_...)
        self.assertEqual(year_week_from_filename("Casa_Dragones_Activity_Report_202529_ts20250722.xlsx"), "2025-29")
        self.assertEqual(year_week_from_filename("Casa_Dragones_Activity_Report_202401_other.xlsx"), "2024-01")
        self.assertEqual(year_week_from_filename("a_b_c_d_202552_rest.xlsx"), "2025-52")

    def test_ignores_temp_files(self):
        self.assertIsNone(year_week_from_filename("~$yDrinks_Activity_Report_202529.xlsx"))

    def test_requires_xlsx(self):
        self.assertIsNone(year_week_from_filename("yDrinks_Activity_Report_202529.csv"))
        self.assertIsNone(year_week_from_filename("yDrinks_Activity_Report_202529"))

    def test_requires_five_parts(self):
        self.assertIsNone(year_week_from_filename("a_b_c_202529.xlsx"))
        self.assertIsNone(year_week_from_filename("a_b_c_d_20252.xlsx"))

    def test_extracts_six_digits(self):
        self.assertEqual(year_week_from_filename("x_x_x_x_202529_rest.xlsx"), "2025-29")
        self.assertEqual(year_week_from_filename("x_x_x_x_199901_rest.xlsx"), "1999-01")


class TestMergeDataframes(unittest.TestCase):
    def test_empty(self):
        result = merge_dataframes({})
        self.assertTrue(result.empty)
        self.assertIsInstance(result, pd.DataFrame)

    def test_single(self):
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        merged = merge_dataframes({"2024-01": df})
        self.assertEqual(len(merged), 2)
        self.assertEqual(list(merged.columns), ["A", "B"])
        pd.testing.assert_frame_equal(merged, df)

    def test_sorted_order(self):
        df1 = pd.DataFrame({"Week": ["2024-01"], "Val": [1]})
        df2 = pd.DataFrame({"Week": ["2024-02"], "Val": [2]})
        df3 = pd.DataFrame({"Week": ["2024-03"], "Val": [3]})
        data = {"2024-03": df3, "2024-01": df1, "2024-02": df2}
        merged = merge_dataframes(data)
        self.assertEqual(len(merged), 3)
        self.assertEqual(list(merged["Val"]), [1, 2, 3])

    def test_ignore_index(self):
        df1 = pd.DataFrame({"A": [1]})
        df2 = pd.DataFrame({"A": [2]})
        merged = merge_dataframes({"2024-01": df1, "2024-02": df2})
        self.assertEqual(list(merged.index), [0, 1])


class TestLoadData(unittest.TestCase):
    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as d:
            result = load_data(d)
            self.assertEqual(result, {})

    def test_ignores_non_xlsx(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "report_202401.txt"), "w") as f:
                f.write("x")
            result = load_data(d)
            self.assertEqual(result, {})

    def test_ignores_temp_xlsx(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "~$report_202401_extra.xlsx"), "w") as f:
                f.write("x")
            result = load_data(d)
            self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
