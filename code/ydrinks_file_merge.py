"""
================================================================================
yDrinks File Merger - Beginner's Guide
================================================================================

WHAT THIS SCRIPT DOES:
 Takes all yDrinks Excel activity reports from a folder and combines them
 into a single Excel file. Works even if some files have formatting issues.

OUTPUT:
 Creates a file called "ydrinks_merged.xlsx" with all the data combined,
 sorted by year and week.
"""

# --- Import tools we need ---
import os                              # For working with folders and file paths
import pandas as pd                    # For working with spreadsheet data (tables)


# Terminal output: keep step headers clear vs. detail lines
_PRINT_RULE = "-" * 52

def _detail(message):
   """Print a sub-step line (indented under the current step)."""
   print(f"  {message}")


def year_week_from_filename(filename):
   """
   Figures out the "year-week" from a filename like: something_202529_otherstuff.xlsx
   Returns it in a nice format: "2025-29" (year 2025, week 29)
   Returns None if the filename doesn't match the expected pattern.
   """
   # Skip files that aren't real Excel files, or temp files (like ~$Report.xlsx)
   if not filename.endswith(".xlsx") or filename.startswith("~$"):
       return None


   # Split the filename by underscores and grab the 5th part (index 4)
   # Example: "report_sales_region_202529_data.xlsx" -> parts[4] = "202529"
   parts = filename.split("_")
   if len(parts) < 5:
       return None
   candidate = parts[4]


   # The year-week must be exactly 6 digits (4 for year, 2 for week)
   # This prevents grabbing wrong numbers like "20252" or "abc123"
   if len(candidate) != 6 or not candidate.isdigit():
       return None

   # Format it nicely: "202529" -> "2025-29"
   try:
       return f"{candidate[:4]}-{candidate[4:6]}"
   except (IndexError, ValueError):
       return None


def load_data(folder_path):
   """
   Reads all Excel files from the given folder and loads them into memory.
   Each file is stored under its year-week key (e.g. "2025-29").
   Skips files that don't match our naming pattern or have no data.
   """
   data = {}  # Empty container to hold our spreadsheets
   _detail(f"Scanning folder: {folder_path}")

   # Loop through every file in the folder
   for name in os.listdir(folder_path):
       key = year_week_from_filename(name)
       if key is None:
           continue  # Skip this file - we couldn't figure out its year-week
       year, week = key.split("-")

       # Build the full path (e.g. "yDrinks_data/report_202529.xlsx")
       path = os.path.join(folder_path, name)

       # Read the Excel file, skip the first row (often headers)
       df = pd.read_excel(path, skiprows=1, engine="calamine")

       # Only add it if it has actual data (not empty)
       if not df.empty:
           data[key] = df
           _detail(
               f"Loading {len(df)} rows for report of week {week} of {year}"
           )
       else:
           _detail(f"Skipped empty file: {name}")
   _detail(f"Finished loading. Reports with data: {len(data)}")

   return data


def merge_dataframes(data_dict):
   """
   Combines all the individual spreadsheets into one big spreadsheet.
   Sorts them by year-week so the oldest is first and newest is last.
   """
   if not data_dict:
       _detail("Nothing to merge (no reports loaded).")
       return pd.DataFrame()  # Empty spreadsheet if no data was loaded


   # Stack all spreadsheets on top of each other, in sorted order
   _detail(f"Merging {len(data_dict)} reports...")
   merged_df = pd.concat([data_dict[k] for k in sorted(data_dict)], ignore_index=True)
   _detail(f"Combined total: {len(merged_df)} rows.")
   return merged_df




# =============================================================================
# MAIN: This runs when you execute the script (e.g. double-click or "python ...")
# =============================================================================
if __name__ == "__main__":
   print()
   print("yDrinks file merge")
   print(_PRINT_RULE)
   # Figure out where the "yDrinks_data" folder is (same level as the "code" folder)
   folder = os.path.join(
       os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
       "yDrinks_data",
   )
   _detail(f"Data folder: {folder}")
   print()


   # Step 1: Load all Excel files from that folder
   print("Step 1/3 — Load reports from folder")
   print(_PRINT_RULE)
   data = load_data(folder)
   print()


   # Step 2: Merge them into one big spreadsheet
   print("Step 2/3 — Merge into one table")
   print(_PRINT_RULE)
   merged = merge_dataframes(data)
   print()


   # Step 3: Save the result to "ydrinks_merged.xlsx" (in the current folder)
   print("Step 3/3 — Write Excel file")
   print(_PRINT_RULE)
   merged.to_excel("ydrinks_merged_draft2.xlsx", index=False)
   _detail('Saved as "ydrinks_merged_draft2.xlsx" (same folder you ran the script from).')
   print()
   print(_PRINT_RULE)
   print("Done.")
