import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date



# ==============================================================================
# 1) FILE PATHS / LOOKUP TABLES
# ==============================================================================
# These paths are built from the script location so the project is portable.
# If someone has the full project folder, the code should work on their machine too.
CODE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CODE_DIR.parent

CODIST_TO_LABELS_PATH = CODE_DIR / "codist_to_labels.xlsx"
CODIST_TO_LABELNUM_PATH = CODE_DIR / "codist_to_labelnum.xlsx"
STATE_TO_REGION_PATH = CODE_DIR / "state_to_region.xlsx"


def load_dict_from_excel(file_path, key_column, value_column, sheet_name=0):
    """
    Read one Excel sheet and return a dictionary.

    Example:
    If the sheet has State -> Region, this returns {"CA": "West", "TX": "South", ...}
    """
    data = pd.read_excel(file_path, sheet_name=sheet_name)
    return data.set_index(key_column)[value_column].to_dict()


def normalize_lookup(mapping):
    """
    Trim whitespace from dictionary keys so values like 'P2 P3 P6 '
    still match keys stored as 'P2 P3 P6'.
    """
    return {str(k).strip(): v for k, v in mapping.items()}


def normalize_text(value):
    """Return trimmed text for Excel values that may contain trailing spaces."""
    if pd.isna(value):
        return value
    return str(value).strip()


# Lookups used later in transformations.
codedist_to_labels = normalize_lookup(
    load_dict_from_excel(CODIST_TO_LABELS_PATH, "CoDist", "Labels")
)
codedist_to_labelnum = normalize_lookup(
    load_dict_from_excel(CODIST_TO_LABELNUM_PATH, "CoDist", "Number of Labels")
)
state_to_region = normalize_lookup(
    load_dict_from_excel(STATE_TO_REGION_PATH, "State", "Region", sheet_name="state_to_region")
)
state_to_sgws_region = normalize_lookup(
    load_dict_from_excel(
        STATE_TO_REGION_PATH,
        "State",
        "SGWS Region",
        sheet_name="state_to_sgws_region",
    )
)


# ==============================================================================
# 2) LOADING THE MAIN EXPORT FILE
# ==============================================================================
def load_excel_with_multiheader(file_path, header_row_start=29):
    """
    Load an Excel file where header info is spread across 2 rows.

    The export format has:
    - Row N: product/category name (often merged across many columns)
    - Row N+1: metric name for each specific column

    This function combines both rows into one clean column name per field.
    """
    skiprows = header_row_start - 1  # Convert 1-based row number to pandas indexing.

    print()
    print(f"Reading Excel file: {file_path}")
    print(f"Header rows: {header_row_start} and {header_row_start + 1}")
    print("-" * 60)

    # Read the two header rows only.
    headers = pd.read_excel(
        file_path,
        skiprows=skiprows - 1,  # start at the first header row
        nrows=2,
        header=None,
    )

    # Forward-fill row 1 headers so blank cells inherit the previous category.
    headers.iloc[0] = headers.iloc[0].ffill()

    # Read all actual data rows.
    df_flat = pd.read_excel(
        file_path,
        skiprows=list(range(skiprows)),  # skip everything before data starts
    )

    # Build one flat column name from (category + metric).
    df_flat.columns = [
        f"{category}_{metric}" if pd.notna(category) else metric
        for category, metric in zip(headers.iloc[0].values, headers.iloc[1].values)
    ]

    print("=" * 60)
    print("SUCCESS! Data loaded successfully.")
    print("=" * 60)
    print(f"DataFrame shape: {df_flat.shape[0]} rows × {df_flat.shape[1]} columns")
    print()

    return df_flat


