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
uploaded_file = st.sidebar.file_uploader("Upload bi_logging.csv", type=["csv"])

# --- MAIN LOGIC ---
if uploaded_file:
    try:
        # Run pipeline: returns fact table, dims, and dashboard data
        df, dims, dashboard = run_pipeline(uploaded_file)

        # =============================
        # 🔢 KPI SECTION
        # =============================
        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Records", len(df))
        col2.metric("Total Themes", len(df["Theme / Topic"].unique()))
        col3.metric("Total Regions", len(df["Region impacted"].unique()))

        # =============================
        # 📊 SUMMARY TABLE
        # =============================
        st.subheader("Theme Summary")
        st.dataframe(dashboard["summary"], use_container_width=True)

        # =============================
        # 📈 TREND CHART
        # =============================
        st.subheader("Trend Over Time")

        if dashboard["trend"] is not None and not dashboard["trend"].empty:
            fig = px.line(
                dashboard["trend"],
                x="Date",
                y="count",
                color="Theme / Topic",
                title="Theme Mentions Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No Date column found or empty trend data.")

        # =============================
        # 🔥 HEATMAP
        # =============================
        st.subheader("Theme vs Region Heatmap")

        if dashboard["heatmap"] is not None and not dashboard["heatmap"].empty:
            plt.figure(figsize=(10, 5))
            sns.heatmap(dashboard["heatmap"], annot=True, fmt=".0f", cmap="coolwarm")
            st.pyplot(plt)
        else:
            st.warning("No Region impacted column found or empty heatmap data.")

        # =============================
        # 🔍 FILTERS (Executive view)
        # =============================
        st.subheader("Drilldown by Theme")

        theme_filter = st.selectbox(
            "Select Theme",
            df["Theme / Topic"].unique()
        )

        filtered_df = df[df["Theme / Topic"] == theme_filter]
        st.dataframe(filtered_df, use_container_width=True)

        st.success("Dashboard loaded successfully")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload a CSV file to begin")
