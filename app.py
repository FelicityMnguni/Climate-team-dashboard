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
st.markdown("Climate risk monitoring | Prototype by SASOL Climate Team")

# --- SIDEBAR ---
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload bi_logging.csv", type=["csv"])

if uploaded_file:
    try:
        # Run pipeline: fact table, dims, dashboard
        df, dims, dashboard = run_pipeline(uploaded_file)

        # =============================
        # 🔍 FILTERS
        # =============================
        # --- KPI CARDS ---
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", len(filtered_df))
        col2.metric("Total Themes", len(filtered_df["Theme"].unique()))
        col3.metric("Total Regions", len(filtered_df["Region"].unique()))
        col4.metric("Escalated Items", filtered_df["Escalation_Flag"].sum())

        st.subheader("Filters")
        theme_filter = st.selectbox(
            "Select Theme",
            ["All"] + df["Theme"].dropna().unique().tolist()
        )
        impact_filter = st.selectbox(
            "Select Potential Impact",
            ["All"] + df["Potential impact"].dropna().unique().tolist()
        )
        region_filter = st.selectbox(
            "Select Region",
            ["All"] + df["Region"].dropna().unique().tolist()
        )

        filtered_df = df.copy()
        if theme_filter != "All":
            filtered_df = filtered_df[filtered_df["Theme"] == theme_filter]
        if impact_filter != "All":
            filtered_df = filtered_df[filtered_df["Potential impact"] == impact_filter]
        if region_filter != "All":
            filtered_df = filtered_df[filtered_df["Region"] == region_filter]

        # --- INTERACTIVE TREND ---
        # --- INTERACTIVE BUBBLE TIMELINE WITH IMPACT ---
        st.subheader("Themes Over Time - Bubble Timeline with Potential Impact")

        if dashboard["trend"] is not None and not dashboard["trend"].empty:
            trend_data = dashboard["trend"].copy()
    
            # Ensure 'Potential impact' exists in trend data
            if "Potential impact" not in trend_data.columns:
                trend_data["Potential impact"] = "Mixed"  # fallback default
    
            # Filter themes if needed
            themes_selected = st.multiselect(
                "Select Themes to Display",
                options=trend_data["Theme"].unique(),
                default=trend_data["Theme"].unique()[:5]
            )
            trend_data = trend_data[trend_data["Theme"].isin(themes_selected)]
    
            # Bubble timeline: size = mentions, color = potential impact
            fig_bubble = px.scatter(
                trend_data,
                x="Date",
                y="Theme",
                size="count",
                color="Potential impact",
                hover_name="Theme",
                hover_data={"count": True, "Date": True, "Potential impact": True},
                size_max=40,
                color_discrete_map={
                    "Positive": "#2ca02c",  # green
                    "Negative": "#d62728",  # red
                     "Mixed": "#ff7f0e"      # orange
                },
                title="Hot Themes Over Time by Potential Impact"
            )
    
            fig_bubble.update_layout(
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="Date",
                yaxis_title="Theme",
                legend_title="Potential Impact",
                hovermode="closest"
            )
    
            st.plotly_chart(fig_bubble, use_container_width=True)
    
        else:
            st.warning("No trend data available for themes over time.")
                st.subheader("Themes Over Time - Interactive Bubble Timeline")

                if dashboard["trend"] is not None and not dashboard["trend"].empty:
                    trend_data = dashboard["trend"].copy()
    
                    # Optional: filter themes if too many
                    themes_selected = st.multiselect(
                        "Select Themes to Display",
                         options=trend_data["Theme"].unique(),
                         default=trend_data["Theme"].unique()[:5]  # show top 5 by default
                    )
                    trend_data = trend_data[trend_data["Theme"].isin(themes_selected)]
    
            # Plotly scatter for bubble timeline
            fig_bubble = px.scatter(
                trend_data,
                x="Date",
                y="Theme",
                size="count",          # bubble size = number of mentions
                color="Theme",         # each theme has a unique color
                hover_name="Theme",
                hover_data={"count": True, "Date": True},
                size_max=40,           # max bubble size
                title="Hot Themes Over Time (Bubble Timeline)"
            )
    
            fig_bubble.update_layout(
                yaxis={'categoryorder':'total ascending'},  # orders themes by total mentions
                xaxis_title="Date",
                yaxis_title="Theme",
                legend_title="Theme",
                hovermode="closest"
            )
    
        st.plotly_chart(fig_bubble, use_container_width=True)
    
        else:
            st.warning("No trend data available for themes over time.")

        # --- MAP: Hot Topics by Region (using counts, no Item) ---
        st.subheader("Hot Topics by Region")
        if not df.empty:
            map_data = (
                df.groupby(["Region", "Theme"])
                  .size()
                  .reset_index(name="count")
            )
            fig_map = px.scatter_geo(
                map_data,
                locations="Region",
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
        top_themes = filtered_df.groupby("Theme").size().reset_index(name="count").sort_values("count", ascending=False)
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
        st.subheader("Drilldown Table")
        st.dataframe(filtered_df, use_container_width=True)

        st.success("Dashboard loaded successfully")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload a CSV file to begin")
