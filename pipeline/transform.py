# pipeline/transform.py
import pandas as pd
import numpy as np
from config import *           # absolute import from root
from pipeline.validation import *   # absolute import from pipeline package

def clean_fields(bi):
    bi = bi.copy()
    # Strip column names
    bi.columns = [c.strip() for c in bi.columns]
    
    # Standardize fields
    bi["Horizon"] = bi["Horizon"].astype(str).str.strip().str.upper()
    bi["Urgency"] = bi["Urgency"].astype(str).str.strip().str.title()
    bi["Region impacted"] = bi["Region impacted"].astype(str).str.strip()
    
    # Validate using validation.py
    bi = validate_horizon(bi)
    bi = validate_urgency(bi)
    return bi

def compute_acceleration(bi):
    bi = bi.sort_values("Date")
    bi["Week"] = bi["Date"].dt.isocalendar().week
    bi["Year"] = bi["Date"].dt.year

    weekly = bi.groupby(["Year","Week","Topic"]).size().reset_index(name="Count")
    weekly["Rolling_4wk"] = weekly.groupby("Topic")["Count"].transform(
        lambda x: x.rolling(4, min_periods=1).sum()
    )
    weekly["Prior"] = weekly.groupby("Topic")["Rolling_4wk"].shift(1).fillna(0)
    weekly["Acceleration"] = (weekly["Rolling_4wk"] - weekly["Prior"]) / weekly["Prior"].replace(0,1)

    return bi.merge(
        weekly[["Year","Week","Topic","Acceleration"]],
        on=["Year","Week","Topic"], how="left"
    )

def compute_scores(bi, risk):
    bi["Horizon_W"] = bi["Horizon"].map(HORIZON_MAP)
    bi["Urgency_W"] = bi["Urgency"].map(URGENCY_MAP)
    bi["Internal_Link_Flag"] = bi["Item"].isin(risk["Risk Description"]).astype(int)
    
    region_counts = bi.groupby("Region impacted")["Item"].count()
    bi["Region_Index"] = bi["Region impacted"].map(region_counts) / region_counts.max()
    
    bi["Weighted_Acceleration"] = bi["Acceleration"] * bi["Horizon_W"]
    
    bi["IMS"] = (
        IMS_WEIGHTS["urgency"] * bi["Urgency_W"] +
        IMS_WEIGHTS["horizon"] * bi["Horizon_W"] +
        IMS_WEIGHTS["internal_link"] * bi["Internal_Link_Flag"] +
        IMS_WEIGHTS["acceleration"] * bi["Weighted_Acceleration"] +
        IMS_WEIGHTS["region"] * bi["Region_Index"]
    )
    return bi

def compute_escalation(bi):
    threshold = bi["IMS"].quantile(ESCALATION_PERCENTILE)
    bi["Escalation_Flag"] = (
        (bi["IMS"] >= threshold) &
        ((bi["Acceleration"] > ESCALATION_ACCEL_THRESHOLD) | (bi["Urgency_W"] >= 0.8))
    )
    return bi

def build_dimensions(bi, risk):
    # Theme
    dim_theme = bi[["Topic"]].drop_duplicates().reset_index(drop=True)
    dim_theme["ThemeKey"] = dim_theme.index + 1
    dim_theme["Theme"] = dim_theme["Topic"].str.strip()
    
    # Region
    dim_region = bi[["Region impacted"]].drop_duplicates().reset_index(drop=True)
    dim_region["RegionKey"] = dim_region.index + 1
    dim_region["Region"] = dim_region["Region impacted"].str.strip()
    
    # Horizon
    dim_horizon = pd.DataFrame({
        "HorizonKey": [1,2,3],
        "Horizon": ["H1","H2","H3"]
    })
    
    # Urgency
    dim_urgency = pd.DataFrame({
        "UrgencyKey": [1,2,3,4],
        "Urgency": ["Very high","High","Medium","Low"]
    })
    
    # Internal risk
    dim_risk = risk.reset_index(drop=True)
    dim_risk["InternalRiskKey"] = dim_risk.index + 1
    dim_risk["Risk Description"] = dim_risk["Risk Description"].str.strip()
    
    return dim_theme, dim_region, dim_horizon, dim_urgency, dim_risk

def build_fact(bi, dims):
    dim_theme, dim_region, dim_horizon, dim_urgency, dim_risk = dims
    
    fact = (
        bi
        .merge(dim_theme[["ThemeKey","Theme"]], left_on="Topic", right_on="Theme", how="left")
        .merge(dim_region[["RegionKey","Region"]], left_on="Region impacted", right_on="Region", how="left")
        .merge(dim_horizon, left_on="Horizon", right_on="Horizon", how="left")
        .merge(dim_urgency, left_on="Urgency", right_on="Urgency", how="left")
        .merge(dim_risk[["InternalRiskKey","Risk Description"]], left_on="Item", right_on="Risk Description", how="left")
    )
    
    # Drop raw text columns
    fact = fact.drop(columns=["Topic", "Region impacted", "Horizon", "Urgency"])
    return fact

def transform_all(data):
    bi = clean_fields(data["bi"])
    bi = compute_acceleration(bi)
    bi = compute_scores(bi, data["risk"])
    bi = compute_escalation(bi)
    dims = build_dimensions(bi, data["risk"])
    fact = build_fact(bi, dims)
    return fact, dims
