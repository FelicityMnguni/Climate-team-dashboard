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
        if "count" not in filtered_df.columns:
            filtered_df["count"] = 1  # each row counts as 1
        
        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')

        # Aggregate counts per Theme per Date
        theme_trends = (
            filtered_df.groupby(['Date', 'Theme'])['count']
            .sum()
            .reset_index()
        )

        if theme_trends.empty:
            st.warning("No data available to display trends.")
        else:
            # Identify emerging themes: calculate last 7-day growth
            recent_counts = (
                theme_trends[theme_trends['Date'] >= (theme_trends['Date'].max() - pd.Timedelta(days=7))]
                .groupby('Theme')['count']
                .sum()
                .reset_index()
            )
            # Top 5 emerging themes by growth
            top_emerging = recent_counts.sort_values('count', ascending=False).head(5)['Theme'].tolist()

            # Plot line chart
            fig_trend = px.line(
                theme_trends,
                x='Date',
                y='count',
                color='Theme',
                line_group='Theme',
                title='Theme Trends Over Time',
                hover_data={'Theme':True, 'count':True}
            )

            # Highlight emerging themes by increasing line width
            for trace in fig_trend.data:
                if trace.name in top_emerging:
                    trace.update(line=dict(width=4))  # thicker line for emerging
                else:
                    trace.update(line=dict(width=1, dash='dot', color='lightgray'))  # de-emphasize others

            st.plotly_chart(fig_trend, use_container_width=True)
        

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
