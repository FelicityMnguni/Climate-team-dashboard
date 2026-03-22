import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry

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
    expected_cols = ["Date","Category","IMS","Theme / Topic","Region impacted",
                     "Urgency","Urgency_W","SDGs","Potential impact","Acceleration","Source"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = np.nan

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Urgency"] = df["Urgency"].fillna("Unknown")
    df["Category"] = df["Category"].fillna("Other")
    df["Acceleration"] = pd.to_numeric(df["Acceleration"], errors="coerce").fillna(1)
    df["IMS"] = pd.to_numeric(df["IMS"], errors="coerce").fillna(0)

    # -----------------------------
    # DERIVED FIELDS
    # -----------------------------
    df["Weighted_Risk"] = df["IMS"] * df["Acceleration"]

    def classify_source(s):
        if pd.isna(s):
            return "External"
        s = str(s).lower()
        if "internal" in s:
            return "Internal"
        elif "short" in s:
            return "WEF Short Term"
        elif "long" in s:
            return "WEF Long Term"
        else:
            return "External"

    df["Source_Type"] = df["Source"].apply(classify_source)

    # -----------------------------
    # FILTERS
    # -----------------------------
    st.sidebar.subheader("Filters")
    selected_category = st.sidebar.multiselect("Category", df["Category"].unique(), default=df["Category"].unique())
    selected_urgency = st.sidebar.multiselect("Urgency", df["Urgency"].unique(), default=df["Urgency"].unique())
    selected_impact = st.sidebar.multiselect("Potential Impact", df["Potential impact"].dropna().unique(), default=df["Potential impact"].dropna().unique())

    filtered_df = df[
        df["Category"].isin(selected_category) &
        df["Urgency"].isin(selected_urgency) &
        df["Potential impact"].isin(selected_impact)
    ]

    # -----------------------------
    # KPI CARDS
    # -----------------------------
    total_reports = len(filtered_df)
    high_urgency = filtered_df[filtered_df.get("Urgency_W",0) >= 0.8].shape[0]

    category_counts = filtered_df["Category"].value_counts()
    risks_count = category_counts.get("Risk",0)
    opp_count = category_counts.get("Opportunity",0)
    trend_count = category_counts.get("Trend",0)

    card_data = [
        {"label":"Reports Logged","value":total_reports,"color":"#457b9d"},
        {"label":"High Urgency Alerts","value":high_urgency,"color":"#e63946"},
        {"label":"Risks","value":risks_count,"color":"#f94144"},
        {"label":"Opportunities","value":opp_count,"color":"#f3722c"},
        {"label":"Trends","value":trend_count,"color":"#90be6d"}
    ]

    row1 = st.columns(2)
    for col, card in zip(row1, card_data[:2]):
        col.markdown(f"<div style='background:{card['color']};padding:30px;border-radius:12px;color:white;text-align:center'><h3>{card['label']}</h3><h1>{card['value']}</h1></div>", unsafe_allow_html=True)

    row2 = st.columns(3)
    for col, card in zip(row2, card_data[2:]):
        col.markdown(f"<div style='background:{card['color']};padding:20px;border-radius:12px;color:white;text-align:center'><h4>{card['label']}</h4><h2>{card['value']}</h2></div>", unsafe_allow_html=True)

    # -----------------------------
    # WEEKLY TRENDS
    # -----------------------------
    st.subheader("Weekly Trends")
    df_valid = filtered_df.dropna(subset=["Date","Category"])
    if not df_valid.empty:
        trends_df = df_valid.groupby([df_valid['Date'].dt.to_period('W'), 'Category']).size().reset_index(name='Count')
        trends_df['Date'] = trends_df['Date'].dt.start_time
        fig_trends = px.line(trends_df, x='Date', y='Count', color='Category', markers=True)
        st.plotly_chart(fig_trends, use_container_width=True)

    # -----------------------------
    # EXECUTIVE RISK-INTEL FLOW (NEW)
    # -----------------------------
    st.subheader("Executive Risk Flow (Source → Theme → Impact → Urgency)")

    risk_df = filtered_df[filtered_df["Category"] == "Risk"].dropna(subset=["Source_Type","Theme / Topic","Potential impact","Urgency"])

    if not risk_df.empty:
        nodes = list(pd.concat([risk_df["Source_Type"], risk_df["Theme / Topic"],
                                risk_df["Potential impact"], risk_df["Urgency"]]).unique())
        idx = {n:i for i,n in enumerate(nodes)}

        source, target, value = [], [], []
        hover = []

        for c1,c2 in [("Source_Type","Theme / Topic"),
                      ("Theme / Topic","Potential impact"),
                      ("Potential impact","Urgency")]:
            grp = risk_df.groupby([c1,c2])["Weighted_Risk"].sum().reset_index()
            for _, r in grp.iterrows():
                source.append(idx[r[c1]])
                target.append(idx[r[c2]])
                value.append(r["Weighted_Risk"])
                hover.append(f"{r[c1]} → {r[c2]}<br>Weighted Risk: {round(r['Weighted_Risk'],2)}")

        fig_exec = go.Figure(go.Sankey(
            node=dict(label=nodes, pad=15, thickness=20),
            link=dict(source=source, target=target, value=value, hovertemplate=hover)
        ))
        st.plotly_chart(fig_exec, use_container_width=True)

    # -----------------------------
    # STRATEGIC HEATMAP (NEW)
    # -----------------------------
    st.subheader("Risk Intensity Over Time (Theme vs Week)")

    heat_df = risk_df.copy()
    if not heat_df.empty:
        heat_df["Week"] = heat_df["Date"].dt.to_period("W").astype(str)
        pivot = heat_df.pivot_table(index="Theme / Topic", columns="Week",
                                   values="Weighted_Risk", aggfunc="mean", fill_value=0)

        fig_heat = px.imshow(pivot, aspect="auto")
        st.plotly_chart(fig_heat, use_container_width=True)

    # -----------------------------
    # TOP ESCALATING RISKS (NEW)
    # -----------------------------
    st.subheader("Top Escalating Risks")

    if not risk_df.empty:
        top_risks = risk_df.sort_values("Weighted_Risk", ascending=False).head(10)
        st.dataframe(top_risks[["Theme / Topic","Source_Type","Potential impact","Urgency","IMS","Acceleration","Weighted_Risk"]])

    # -----------------------------
    # OLD SANKEY (UNCHANGED)
    # -----------------------------
    st.subheader("General Intelligence Flow")

    sankey_df = filtered_df.dropna(subset=["Category","Theme / Topic","Region impacted","Urgency"])
    if not sankey_df.empty:
        nodes = list(pd.concat([sankey_df["Category"], sankey_df["Theme / Topic"],
                                sankey_df["Region impacted"], sankey_df["Urgency"]]).unique())
        idx = {n:i for i,n in enumerate(nodes)}

        source, target, value, hover = [], [], [], []

        for c1,c2 in [("Category","Theme / Topic"),
                      ("Theme / Topic","Region impacted"),
                      ("Region impacted","Urgency")]:
            grp = sankey_df.groupby([c1,c2]).size().reset_index(name='Count')
            for _, r in grp.iterrows():
                source.append(idx[r[c1]])
                target.append(idx[r[c2]])
                value.append(r["Count"])
                hover.append(f"{r[c1]} → {r[c2]}: {r['Count']}")

        fig_old = go.Figure(go.Sankey(
            node=dict(label=nodes),
            link=dict(source=source, target=target, value=value, hovertemplate=hover)
        ))
        st.plotly_chart(fig_old, use_container_width=True)

    # -----------------------------
    # URGENCY BREAKDOWN
    # -----------------------------
    st.subheader("Urgency Breakdown")
    df_valid = filtered_df.dropna(subset=["Urgency","Category"])
    if not df_valid.empty:
        urgency_df = df_valid.groupby(["Urgency","Category"]).size().unstack(fill_value=0)
        fig_urgency = px.bar(urgency_df, barmode='stack')
        st.plotly_chart(fig_urgency, use_container_width=True)

    # -----------------------------
    # INTELLIGENCE LOG
    # -----------------------------
    st.subheader("Intelligence Log")
    log_cols = ["Date","Category","Theme / Topic","SDGs","Urgency","Potential impact"]
    st.dataframe(filtered_df[log_cols].sort_values("Date",ascending=False), use_container_width=True)

else:
    st.info("Upload your generated fact_table.csv to begin")
