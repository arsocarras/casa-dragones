"""
Tests for xlsx_reader: column/row parsing, unique columns, and read_xlsx_sheet.
"""

import io
import os
import tempfile
import unittest
import zipfile
import pandas as pd

from xlsx_reader import (
    read_xlsx_sheet,
    _col_ref_to_index,
    _cell_ref_to_row_col,
    _unique_columns,
)


def _escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _index_to_col(i):
    result = []
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        result.append(chr(ord("A") + r))
    return "".join(reversed(result))


def _make_minimal_xlsx(rows_data, shared_strings_list=None):
    """Build a minimal .xlsx (zip) with given header row and data rows."""
    NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        if shared_strings_list is not None:
            ss = '<?xml version="1.0"?><sst xmlns="' + NS + '" count="' + str(len(shared_strings_list)) + '" uniqueCount="' + str(len(shared_strings_list)) + '">'
            for s in shared_strings_list:
                ss += "<si><t>" + _escape(s) + "</t></si>"
            ss += "</sst>"
            z.writestr("xl/sharedStrings.xml", ss.encode("utf-8"))
        rels = '<?xml version="1.0"?><Relationships xmlns="' + RELS_NS + '">'
        rels += '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml" Id="rId1"/>'
        rels += "</Relationships>"
        z.writestr("xl/_rels/workbook.xml.rels", rels.encode("utf-8"))
        sheet = '<?xml version="1.0"?><worksheet xmlns="' + NS + '"><sheetData>'
        for row_idx, row in enumerate(rows_data):
            excel_row = row_idx + 1
            sheet += '<row r="' + str(excel_row) + '">'
            for col_idx, val in enumerate(row):
                col_ref = _index_to_col(col_idx)
                cell_ref = col_ref + str(excel_row)
                if isinstance(val, str) and shared_strings_list is not None and val in shared_strings_list:
                    s_idx = shared_strings_list.index(val)
                    sheet += '<c r="' + cell_ref + '" t="s"><v>' + str(s_idx) + '</v></c>'
                elif isinstance(val, (int, float)):
                    sheet += '<c r="' + cell_ref + '"><v>' + str(val) + '</v></c>'
                elif isinstance(val, str):
                    sheet += '<c r="' + cell_ref + '" t="str"><v>' + _escape(val) + '</v></c>'
            sheet += "</row>"
        sheet += "</sheetData></worksheet>"
        z.writestr("xl/worksheets/sheet1.xml", sheet.encode("utf-8"))
    buf.seek(0)
    return buf.read()


class TestColRefToIndex(unittest.TestCase):
    def test_single_letter(self):
        self.assertEqual(_col_ref_to_index("A"), 0)
        self.assertEqual(_col_ref_to_index("a"), 0)
        self.assertEqual(_col_ref_to_index("B"), 1)
        self.assertEqual(_col_ref_to_index("Z"), 25)

    def test_double_letter(self):
        self.assertEqual(_col_ref_to_index("AA"), 26)
        self.assertEqual(_col_ref_to_index("AB"), 27)
        self.assertEqual(_col_ref_to_index("AZ"), 51)
        self.assertEqual(_col_ref_to_index("BA"), 52)
        self.assertEqual(_col_ref_to_index("ZZ"), 701)

    def test_triple_letter(self):
        self.assertEqual(_col_ref_to_index("AAA"), 702)


class TestCellRefToRowCol(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(_cell_ref_to_row_col("A1"), (0, 0))
        self.assertEqual(_cell_ref_to_row_col("B1"), (0, 1))
        self.assertEqual(_cell_ref_to_row_col("A2"), (1, 0))
        self.assertEqual(_cell_ref_to_row_col("Z10"), (9, 25))

    def test_multiple_columns(self):
        self.assertEqual(_cell_ref_to_row_col("AA1"), (0, 26))
        self.assertEqual(_cell_ref_to_row_col("AB10"), (9, 27))


class TestUniqueColumns(unittest.TestCase):
    def test_no_duplicates(self):
        self.assertEqual(_unique_columns(["A", "B", "C"]), ["A", "B", "C"])

    def test_with_duplicates(self):
        self.assertEqual(_unique_columns(["A", "B", "A"]), ["A", "B", "A_1"])

    def test_multiple_duplicates(self):
        self.assertEqual(_unique_columns(["X", "X", "X"]), ["X", "X_1", "X_2"])

    def test_empty_string_duplicates(self):
        raw = ["", "A", ""]
        out = _unique_columns(raw)
        self.assertEqual(out[0], "")
        self.assertEqual(out[1], "A")
        self.assertEqual(out[2], "Unnamed_1")

    def test_non_string_coerced(self):
        self.assertEqual(_unique_columns([1, 2, 1]), ["1", "2", "1_1"])


class TestReadXlsxSheetErrors(unittest.TestCase):
    def test_nonexistent_file(self):
        result = read_xlsx_sheet("/nonexistent/path/file.xlsx")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    def test_bad_zip(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(b"not a zip file")
            path = f.name
        try:
            result = read_xlsx_sheet(path)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)
        finally:
            os.unlink(path)

    def test_zip_with_no_worksheet(self):
        RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            rels = '<?xml version="1.0"?><Relationships xmlns="' + RELS_NS + '"></Relationships>'
            z.writestr("xl/_rels/workbook.xml.rels", rels.encode("utf-8"))
        buf.seek(0)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(buf.read())
            path = f.name
        try:
            result = read_xlsx_sheet(path)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)
        finally:
            os.unlink(path)


class TestReadXlsxSheetValid(unittest.TestCase):
    def test_minimal_valid(self):
        shared = ["Name", "Score"]
        rows = [["Name", "Score"], ["Alice", 100], ["Bob", 95]]
        xlsx_bytes = _make_minimal_xlsx(rows, shared_strings_list=shared)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(xlsx_bytes)
            path = f.name
        try:
            df = read_xlsx_sheet(path, skip_rows=0)
            self.assertFalse(df.empty)
            self.assertEqual(list(df.columns), ["Name", "Score"])
            self.assertEqual(len(df), 2)
            self.assertEqual(df.iloc[0]["Name"], "Alice")
            self.assertEqual(df.iloc[0]["Score"], 100.0)
            self.assertEqual(df.iloc[1]["Name"], "Bob")
            self.assertEqual(df.iloc[1]["Score"], 95.0)
        finally:
            os.unlink(path)

    def test_skip_rows(self):
        shared = ["Title", "Name", "Value", "A", "B"]
        rows = [["Report Title"], ["Name", "Value"], ["A", 10], ["B", 20]]
        xlsx_bytes = _make_minimal_xlsx(rows, shared_strings_list=shared)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(xlsx_bytes)
            path = f.name
        try:
            df = read_xlsx_sheet(path, skip_rows=1)
            self.assertEqual(list(df.columns), ["Name", "Value"])
            self.assertEqual(len(df), 2)
            self.assertEqual(df.iloc[0]["Name"], "A")
            self.assertEqual(df.iloc[0]["Value"], 10.0)
            self.assertEqual(df.iloc[1]["Name"], "B")
            self.assertEqual(df.iloc[1]["Value"], 20.0)
        finally:
            os.unlink(path)

    def test_too_many_skip_returns_empty(self):
        rows = [["H1", "H2"]]
        xlsx_bytes = _make_minimal_xlsx(rows, shared_strings_list=["H1", "H2"])
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(xlsx_bytes)
            path = f.name
        try:
            df = read_xlsx_sheet(path, skip_rows=5)
            self.assertTrue(df.empty)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
