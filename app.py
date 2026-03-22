import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- CONFIG ---
st.set_page_config(page_title="Climate BI, layout="wide")

st.title("Climate BI")
st.markdown("Climate BI prototype| by SASOL Climate Team, 2026")

# =============================
# 📂 LOAD FACT TABLE
# =============================
uploaded_file = st.sidebar.file_uploader("Upload Fact Table", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Ensure correct types
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # =============================
    # 🔍 FILTERS
    # =============================
    st.sidebar.header("Filters")

    theme_filter = st.sidebar.selectbox(
        "Theme",
        ["All"] + df["Theme / Topic"].dropna().unique().tolist()
    )

    region_filter = st.sidebar.selectbox(
        "Region",
        ["All"] + df["Region impacted"].dropna().unique().tolist()
    )

    escalation_filter = st.sidebar.selectbox(
        "Escalation",
        ["All", "Escalated Only"]
    )

    # Apply filters
    filtered_df = df.copy()

    if theme_filter != "All":
        filtered_df = filtered_df[filtered_df["Theme / Topic"] == theme_filter]

    if region_filter != "All":
        filtered_df = filtered_df[filtered_df["Region impacted"] == region_filter]

    if escalation_filter == "Escalated Only":
        filtered_df = filtered_df[filtered_df["Escalation_Flag"] == True]

    # =============================
    # 🔢 KPI CARDS (NOW INTELLIGENT)
    # =============================
    st.subheader("Key Risk Signals")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Signals", len(filtered_df))
    col2.metric("Avg IMS (Materiality)", round(filtered_df["IMS"].mean(), 2))
    col3.metric("Avg Acceleration", round(filtered_df["Acceleration"].mean(), 2))
    col4.metric("Escalations", int(filtered_df["Escalation_Flag"].sum()))

    # =============================
    # 📈 EMERGING THEMES (ACCELERATION-DRIVEN)
    # =============================
    st.subheader("Emerging Themes (Acceleration-Based)")

    emerging = (
        filtered_df.groupby("Theme / Topic")["Acceleration"]
        .mean()
        .reset_index()
        .sort_values("Acceleration", ascending=False)
        .head(10)
    )

    fig_emerging = px.bar(
        emerging,
        x="Theme / Topic",
        y="Acceleration",
        title="Top Emerging Themes",
        text_auto=True
    )

    st.plotly_chart(fig_emerging, use_container_width=True)

    # =============================
    # 🌍 MAP (NOW IMS-WEIGHTED)
    # =============================
    st.subheader("Geographic Risk Intensity (IMS Weighted)")

    map_data = (
        filtered_df.groupby("Region impacted")["IMS"]
        .mean()
        .reset_index()
    )

    fig_map = px.choropleth(
        map_data,
        locations="Region impacted",
        locationmode="country names",
        color="IMS",
        hover_name="Region impacted",
        color_continuous_scale="Reds",
        title="Average Risk Materiality by Region"
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # =============================
    # 🔥 HEATMAP (ESCALATION-BASED)
    # =============================
    st.subheader("Escalation Hotspots")

    heat_data = filtered_df.pivot_table(
        index="Theme / Topic",
        columns="Region impacted",
        values="Escalation_Flag",
        aggfunc="sum",
        fill_value=0
    )

    fig_heat = px.imshow(
        heat_data,
        color_continuous_scale="Reds",
        labels={"color": "Escalation Intensity"}
    )

    st.plotly_chart(fig_heat, use_container_width=True)

    # =============================
    # ⚠️ INTERNAL RISK LINKAGE
    # =============================
    st.subheader("Internal Risk Linkage")

    linkage = (
        filtered_df.groupby("Theme / Topic")["Internal_Link_Flag"]
        .mean()
        .reset_index()
        .sort_values("Internal_Link_Flag", ascending=False)
        .head(10)
    )

    fig_link = px.bar(
        linkage,
        x="Theme / Topic",
        y="Internal_Link_Flag",
        title="Themes Most Linked to Internal Risks"
    )

    st.plotly_chart(fig_link, use_container_width=True)

    # =============================
    # 📋 DRILLDOWN
    # =============================
    st.subheader("Detailed Intelligence View")

    st.dataframe(
        filtered_df.sort_values("IMS", ascending=False),
        use_container_width=True
    )

    st.success("Dashboard loaded successfully")

else:
    st.info("Upload your generated fact_table.csv to begin")
