import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Climate BI", layout="wide")
st.title("Climate BI")
st.markdown("Climate Risk Monitoring Prototype | Developed by SASOL Climate Team, 2026")

# -----------------------------
# LOAD FACT TABLE
# -----------------------------
uploaded_file = st.sidebar.file_uploader("Upload Fact Table CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Ensure expected columns exist
    expected_cols = ["Date","Category","IMS","Theme / Topic","Region impacted","Urgency","Urgency_W","SDGs","Headline"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = np.nan

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # -----------------------------
    # TOP KPI CARDS
    # -----------------------------
    total_reports = len(df)
    high_urgency = df[df.get("Urgency_W", 0) >= 0.8].shape[0]

    risks_pct = round((df.get('Category', '') == "Risk").mean() * 100, 1)
    opp_pct = round((df.get('Category', '') == "Opportunity").mean() * 100, 1)
    trends_pct = round((df.get('Category', '') == "Trend").mean() * 100, 1)

    col1, col2, col3, col4, col5 = st.columns([1,1,2,1,1])
    col1.metric("Reports Logged", total_reports)
    col2.metric("High Urgency Alerts", high_urgency)
    col3.metric("Risks | Opportunities | Trends", f"{risks_pct}% | {opp_pct}% | {trends_pct}%")

    # -----------------------------
    # DYNAMIC SDG TILES
    # -----------------------------
    st.subheader("SDGs")
    if "SDGs" in df.columns and df["SDGs"].notna().any():
        unique_sdgs = pd.Series(df["SDGs"].dropna().astype(str).str.split(",").sum()).unique()
        sdg_colors = px.colors.qualitative.Pastel
        sdg_html = ""
        for i, sdg in enumerate(unique_sdgs):
            color = sdg_colors[i % len(sdg_colors)]
            sdg_html += f"<div style='background-color:{color}; color:black; padding:10px; margin:2px; display:inline-block; border-radius:5px;'>SDG {sdg.strip()}</div>"
        col4.markdown(sdg_html, unsafe_allow_html=True)
    else:
        col4.markdown("<div style='padding:10px;'>No SDGs reported</div>", unsafe_allow_html=True)

    # -----------------------------
    # TRENDS OVER TIME (WEEKLY)
    # -----------------------------
    st.subheader("Trends Over Time (Weekly)")
    if not df.empty and "Category" in df.columns:
        trends_df = df.groupby([df['Date'].dt.to_period('W'), 'Category']).size().reset_index(name='Count')
        trends_df['Date'] = trends_df['Date'].dt.start_time
        fig_trends = px.line(trends_df, x='Date', y='Count', color='Category', markers=True)
        st.plotly_chart(fig_trends, use_container_width=True)

    # -----------------------------
    # GEOGRAPHIC IMPACT
    # -----------------------------
    st.subheader("Geographic Impact")
    if "Region impacted" in df.columns and "IMS" in df.columns:
        map_df = df.groupby("Region impacted")["IMS"].mean().reset_index()
        fig_map = px.choropleth(
            map_df,
            locations="Region impacted",
            locationmode="country names",
            color="IMS",
            color_continuous_scale="Greens",
            title="Average Risk Materiality by Region"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # -----------------------------
    # KEY THEMES
    # -----------------------------
    st.subheader("Key Themes")
    if "Theme / Topic" in df.columns and "IMS" in df.columns:
        top_themes = df.groupby("Theme / Topic")["IMS"].mean().sort_values(ascending=False).head(6)
        theme_colors = ["#e63946","#2a9d8f","#f4a261","#457b9d","#f1faee","#a8dadc"]
        theme_html = ""
        for i, theme in enumerate(top_themes.index):
            color = theme_colors[i % len(theme_colors)]
            theme_html += f"<div style='background-color:{color}; color:white; padding:10px; margin:2px; display:inline-block; border-radius:5px;'>{theme}</div>"
        st.markdown(theme_html, unsafe_allow_html=True)

    # -----------------------------
    # URGENCY BREAKDOWN
    # -----------------------------
    st.subheader("Urgency Breakdown")
    if "Urgency" in df.columns and "Category" in df.columns:
        urgency_df = df.groupby(['Urgency','Category']).size().unstack(fill_value=0)
        fig_urgency = px.bar(urgency_df, barmode='stack', title="Urgency by Category")
        st.plotly_chart(fig_urgency, use_container_width=True)

    # -----------------------------
    # INTELLIGENCE LOG
    # -----------------------------
    st.subheader("Intelligence Log")
    log_cols = ["Date","Headline","Category","Theme / Topic","SDGs","Urgency"]
    existing_cols = [col for col in log_cols if col in df.columns]
    st.dataframe(df[existing_cols].sort_values("Date", ascending=False), use_container_width=True)

else:
    st.info("Upload your generated fact_table.csv to begin")
