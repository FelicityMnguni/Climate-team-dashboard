# app.py
import sys
import os
sys.path.append(os.path.abspath("."))

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from pipeline.run_pipeline import run_pipeline

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Executive Intelligence Dashboard",
    layout="wide"
)

# --- HEADER ---
st.title("Executive Intelligence Dashboard")
st.markdown("Prototype for AI-driven risk and theme monitoring")

# --- SIDEBAR ---
st.sidebar.header("Upload Data")
bi_file = st.sidebar.file_uploader("Upload BI Logging CSV", type=["csv"])
risk_file = st.sidebar.file_uploader("Upload Internal Risks CSV", type=["csv"])

# --- MAIN LOGIC ---
if bi_file and risk_file:

    try:
        # Run full ETL pipeline
        fact, dims, dashboard = run_pipeline(bi_file, risk_file)
        df = fact  # Use the fact table for metrics and drilldown

        # =============================
        # 🔢 KPI SECTION
        # =============================
        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Records", len(df))
        col2.metric("Avg Risk", round(df["Risk"].mean(), 2))
        col3.metric("Max Risk", round(df["Risk"].max(), 2))

        # =============================
        # 📊 SUMMARY TABLE
        # =============================
        st.subheader("Theme Summary")
        st.dataframe(dashboard["summary"], use_container_width=True)

        # =============================
        # 📈 TREND CHART
        # =============================
        st.subheader("Risk Trends")
        if dashboard["trend"] is not None:
            fig = px.line(
                dashboard["trend"],
                x="Date",
                y="risk",
                color="Theme / Topic",
                title="Risk Trends Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No trend data available. Check Date column.")

        # =============================
        # 🔥 HEATMAP
        # =============================
        st.subheader("Risk Heatmap (Theme vs Region)")
        if dashboard["heatmap"] is not None:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.heatmap(dashboard["heatmap"], annot=True, fmt=".1f", ax=ax)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("No heatmap data available. Check Region column.")

        # =============================
        # 🔍 FILTERS (Executive view)
        # =============================
        st.subheader("Drilldown")
        df["Theme / Topic"] = df["Theme / Topic"].fillna("Unknown")  # ensure no NaNs
        theme_filter = st.selectbox(
            "Select Theme",
            df["Theme / Topic"].unique()
        )

        filtered_df = df[df["Theme / Topic"] == theme_filter]
        st.dataframe(filtered_df, use_container_width=True)

        st.success("Dashboard loaded successfully!")

    except Exception as e:
        st.error(f"Error running pipeline: {e}")

else:
    st.info("Upload both BI logging and Internal Risks CSVs to begin.")
