# yDrinks test suite

Tests check **xlsx_reader** and **ydrinks_file_merge** for correctness and help catch regressions.

## Run all tests

From the `code` directory:

```bash
python3 run_tests.py
```

Or with unittest directly:

```bash
cd code
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## What’s covered

- **test_xlsx_reader.py**
  - Column ref parsing (`A`, `AA`, `AB`, …)
  - Cell ref parsing (`A1`, `B2`, …)
  - Unique column names (including duplicates and empty names)
  - `read_xlsx_sheet`: missing/bad file, bad zip, valid minimal xlsx, `skip_rows`, empty when skip too large

- **test_ydrinks_file_merge.py**
  - `year_week_from_filename`: valid names (e.g. `Casa_Dragones_Activity_Report_202529_...`), temp files `~$`, non-.xlsx, need 5 parts and 6-digit YYYYWW
  - `merge_dataframes`: empty dict, single DataFrame, multiple in sorted order, reset index
  - `load_data`: empty folder, non-.xlsx files, temp `.xlsx` files

## Bug found and fixed

The suite found that `year_week_from_filename` did not require the 5th part to be exactly 6 digits, so a name like `a_b_c_d_20252.xlsx` produced `2025-2.` instead of `None`. The implementation was updated to require `len(parts[4]) == 6` and `parts[4].isdigit()`.
