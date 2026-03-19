def prepare_dashboard_data(df):
    """Prepare aggregated datasets for dashboard"""

    # Summary metrics
    summary = df.groupby("Theme / Topic").agg(
        avg_risk=("Risk Score", "mean"),
        max_risk=("Risk Score", "max"),
        count=("Risk Score", "count")
    ).reset_index()

    # Trend data
    trend = None
    if "Date" in df.columns:
        trend = df.groupby(["Date", "Theme / Topic"]).agg(
            risk=("Risk Score", "mean")
        ).reset_index()

    # Heatmap data
    heatmap = None
    if "Region" in df.columns:
        heatmap = df.pivot_table(
            index="Theme / Topic",
            columns="Region",
            values="Risk Score",
            aggfunc="mean"
        )

    return {
        "summary": summary,
        "trend": trend,
        "heatmap": heatmap
    }
