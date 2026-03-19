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
        df, dashboard = run_pipeline(uploaded_file)

        # =============================
        # 🔢 KPI SECTION
        # =============================
        st.subheader("Key Metrics")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Records", len(df))
        col2.metric("Avg Risk Score", round(df["Risk Score"].mean(), 2))
        col3.metric("Max Risk Score", round(df["Risk Score"].max(), 2))

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
            st.warning("No Date column found.")

        # =============================
        # 🔥 HEATMAP
        # =============================
        st.subheader("Risk Heatmap (Theme vs Region)")

        if dashboard["heatmap"] is not None:
            plt.figure(figsize=(10, 5))
            sns.heatmap(dashboard["heatmap"], annot=True, fmt=".1f")
            st.pyplot(plt)
        else:
            st.warning("No Region column found.")

        # =============================
        # 🔍 FILTERS (Executive view)
        # =============================
        st.subheader("Drilldown")

        theme_filter = st.selectbox(
            "Select Theme",
            df["Theme / Topic"].unique()
        )

        filtered_df = df[df["Theme / Topic"] == theme_filter]
        st.dataframe(filtered_df)

        st.success("Dashboard loaded successfully")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload a CSV file to begin")