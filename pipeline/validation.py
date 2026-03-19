# validation.py
import pandas as pd
import os

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

def log_invalid(df, filename):
    # Do nothing
    pass
