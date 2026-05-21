"""
Read first sheet from .xlsx using zip/XML only (no openpyxl).
Use this when openpyxl fails on files with non-standard or broken styles.
"""

import zipfile
import xml.etree.ElementTree as ET

import pandas as pd

NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RELS_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}


def _col_ref_to_index(ref):
    idx = 0
    for c in ref:
        idx = idx * 26 + (ord(c.upper()) - ord("A") + 1)
    return idx - 1


def _cell_ref_to_row_col(cell_ref):
    col_part = "".join(c for c in cell_ref if c.isalpha())
    row_part = cell_ref[len(col_part):]
    return int(row_part) - 1, _col_ref_to_index(col_part)


def _unique_columns(raw):
    raw = [x if isinstance(x, str) else str(x) for x in raw]
    seen, out = {}, []
    for c in raw:
        if c not in seen:
            seen[c] = 0
            out.append(c)
        else:
            seen[c] += 1
            out.append(f"{c}_{seen[c]}" if c else f"Unnamed_{seen[c]}")
    return out


def read_xlsx_sheet(filepath, skip_rows=1):
    """
    Read the first sheet from an .xlsx. Returns a DataFrame or empty one.
    skip_rows: number of rows to skip before the header row (default 1 = skip title row).
    Returns empty DataFrame on bad zip, I/O errors, or parse errors (e.g. lock files ~$*.xlsx).
    """
    try:
        return _read_xlsx_sheet(filepath, skip_rows)
    except (zipfile.BadZipFile, OSError, ET.ParseError):
        return pd.DataFrame()


def _read_xlsx_sheet(filepath, skip_rows):
    shared_strings = []
    with zipfile.ZipFile(filepath, "r") as z:
        try:
            with z.open("xl/sharedStrings.xml") as f:
                root = ET.parse(f).getroot()
                for si in root.findall(".//main:si", NS):
                    t = si.find("main:t", NS)
                    if t is not None and t.text:
                        shared_strings.append(t.text)
                    else:
                        shared_strings.append(
                            "".join(p.text or "" for p in si.findall(".//main:t", NS))
                        )
        except KeyError:
            pass

        with z.open("xl/_rels/workbook.xml.rels") as f:
            root = ET.parse(f).getroot()
            sheet_path = None
            for rel in root.findall("r:Relationship", RELS_NS):
                if "worksheet" in rel.get("Type", ""):
                    sheet_path = "xl/" + rel.get("Target", "")
                    break
        if not sheet_path:
            return pd.DataFrame()

        with z.open(sheet_path) as f:
            sheet_data = ET.parse(f).getroot().find("main:sheetData", NS)
            if sheet_data is None:
                return pd.DataFrame()

            grid = {}
            for row_elem in sheet_data.findall("main:row", NS):
                for c in row_elem.findall("main:c", NS):
                    r = c.get("r")
                    if not r:
                        continue
                    cell_row, cell_col = _cell_ref_to_row_col(r)
                    v = c.find("main:v", NS)
                    if v is None or v.text is None:
                        continue
                    t = c.get("t", "n")
                    if t == "s":
                        try:
                            val = shared_strings[int(v.text)]
                        except (IndexError, ValueError):
                            val = v.text
                    elif t in ("str", "inlineStr"):
                        val = v.text
                    else:
                        try:
                            val = float(v.text)
                        except ValueError:
                            val = v.text
                    grid[(cell_row, cell_col)] = val

    if not grid:
        return pd.DataFrame()

    max_row = max(r for r, _ in grid) + 1
    max_col = max(c for _, c in grid) + 1
    rows = [[grid.get((r, c), None) for c in range(max_col)] for r in range(max_row)]

    if len(rows) <= skip_rows:
        return pd.DataFrame()
    columns = _unique_columns(rows[skip_rows])
    return pd.DataFrame(rows[skip_rows + 1:], columns=columns)
