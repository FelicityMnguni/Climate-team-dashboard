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
    expected_cols = ["Date","Category","IMS","Theme / Topic","Region impacted",
                     "Urgency","Urgency_W","SDGs","Headline"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = np.nan

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Fill missing Urgency
    df["Urgency"] = df["Urgency"].fillna("Unknown")

    # Create Category column if missing
    if "Category" not in df.columns or df["Category"].isnull().all():
        def get_category(row):
            if str(row.get("Risk","No")) == "Yes":
                return "Risk"
            elif str(row.get("Opportunity","No")) == "Yes":
                return "Opportunity"
            elif str(row.get("Trend","No")) == "Yes":
                return "Trend"
            else:
                return "Other"
        df["Category"] = df.apply(get_category, axis=1)

    # -----------------------------
    # INTERACTIVE KPI CARDS
    # -----------------------------
    total_reports = len(df)
    high_urgency = df[df.get("Urgency_W",0) >= 0.8].shape[0]

    category_counts = df["Category"].value_counts()
    risks_count = category_counts.get("Risk",0)
    opp_count = category_counts.get("Opportunity",0)
    trend_count = category_counts.get("Trend",0)

    card_data = [
        {"label":"Reports Logged","value":total_reports,"color":"#457b9d","filter":df},
        {"label":"High Urgency Alerts","value":high_urgency,"color":"#e63946","filter":df[df["Urgency_W"]>=0.8]},
        {"label":"Risks","value":risks_count,"color":"#f94144","filter":df[df["Category"]=="Risk"]},
        {"label":"Opportunities","value":opp_count,"color":"#f3722c","filter":df[df["Category"]=="Opportunity"]},
        {"label":"Trends","value":trend_count,"color":"#90be6d","filter":df[df["Category"]=="Trend"]}
    ]

    kpi_cols = st.columns(len(card_data))
    for col, card in zip(kpi_cols, card_data):
        col.markdown(
            f"""
            <div style='background-color:{card['color']}; color:white; padding:20px; 
                        text-align:center; border-radius:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>
                <h3 style='margin:0'>{card['label']}</h3>
                <h2 style='margin:0'>{card['value']}</h2>
            </div>
            """, unsafe_allow_html=True
        )
        with col.expander(f"View {card['label']}"):
            display_cols = ["Date","Headline","Category","Theme / Topic","SDGs","Urgency"]
            existing_cols = [c for c in display_cols if c in card["filter"].columns]
            st.dataframe(card["filter"][existing_cols].sort_values("Date",ascending=False), use_container_width=True)

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
        st.markdown(sdg_html, unsafe_allow_html=True)
    else:
        st.markdown("<div style='padding:10px;'>No SDGs reported</div>", unsafe_allow_html=True)

    # -----------------------------
    # WEEKLY TRENDS
    # -----------------------------
    st.subheader("Weekly Trends")
    df_valid = df.dropna(subset=["Date","Category"])
    if not df_valid.empty:
        trends_df = df_valid.groupby([df_valid['Date'].dt.to_period('W'), 'Category']).size().reset_index(name='Count')
        trends_df['Date'] = trends_df['Date'].dt.start_time
        fig_trends = px.line(trends_df, x='Date', y='Count', color='Category', markers=True,
                             labels={"Count":"Number of Reports","Date":"Week"})
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.info("No valid data for trends over time.")

    # -----------------------------
    # GEOGRAPHIC IMPACT
    # -----------------------------
    st.subheader("Geographic Impact")
    if "Region impacted" in df.columns and "IMS" in df.columns and not df.empty:
        map_df = df.groupby("Region impacted")["IMS"].mean().reset_index()
        if not map_df.empty:
            fig_map = px.choropleth(map_df,
                                    locations="Region impacted",
                                    locationmode="country names",
                                    color="IMS",
                                    color_continuous_scale="Greens",
                                    title="Average Risk Materiality by Region")
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No data to display on map.")

    # -----------------------------
    # KEY THEMES
    # -----------------------------
    st.subheader("Key Themes")
    if "Theme / Topic" in df.columns and "IMS" in df.columns and not df.empty:
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
    df_valid = df.dropna(subset=["Urgency","Category"])
    if not df_valid.empty:
        urgency_df = df_valid.groupby(["Urgency","Category"]).size().unstack(fill_value=0)
        if not urgency_df.empty:
            fig_urgency = px.bar(urgency_df, barmode='stack', title="Urgency by Category",
                                 labels={"value":"Number of Reports","Urgency":"Urgency Level"})
            st.plotly_chart(fig_urgency, use_container_width=True)
        else:
            st.info("No data for urgency breakdown.")
    else:
        st.info("No valid data for urgency breakdown.")

    # -----------------------------
    # INTELLIGENCE LOG
    # -----------------------------
    st.subheader("Intelligence Log")
    log_cols = ["Date","Headline","Category","Theme / Topic","SDGs","Urgency"]
    existing_cols = [c for c in log_cols if c in df.columns]
    st.dataframe(df[existing_cols].sort_values("Date",ascending=False), use_container_width=True)

else:
    st.info("Upload your generated fact_table.csv to begin")
