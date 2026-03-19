import pandas as pd

def extract_data(file):
    """Extract data from uploaded CSV"""
    df = pd.read_csv(file)
    return df