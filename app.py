import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Climate BI", layout="wide")
st.title("Climate BI")
st.markdown("Climate Risk Monitoring Prototype| Developed by SASOL Climate Team, 2026")

# -----------------------------
# LOAD FACT TABLE
# -----------------------------
uploaded_file = st.sidebar.file_uploader("Upload Fact Table CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # -----------------------------
    # TOP KPI CARDS
    # -----------------------------
    total_reports = len(df)
    high_urgency = df[df["Urgency_W"] >= 0.8].shape[0]

    risks_pct = round((df['Category']=="Risk").mean()*100,1)
    opp_pct = round((df['Category']=="Opportunity").mean()*100,1)
    trends_pct = round((df['Category']=="Trend").mean()*100,1)

    col1, col2, col3, col4, col5 = st.columns([1,1,2,1,1])
    col1.metric("Reports Logged", total_reports)
    col2.metric("High Urgency Alerts", high_urgency)
    col3.metric("Risks | Opportunities | Trends", f"{risks_pct}% | {opp_pct}% | {trends_pct}%")

    # SDG Tiles
    sdgs = {13:"green", 7:"orange", 9:"orange"}
    for i, (sdg, color) in enumerate(sdgs.items()):
        col4.markdown(
            f"<div style='background-color:{color}; color:white; padding:15px; text-align:center; border-radius:5px;'>SDG {sdg}</div>",
            unsafe_allow_html=True
        )

    # -----------------------------
    # TRENDS OVER TIME
    # -----------------------------
    st.subheader("Trends Over Time")
    trends_df = df.groupby([df['Date'].dt.to_period('M'), 'Category']).size().reset_index(name='Count')
    trends_df['Date'] = trends_df['Date'].dt.to_timestamp()
    fig_trends = px.line(trends_df, x='Date', y='Count', color='Category', markers=True)
    st.plotly_chart(fig_trends, use_container_width=True)

    # -----------------------------
    # GEOGRAPHIC IMPACT
    # -----------------------------
    st.subheader("Geographic Impact")
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
    urgency_df = df.groupby(['Urgency','Category']).size().unstack(fill_value=0)
    fig_urgency = px.bar(urgency_df, barmode='stack', title="Urgency by Category")
    st.plotly_chart(fig_urgency, use_container_width=True)

    # -----------------------------
    # INTELLIGENCE LOG
    # -----------------------------
    st.subheader("Intelligence Log")
    log_cols = ["Date","Headline","Category","Theme / Topic","SDGs","Urgency"]
    st.dataframe(df[log_cols].sort_values("Date", ascending=False), use_container_width=True)

else:
    st.info("Upload your generated fact_table.csv to begin")
