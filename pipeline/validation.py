def validate_data(df):
    """Basic validation checks"""

    required_cols = ["Theme / Topic", "Risk Score"]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = df.dropna(subset=["Risk Score"])

    return df
