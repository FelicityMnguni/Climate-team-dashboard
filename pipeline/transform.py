import pandas as pd

def transform_data(df):
    """Clean and standardize data"""

    df = df.copy()

    # Standardise column names
    df.columns = df.columns.str.strip()

    # Convert date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Ensure numeric risk score
    if "Risk Score" in df.columns:
        df["Risk Score"] = pd.to_numeric(df["Risk Score"], errors="coerce")

    # Fill missing categories
    df["Theme / Topic"] = df.get("Theme / Topic", "Unknown").fillna("Unknown")
    df["Region"] = df.get("Region", "Unknown").fillna("Unknown")

    return df
