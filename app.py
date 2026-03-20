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

        col1, col2, col3, col4 = st.columns(4)

        col1.markdown(f"<h3 style='color:#1f77b4'>Total Records<br>{total_records}</h3>", unsafe_allow_html=True)
        col2.markdown(f"<h3 style='color:#9467bd'>Total Themes<br>{total_themes}</h3>", unsafe_allow_html=True)
        col3.markdown(f"<h3 style='color:#17becf'>Total Regions<br>{total_regions}</h3>", unsafe_allow_html=True)
        col4.markdown(f"<h3 style='color:#d62728'>Escalated Items<br>{escalated}</h3>", unsafe_allow_html=True)

        # =============================
        # 📈 BUBBLE TIMELINE (FILTERED)
        # =============================
        st.subheader("Timeline with Potential Impact")

        if dashboard["trend"] is not None and not dashboard["trend"].empty:
            trend_data = dashboard["trend"].copy()

            # Clean + enforce consistency
            trend_data["count"] = pd.to_numeric(trend_data["count"], errors="coerce").fillna(1)
            trend_data["Date"] = pd.to_datetime(trend_data["Date"], errors="coerce")
            trend_data = trend_data.dropna(subset=["Date"])

            # Ensure only Positive/Negative in trend_data
            if "Potential impact" in trend_data.columns:
                trend_data = trend_data[trend_data["Potential impact"].isin(["Positive", "Negative"])]

            # Apply SAME filters to trend data
            if theme_filter != "All":
                trend_data = trend_data[trend_data["Theme"] == theme_filter]

            if impact_filter != "All" and "Potential impact" in trend_data.columns:
                trend_data = trend_data[trend_data["Potential impact"] == impact_filter]

            if trend_data.empty:
                st.warning("No data available for selected filters.")
            else:
                fig_bubble = px.scatter(
                    trend_data,
                    x="Date",
                    y="Theme",
                    size="count",
                    color="Potential impact" if "Potential impact" in trend_data.columns else None,
                    size_max=80,
                    color_discrete_map={
                        "Positive": "#2ca02c",
                        "Negative": "#d62728"
                    },
                    title="Hot Themes Over Time"
                )

                fig_bubble.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    xaxis_title="Date",
                    yaxis_title="",
                    legend_title="Impact",
                    hovermode="closest"
                )

                st.plotly_chart(fig_bubble, use_container_width=True)
        else:
            st.warning("No trend data available.")

        # =============================
        # 🌍 MAP
        # =============================
        st.subheader("Hot Topics by Region")

        if not filtered_df.empty:
            map_data = (
                filtered_df.groupby(["Region", "Theme"])
                .size()
                .reset_index(name="count")
            )

            fig_map = px.scatter_geo(
                map_data,
                locations="Region",
                locationmode="country names",
                color="Theme",
                size="count",
                projection="natural earth"
            )

            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No region data available.")

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
