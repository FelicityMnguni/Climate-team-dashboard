import streamlit as st
import pandas as pd
import plotly.express as px

from pipeline.run_pipeline import run_pipeline

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Climate Team Executive Dashboard",
    layout="wide"
)

# --- HEADER ---
st.title("Climate Team Executive Dashboard")
st.markdown("AI-driven risk monitoring prototype by SASOL Climate Team")

# --- SIDEBAR ---
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload bi_logging.csv", type=["csv"])

if uploaded_file:
    try:
        df, dims, dashboard = run_pipeline(uploaded_file)

        # --- KPI CARDS ---
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", len(df))
        col2.metric("Total Themes", len(df["Theme"].unique()))
        col3.metric("Total Regions", len(df["Region"].unique()))
        col4.metric("Escalated Items", df["Escalation_Flag"].sum())

        # --- INTERACTIVE TREND ---
        st.subheader("Trends Over Time")
        if dashboard["trend"] is not None and not dashboard["trend"].empty:
            themes_selected = st.multiselect(
                "Select Themes to Display",
                options=dashboard["trend"]["Theme"].unique(),
                default=dashboard["trend"]["Theme"].unique()[:3]
            )
            trend_data = dashboard["trend"][dashboard["trend"]["Theme"].isin(themes_selected)]
            fig_trend = px.line(
                trend_data,
                x="Date",
                y="count",
                color="Theme",
                hover_data=["count"],
                title="Theme Mentions Over Time"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("No Date data for trends.")

        # --- MAP: Hot Topics by Region ---
        st.subheader("Hot Topics by Region")
        if not df.empty:
            # Assuming 'Region' column contains recognizable location names
            map_data = df.groupby(["Region","Theme"]).agg(count=("Item","count")).reset_index()
            fig_map = px.scatter_geo(
                map_data,
                locations="Region",      # Use country or region codes
                locationmode="country names",
                color="Theme",
                size="count",
                hover_name="Theme",
                hover_data=["count"],
                projection="natural earth",
                title="Hot Topics Across Regions"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No region data available for map.")

        # --- HEATMAP ---
        st.subheader("Theme vs Region Heatmap")
        if dashboard["heatmap"] is not None and not dashboard["heatmap"].empty:
            fig_heat = px.imshow(
                dashboard["heatmap"],
                text_auto=True,
                color_continuous_scale="RdYlGn",
                aspect="auto",
                labels={"x":"Region", "y":"Theme", "color":"Count"}
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.warning("No heatmap data available.")

        # --- HOT TOPICS BAR CHART ---
        st.subheader("Top Hot Themes")
        top_themes = df.groupby("Theme").agg(count=("Item","count")).reset_index().sort_values("count", ascending=False)
        fig_bar = px.bar(
            top_themes.head(10),
            x="Theme",
            y="count",
            color="count",
            text="count",
            title="Top 10 Hot Themes"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- DRILLDOWN TABLE ---
        st.subheader("Drilldown by Theme and Region")
        theme_filter = st.selectbox("Select Theme", df["Theme"].unique())
        region_filter = st.selectbox("Select Region", df["Region"].unique())
        filtered_df = df[(df["Theme"] == theme_filter) & (df["Region"] == region_filter)]
        st.dataframe(filtered_df, use_container_width=True)

        st.success("Dashboard loaded successfully")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload a CSV file to begin")
