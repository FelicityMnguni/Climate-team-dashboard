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
                     "Urgency","Urgency_W","SDGs","Headline","Potential impact","Internal_Link"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = np.nan

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Urgency"] = df["Urgency"].fillna("Unknown")
    df["Category"] = df["Category"].fillna("Other")

    # -----------------------------
    # FILTERS
    # -----------------------------
    st.sidebar.subheader("Filters")
    selected_category = st.sidebar.multiselect("Category", df["Category"].dropna().unique(), default=df["Category"].dropna().unique())
    selected_urgency = st.sidebar.multiselect("Urgency", df["Urgency"].dropna().unique(), default=df["Urgency"].dropna().unique())
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
        {"label":"Reports Logged","value":total_reports,"color":"#457b9d","filter":filtered_df},
        {"label":"High Urgency Alerts","value":high_urgency,"color":"#e63946","filter":filtered_df[filtered_df["Urgency_W"]>=0.8]},
        {"label":"Risks","value":risks_count,"color":"#f94144","filter":filtered_df[filtered_df["Category"]=="Risk"]},
        {"label":"Opportunities","value":opp_count,"color":"#f3722c","filter":filtered_df[filtered_df["Category"]=="Opportunity"]},
        {"label":"Trends","value":trend_count,"color":"#90be6d","filter":filtered_df[filtered_df["Category"]=="Trend"]}
    ]

    # First row: Reports Logged & High Urgency
    row1_cols = st.columns([2,2])
    for col, card in zip(row1_cols, card_data[:2]):
        col.markdown(
            f"""
            <div style='background-color:{card['color']}; color:white; padding:30px; 
                        text-align:center; border-radius:12px; box-shadow: 3px 3px 8px rgba(0,0,0,0.2);'>
                <h3 style='margin:0; font-size:22px'>{card['label']}</h3>
                <h1 style='margin:0; font-size:36px'>{card['value']}</h1>
            </div>
            """, unsafe_allow_html=True
        )
        with col.expander(f"View {card['label']}"):
            display_cols = ["Date","Headline","Category","Theme / Topic","SDGs","Urgency","Potential impact","Internal_Link"]
            existing_cols = [c for c in display_cols if c in card["filter"].columns]
            st.dataframe(card["filter"][existing_cols].sort_values("Date",ascending=False), use_container_width=True)

    # Second row: Risks, Opportunities, Trends
    row2_cols = st.columns([1,1,1])
    for col, card in zip(row2_cols, card_data[2:]):
        col.markdown(
            f"""
            <div style='background-color:{card['color']}; color:white; padding:25px; 
                        text-align:center; border-radius:12px; box-shadow: 3px 3px 8px rgba(0,0,0,0.2);'>
                <h3 style='margin:0; font-size:20px'>{card['label']}</h3>
                <h2 style='margin:0; font-size:28px'>{card['value']}</h2>
            </div>
            """, unsafe_allow_html=True
        )
        with col.expander(f"View {card['label']}"):
            display_cols = ["Date","Headline","Category","Theme / Topic","SDGs","Urgency","Potential impact","Internal_Link"]
            existing_cols = [c for c in display_cols if c in card["filter"].columns]
            st.dataframe(card["filter"][existing_cols].sort_values("Date",ascending=False), use_container_width=True)

    # -----------------------------
    # DYNAMIC SDG TILES
    # -----------------------------
    st.subheader("SDGs")
    if "SDGs" in filtered_df.columns and filtered_df["SDGs"].notna().any():
        unique_sdgs = pd.Series(filtered_df["SDGs"].dropna().astype(str).str.split(",").sum()).unique()
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
    df_valid = filtered_df.dropna(subset=["Date","Category"])
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
    def to_iso3(name):
        try:
            return pycountry.countries.lookup(name).alpha_3
        except:
            return None
    filtered_df['Region_ISO'] = filtered_df['Region impacted'].apply(to_iso3)
    map_df = filtered_df.dropna(subset=['Region_ISO']).groupby('Region_ISO')['IMS'].mean().reset_index()
    if not map_df.empty:
        fig_map = px.choropleth(map_df,
                                locations="Region_ISO",
                                locationmode="ISO-3",
                                color="IMS",
                                color_continuous_scale="Greens",
                                title="Average Risk Materiality by Region")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No valid data for geographic impact.")

    # -----------------------------
    # KEY THEMES
    # -----------------------------
    st.subheader("Key Themes")
    if "Theme / Topic" in filtered_df.columns and "IMS" in filtered_df.columns and not filtered_df.empty:
        top_themes = filtered_df.groupby("Theme / Topic")["IMS"].mean().sort_values(ascending=False).head(6)
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
    df_valid = filtered_df.dropna(subset=["Urgency","Category"])
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
    # SANKY DIAGRAM: Category → Theme → Region → Urgency
    # -----------------------------
    st.subheader("Risk Links Flow (Sankey)")
    sankey_df = filtered_df.dropna(subset=["Category","Theme / Topic","Region impacted","Urgency"])
    if not sankey_df.empty:
        all_nodes = list(pd.concat([sankey_df["Category"], sankey_df["Theme / Topic"],
                                    sankey_df["Region impacted"], sankey_df["Urgency"]]).unique())
        node_indices = {name:i for i,name in enumerate(all_nodes)}

        source = []
        target = []
        value = []

        for col1,col2 in [("Category","Theme / Topic"),("Theme / Topic","Region impacted"),("Region impacted","Urgency")]:
            grp = sankey_df.groupby([col1,col2]).size().reset_index(name='Count')
            for _, row in grp.iterrows():
                source.append(node_indices[row[col1]])
                target.append(node_indices[row[col2]])
                value.append(row['Count'])

        fig_sankey = go.Figure(go.Sankey(
            node=dict(label=all_nodes, pad=15, thickness=20, color="lightblue"),
            link=dict(source=source, target=target, value=value)
        ))
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.info("No valid data for Sankey diagram.")

    # -----------------------------
    # INTELLIGENCE LOG with clickable links
    # -----------------------------
    st.subheader("Intelligence Log")
    log_cols = ["Date","Headline","Category","Theme / Topic","SDGs","Urgency","Potential impact","Internal_Link"]
    existing_cols = [c for c in log_cols if c in filtered_df.columns]

    # Make clickable links
    if "Internal_Link" in existing_cols:
        filtered_df['Internal_Link_Display'] = filtered_df['Internal_Link'].apply(
            lambda x: f"[View Link]({x})" if pd.notna(x) else ""
        )
        display_cols = [c if c!="Internal_Link" else "Internal_Link_Display" for c in existing_cols]
        st.markdown(filtered_df[display_cols].to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.dataframe(filtered_df[existing_cols].sort_values("Date",ascending=False), use_container_width=True)

else:
    st.info("Upload your generated fact_table.csv to begin")
