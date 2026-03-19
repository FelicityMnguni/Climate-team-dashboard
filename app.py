import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

from pipeline.run_pipeline import run_pipeline

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Climate Team - Business Intelligence",
    layout="wide"
)

# --- HEADER ---
st.title("Climate Team - Business Intelligence")
st.markdown("Prototype for risk monitoring developed by SASOL Climate Team")

# --- SIDEBAR ---
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload bi_logging.csv", type=["csv"])

if uploaded_file:
    try:
        # Run pipeline: fact table, dims, dashboard
        df, dims, dashboard = run_pipeline(uploaded_file)

        # =============================
        # 🔢 KPI SECTION
        # =============================
        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(df))
        col2.metric("Total Themes", len(df["Topic"].unique()))
        col3.metric("Total Regions", len(df["Region impacted"].unique()))

        # =============================
        # 🔍 FILTERS
        # =============================
        st.subheader("Filters")
        theme_filter = st.selectbox(
            "Select Theme",
            ["All"] + df["Topic"].dropna().unique().tolist()
        )
        impact_filter = st.selectbox(
            "Select Potential Impact",
            ["All"] + df["Potential impact"].dropna().unique().tolist()
        )

        filtered_df = df.copy()
        if theme_filter != "All":
            filtered_df = filtered_df[filtered_df["Topic"] == theme_filter]
        if impact_filter != "All":
            filtered_df = filtered_df[filtered_df["Potential impact"] == impact_filter]

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
            # Highlight hot topics by color
            hot_topics = dashboard["trend"].groupby("Topic")["mentions"].sum().sort_values(ascending=False).head(5).index
            dashboard["trend"]["Hot"] = dashboard["trend"]["Topic"].apply(lambda x: "Hot" if x in hot_topics else "Normal")

            fig = px.line(
                dashboard["trend"],
                x="Date",
                y="mentions",
                color="Topic",
                line_dash="Hot",
                title="Theme Mentions Over Time (Hot Topics Highlighted)",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No Date column found or trend data is empty.")

        # =============================
        # 🌍 HEATMAP ON WORLD MAP
        # =============================
        st.subheader("Theme Mentions by Region (Interactive Map)")

        if dashboard["heatmap"] is not None and not dashboard["heatmap"].empty:
            heatmap_df = dashboard["heatmap"].reset_index().melt(
                id_vars="Topic",
                var_name="Region",
                value_name="Mentions"
            )

            fig = px.choropleth(
                heatmap_df,
                locations="Region",
                locationmode="country names",  # adjust if Region column has country names
                color="Mentions",
                hover_name="Topic",
                title="Theme Mentions by Region",
                color_continuous_scale="YlOrRd"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No Region impacted column found or heatmap data is empty.")

        # =============================
        # 🔍 DRILLDOWN TABLE
        # =============================
        st.subheader("Drilldown by Theme and Impact")
        st.dataframe(filtered_df, use_container_width=True)

        st.success("Dashboard loaded successfully")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload a CSV file to begin")
