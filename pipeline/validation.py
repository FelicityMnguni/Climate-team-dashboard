# validation.py
import pandas as pd
from config import ERROR_LOG_PATH
import os

def log_invalid(df, filename):
    if not os.path.exists(ERROR_LOG_PATH):
        os.makedirs(ERROR_LOG_PATH)
    df.to_csv(f"{ERROR_LOG_PATH}{filename}", index=False)

def validate_bi(df):
    required = ["Date","Theme / Topic","Horizon","Urgency","Region impacted"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing BI columns: {missing}")

def validate_horizon(df):
    valid = ["H1","H2","H3"]
    invalid_rows = df[~df["Horizon"].isin(valid)]
    if len(invalid_rows) > 0:
        log_invalid(invalid_rows, "invalid_horizon.csv")
        df = df[df["Horizon"].isin(valid)]
    return df

def validate_urgency(df):
    valid = ["Very high","High","Medium","Low"]
    invalid_rows = df[~df["Urgency"].isin(valid)]
    if len(invalid_rows) > 0:
        log_invalid(invalid_rows, "invalid_urgency.csv")
        df = df[df["Urgency"].isin(valid)]
    return df