# ==============================================================================
# 3) BUSINESS TRANSFORMATION (JOSH TABLE)
# ==============================================================================
def josh_edits(df_flat):
    """
    Build the business-friendly summary table used in final reporting.
    """
    #print(df_flat)
    print()
    print("-" * 60)
    print("Starting business transformation (josh_edits)...")
    print("-" * 60)

    # Rename columns where CoDist mapping provides better business labels.
    df_flat = df_flat.rename(columns=codedist_to_labels)

    # Build the core summary table with account + product metrics.
    df_josh = pd.DataFrame(
        {
            "Customer Name": df_flat["Account_Customer Name"],
            "TDLinx Code": df_flat["Account_TDLinx Code"],
            "State": df_flat["Account_State"],
            # If owner is listed as "Independent", use customer name as owner.
            "Owner": np.where(
                df_flat["Account_Owner"] == "Independent",
                df_flat["Account_Customer Name"],
                df_flat["Account_Owner"],
            ),
            "Region": df_flat["Account_State"].apply(
                lambda x: state_to_region.get(x, "Other") if pd.notna(x) else "Other"
            ),
            "SGWS Region": df_flat["Account_State"].apply(
                lambda x: state_to_sgws_region.get(x, "Other") if pd.notna(x) else "Other"
            ),
            "Labels": df_flat["Product Universe_CoDist"].apply(
                lambda x: codedist_to_labels.get(normalize_text(x), x) if pd.notna(x) else x
            ),
            "Joven 9LC TY": df_flat["Casa Dragones Tequila Joven_9L"],
            "Joven 9LC LY": df_flat["Casa Dragones Tequila Joven_9L"]
            - df_flat["Casa Dragones Tequila Joven_9L Chg"],
            "Blanco 9LC TY": df_flat["Casa Dragones Tequila Blanco_9L"],
            "Blanco 9LC LY": df_flat["Casa Dragones Tequila Blanco_9L"]
            - df_flat["Casa Dragones Tequila Blanco_9L Chg"],
            "Añejo 9LC TY": df_flat["Casa Dragones Tequila Anejo, E..._9L"],
            "Añejo 9LC LY": df_flat["Casa Dragones Tequila Anejo, E..._9L"]
            - df_flat["Casa Dragones Tequila Anejo, E..._9L Chg"],
            "Reposado 9LC TY": df_flat["Casa Dragones Tequila Reposado_9L"],
            "Reposado 9LC LY": df_flat["Casa Dragones Tequila Reposado_9L"]
            - df_flat["Casa Dragones Tequila Reposado_9L Chg"],
            "Cristalino 9LC TY": df_flat["Casa Dragones Teq Crist80 200c..._9L"],
            "Cristalino 9LC LY": df_flat["Casa Dragones Teq Crist80 200c..._9L"]
                - df_flat["Casa Dragones Teq Crist80 200c..._9L Chg"],
            "TK 9LC TY": df_flat["Casa Dragones Other_9L"],
            "TK 9LC LY": df_flat["Casa Dragones Other_9L"] - df_flat["Casa Dragones Other_9L Chg"],
        }
    )

    print()
    print("Built base summary columns. Calculating totals and POD flags...")

    # Total Casa Dragones 9L case volume (TY and LY).
    df_josh["Total CD 9LC TY"] = df_josh[
        ["Joven 9LC TY", "Blanco 9LC TY", "Añejo 9LC TY", "Reposado 9LC TY", "TK 9LC TY", "Cristalino 9LC TY"]
    ].sum(axis=1)
    df_josh["Total CD 9LC LY"] = df_josh[
        ["Joven 9LC TY", "Blanco 9LC LY", "Añejo 9LC LY", "Reposado 9LC LY", "TK 9LC LY", "Cristalino 9LC LY"]
    ].sum(axis=1)

    # POD (Point of Distribution) flags: 1 means that item sold > 0, 0 means no sales.
    df_josh["Joven POD TY"] = (df_josh["Joven 9LC TY"] > 0).astype(int)
    df_josh["Joven POD LY"] = (df_josh["Joven 9LC LY"] > 0).astype(int)
    df_josh["Blanco POD TY"] = (df_josh["Blanco 9LC TY"] > 0).astype(int)
    df_josh["Blanco POD LY"] = (df_josh["Blanco 9LC LY"] > 0).astype(int)
    df_josh["Añejo POD TY"] = (df_josh["Añejo 9LC TY"] > 0).astype(int)
    df_josh["Añejo POD LY"] = (df_josh["Añejo 9LC LY"] > 0).astype(int)
    df_josh["Reposado POD TY"] = (df_josh["Reposado 9LC TY"] > 0).astype(int)
    df_josh["Reposado POD LY"] = (df_josh["Reposado 9LC LY"] > 0).astype(int)
    df_josh["Cristalino POD TY"] = (df_josh["Cristalino 9LC TY"] > 0).astype(int)
    df_josh["Cristalino POD LY"] = (df_josh["Cristalino 9LC LY"] > 0).astype(int)
    df_josh["TK POD TY"] = (df_josh["TK 9LC TY"] > 0).astype(int)
    df_josh["TK POD LY"] = (df_josh["TK 9LC LY"] > 0).astype(int)

    # Overall POD for the full Casa Dragones portfolio.
    df_josh["Total CD POD TY"] = df_josh[
        ["Joven POD TY", "Blanco POD TY", "Añejo POD TY", "Reposado POD TY", "TK POD TY", "Cristalino POD TY"]
    ].any(axis=1).astype(int)
    df_josh["Total CD POD LY"] = df_josh[
        ["Joven POD LY", "Blanco POD LY", "Añejo POD LY", "Reposado POD LY", "TK POD LY", "Cristalino POD LY"]
    ].any(axis=1).astype(int)

    print()
    print("Calculating state ACV metrics...")

    # State ACV contribution calculations.
    state_total_acv_ty = df_flat.groupby("Account_State")["Product Universe_%ACV$"].sum().to_dict()
    df_josh["State TOTAL ACV TY"] = df_flat["Account_State"].map(state_total_acv_ty)
    df_josh["% of State ACV TY"] = (
        df_flat["Product Universe_%ACV$"] / df_josh["State TOTAL ACV TY"]
    ) * 100
    df_josh["State ACV TY"] = df_josh["% of State ACV TY"].where(df_josh["Total CD POD TY"] != 0, 0)
    df_josh["State ACV LY"] = df_josh["% of State ACV TY"].where(df_josh["Total CD POD LY"] != 0, 0)

    print()
    print("Adding number-of-labels mapping...")

    # Add number of labels from CoDist mapping.
    df_josh["Number of Labels"] = df_flat["Product Universe_CoDist"].apply(
        lambda x: codedist_to_labelnum.get(normalize_text(x), x) if pd.notna(x) else x
    )

    print()
    print("Finished business transformation.")
    print("-" * 60)
    print()
    return df_josh


