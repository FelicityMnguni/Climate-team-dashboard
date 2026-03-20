import streamlit as st 
import pandas as pd
import plotly.express as px
import numpy as np 
from pipeline.run_pipeline import run_pipeline

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Climate Team Executive Dashboard",
    layout="wide"
)

# --- HEADER ---
st.title("Climate Team Executive Dashboard")
st.markdown("Climate risk monitoring | Prototype by SASOL Climate Team")

# --- SIDEBAR ---
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload bi_logging.csv", type=["csv"])

if uploaded_file:
    try:
        # Run pipeline
        df, dims, dashboard = run_pipeline(uploaded_file)

        # =============================
        # 🔍 SIDEBAR FILTERS
        # =============================
        st.sidebar.subheader("Filters")

        theme_filter = st.sidebar.selectbox(
            "Theme",
            ["All"] + df["Theme"].dropna().unique().tolist()
        )

        impact_filter = st.sidebar.selectbox(
            "Potential Impact",
            ["All", "Positive", "Negative"]  # force only 2 categories
        )

        region_filter = st.sidebar.selectbox(
            "Region",
            ["All"] + df["Region"].dropna().unique().tolist()
        )

        # Apply filters
        filtered_df = df.copy()

        if theme_filter != "All":
            filtered_df = filtered_df[filtered_df["Theme"] == theme_filter]

        if impact_filter != "All":
            filtered_df = filtered_df[filtered_df["Potential impact"].isin(["Positive", "Negative"])]
            filtered_df = filtered_df[filtered_df["Potential impact"] == impact_filter]

        if region_filter != "All":
            filtered_df = filtered_df[filtered_df["Region"] == region_filter]

        # =============================
        # 🔢 KPI CARDS (COLOR CODED)
        # =============================
        st.subheader("Key Metrics")

        total_records = len(filtered_df)
        total_themes = filtered_df["Theme"].nunique()
        total_regions = filtered_df["Region"].nunique()
        escalated = filtered_df["Escalation_Flag"].sum()

        # Professional colors for card backgrounds
        kpi_bg_colors = {
            "records": "#1565C0",    # Deep blue
            "themes": "#2E7D32",     # Deep green
            "regions": "#FFB300",    # Amber / gold
            "escalated": "#C62828",  # Deep red
        }

        # Optional: light gray card style for spacing and rounded corners
        card_style = "padding:20px; border-radius:10px; text-align:center; color:white; font-size:20px; font-weight:bold;"

        col1, col2, col3, col4 = st.columns(4)

        col1.markdown(
             f"<div style='background-color:{kpi_bg_colors['records']}; {card_style}'>Total Records<br>{total_records}</div>",
             unsafe_allow_html=True
        )
        col2.markdown(
            f"<div style='background-color:{kpi_bg_colors['themes']}; {card_style}'>Total Themes<br>{total_themes}</div>",
            unsafe_allow_html=True
        )
        col3.markdown(
            f"<div style='background-color:{kpi_bg_colors['regions']}; {card_style}'>Total Regions<br>{total_regions}</div>",
            unsafe_allow_html=True
        )
        col4.markdown(
            f"<div style='background-color:{kpi_bg_colors['escalated']}; {card_style}'>Escalated Items<br>{escalated}</div>",
            unsafe_allow_html=True
        )

        # =============================
        # 📈 BUBBLE TIMELINE (FILTERED)
        # =============================
        st.subheader("Emerging themes")
        # Ensure 'Date' is datetime
        trend_data['Date'] = pd.to_datetime(trend_data['Date'], errors='coerce')

        # Ensure 'count' is numeric and has a minimum of 1
        trend_data['count'] = pd.to_numeric(trend_data.get('count', 1), errors='coerce').fillna(1)
        trend_data.loc[trend_data['count'] <= 0, 'count'] = 1

        # Check if there's data to plot
        if trend_data.empty:
            st.warning("No data available to display.")
        else:
            # Simple bubble chart
            fig_bubble = px.scatter(
                trend_data,
                x='Date',
                y='Theme',
                size='count',
                size_max=80,
                title='Themes Over Time'
            )

            st.plotly_chart(fig_bubble, use_container_width=True)
        

        # =============================
        # 🌍 MAP
        # =============================
        #st.subheader("Hot Topics by Region")

        themes = filtered_df["Theme"].unique()
        selected_themes = st.multiselect("Select Themes to Display on Map", options=themes, default=themes)

        # Filter data for selected themes
        map_data = filtered_df[filtered_df["Theme"].isin(selected_themes)]

        if map_data.empty:
           st.warning("No map data for the selected themes.")
        else:
            # Example: scatter map if you have lat/lon columns
            fig_map = px.scatter_mapbox(
              map_data,
              lat="Latitude",          # Replace with your latitude column
              lon="Longitude",         # Replace with your longitude column
              hover_name="Theme",
              hover_data=["Region", "count"],
              size="count",
              size_max=25,
              color="Theme",           # Optional: color by theme for clarity
              zoom=5)

            fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
    

        # =============================
        # 🔥 HEATMAP
        # =============================
        st.subheader("Escalation")

        if not filtered_df.empty:
            heat_data = (
                filtered_df.groupby(["Theme", "Region"])["Escalation_Flag"]
                .sum()
                .reset_index()
                .pivot(index="Theme", columns="Region", values="Escalation_Flag")
                .fillna(0)
            )

            heat_display = heat_data.replace(0, np.nan)

            fig_heat = px.imshow(
                heat_display,
                color_continuous_scale="RdYlGn",
                labels={"x":"Region", "y":"Theme", "color":"Escalations"},
                template="plotly_white"
            )

            fig_heat.update_traces(
                colorscale=[[0, "lightgrey"], [0.00001, "yellow"], [1, "red"]]
            )

            st.plotly_chart(fig_heat, use_container_width=True)

        # =============================
        # 📊 TOP THEMES (CLEAN)
        # =============================
        st.subheader("Top Hot Themes")

        top_themes = (
            filtered_df.groupby("Theme")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(10)
        )

        fig_bar = px.bar(
            top_themes,
            x="Theme",
            y="count",
            text="count",
            color_discrete_sequence=["#1f77b4"]  # single color
        )

        fig_bar.update_layout(
            yaxis_title="",
            xaxis_title="",
            showlegend=False
        )

        st.plotly_chart(fig_bar, use_container_width=True)

        # =============================
        # 📋 DRILLDOWN
        # =============================
        st.subheader("Drilldown Table")
        st.dataframe(filtered_df, use_container_width=True)

        st.success("Dashboard loaded successfully")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload a CSV file to begin")
