# pipeline/load.py
def prepare_dashboard_data(df):
    """Prepare aggregated datasets for dashboard without Risk Score"""

    # Ensure column names are clean
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Use Item count instead of Risk Score
    summary = df.groupby("Topic").agg(
        count=("Item", "count")
    ).reset_index()

    # Trend data
    trend = None
    if "Date" in df.columns:
        trend = df.groupby(["Date", "Topic"]).agg(
            count=("Item", "count")
        ).reset_index()

    # Heatmap data
    heatmap = None
    if "Region impacted" in df.columns:
        heatmap = df.pivot_table(
            index="Topic",
            columns="Region impacted",
            values="Item",
            aggfunc="count"
        )

    return {
        "summary": summary,
        "trend": trend,
        "heatmap": heatmap
    }
