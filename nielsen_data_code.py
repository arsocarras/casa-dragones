import numpy as np
import pandas as pd


####### Important Maps for Data Cleaning #######
expression_map = {
        "CASA DRAGONES ANEJO TEQUILA": "Anejo",
        "CASA DRAGONES JOVEN TEQUILA": "Joven",
        "CASA DRAGONES BLANCO TEQUILA": "Blanco",
        "CASA DRAGONES REPOSADO TEQUILA": "Reposado"}

size_map = {
        "375ML": 0.375,
        "750ML": 0.750,} # in liters

##################################################

def load_data(file_path):
    """
    Load the raw data from the Excel file
    """
    raw_data = pd.read_excel(file_path, "Weekly Casa Dragones")
    return raw_data



def clean_data(raw_data):
    """
    Clean the raw data to prepare for analysis
    """
    clean_data = raw_data.copy()
    
    # 1) Create Expression Column for easy access
    clean_data["Expression"] = clean_data["ALC Brand Extension"].map(expression_map)

    # 2) Create Size Column in L
    clean_data["Size (in L)"] = clean_data["ALC Size"].map(size_map)

    # 3) Get Date from Week Number
    date_parts = clean_data["Time Periods"].str[-10:].str.split("-")
    clean_data["Year"] = date_parts.str[2].astype(int)
    clean_data["Month"] = date_parts.str[0].astype(int)
    clean_data["Day"] = date_parts.str[1].astype(int)

    clean_data["Date"] = pd.to_datetime(clean_data[["Year", "Month", "Day"]])

    # 4) Delete Unnecessary Columns
    clean_data = clean_data.drop(columns=["Time Periods", "ALC Brand Extension", "ALC Size"])

    # 5) Add in % Change Column for each metric
    cols_to_convert = [
        "Total $ Sales Change vs Year-Ago", "Total $ Sales YA",
        "Total EQ Unit Sales Change vs Year-Ago", "Total EQ Unit Sales YA",
        "Total TDP Change vs Year-Ago", "Total TDP YA",
        "% ACV (Max) Change vs Year-Ago", "% ACV (Max) YA",
        "Total Average Price Change vs Year-Ago", "Total Average Price YA",
        "Total Average EQ Price Change vs Year-Ago", "Total Average EQ Price YA"
    ]

    for col in cols_to_convert:
        clean_data[col] = pd.to_numeric(clean_data[col], errors="coerce")


    pairs = [
        ("Total $ Sales Change vs Year-Ago", "Total $ Sales YA", "Total $ Sales % Change vs Year Ago"),
        ("Total EQ Unit Sales Change vs Year-Ago", "Total EQ Unit Sales YA", "Total EQ Unit Sales % Change vs Year Ago"),
        ("Total TDP Change vs Year-Ago", "Total TDP YA", "Total TDP % Change vs Year Ago"),
        ("% ACV (Max) Change vs Year-Ago", "% ACV (Max) YA", "% ACV (Max) % Change vs Year-Ago"),
        ("Total Average Price Change vs Year-Ago", "Total Average Price YA", "Total Average Price % Change vs Year-Ago"),
        ("Total Average EQ Price Change vs Year-Ago", "Total Average EQ Price YA", "Total Average EQ Price % Change vs Year-Ago"),
    ]

    for num_col, den_col, out_col in pairs:
        clean_data[out_col] = clean_data[num_col].div(clean_data[den_col].replace(0, np.nan)).fillna(0)

    # 6) Sort by Date
    clean_data = clean_data.sort_values(by="Date").reset_index(drop=True)
    return clean_data




if __name__ == "__main__":
    file_path = "data/Casa Dragones Weekly Nielsen.xlsx"
    raw_data = load_data(file_path)
    cleaned_df = clean_data(raw_data)

    cleaned_df.to_excel("weekly_cleaned.xlsx", index=False)
