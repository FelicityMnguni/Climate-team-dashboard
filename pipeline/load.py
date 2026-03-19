# pipeline/load.py
def prepare_dashboard_data(df):
    """Prepare aggregated datasets for dashboard using Theme from fact table"""

    # Ensure column names are clean
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Summary metrics
    summary = df.groupby("Theme").agg(
        count=("InternalRiskKey", "count")  # use any non-dropped column
    ).reset_index()

    # Trend data
    trend = None
    if "Date" in df.columns:
        trend = df.groupby(["Date", "Theme"]).agg(
            count=("InternalRiskKey", "count")
        ).reset_index()

    # Heatmap data
    heatmap = None
    if "RegionKey" in df.columns:
        heatmap = df.pivot_table(
            index="Theme",
            columns="Region",
            values="InternalRiskKey",
            aggfunc="count"
        )

    return {
        "summary": summary,
        "trend": trend,
        "heatmap": heatmap
    }