# ==============================================================================
# 4) REFERENCE SHEETS FOR OUTPUT FILE
# ==============================================================================
def build_reference_sheets():
    """
    Build helper tabs (MAP and CoDist Information) for the exported workbook.
    """
    df_map = pd.DataFrame(
        {
            "State": list(state_to_region.keys()),
            "Region": list(state_to_region.values()),
            "SGWS Region": [state_to_sgws_region.get(state, "") for state in state_to_region.keys()],
        }
    )

    df_codist = pd.DataFrame(
        {
            "CoDist": list(codedist_to_labels.keys()),
            "Labels": list(codedist_to_labels.values()),
        }
    )
    df_codist["Number of Labels"] = df_codist["CoDist"].map(codedist_to_labelnum)
    return df_map, df_codist


# ==============================================================================
# 5) MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    # Standard input filename (same for every run).
    # Put this file in the project root folder.
    input_filename = "acv_data_export.xlsx"
    file_path = PROJECT_ROOT / input_filename
    header_start_row = 29

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}\n"
            "Place the file in the project root folder or update 'input_filename'."
        )

    print()
    print("=" * 60)
    print("Step A/4: Loading and flattening export file...")
    print("=" * 60)
    df_flat = load_excel_with_multiheader(file_path, header_start_row)

    print("=" * 60)
    print("Step B/4: Building business summary table...")
    print("=" * 60)
    df_josh_edits = josh_edits(df_flat)

    print("=" * 60)
    print("Step C/4: Building helper reference sheets...")
    print("=" * 60)
    df_map, df_codist = build_reference_sheets()

    print()
    print("=" * 60)
    print("Step D/4: Writing output workbook (this can take a few minutes)...")
    print("=" * 60)

    # Step D: Save all tabs into one output workbook.
    today = date.today().strftime("%b-%d-%Y")  # e.g. "Jun-16-2026"
    output_file = PROJECT_ROOT / f"ACV Report Summary {today}.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        # Commented out to speed up export time (largest sheet).
        # print("  - Writing sheet: original_data")
        # df_flat.to_excel(writer, sheet_name="original_data", index=False)
        print("  - Writing sheet: data_summary")
        df_josh_edits.to_excel(writer, sheet_name="data_summary", index=False)
        print("  - Writing sheet: MAP")
        df_map.to_excel(writer, sheet_name="MAP", index=False)
        print("  - Writing sheet: CoDist Information")
        df_codist.to_excel(writer, sheet_name="CoDist Information", index=False)

    print()
    print(f"Done. Output saved to: {output_file}")
    print()