# run_pipeline.py

from pipeline.extract import extract_all
from pipeline.transform import transform_all
from pipeline.load import prepare_dashboard_data  # your load function

def run_pipeline(bi_file, risk_file=None):
    """
    Runs the full ETL pipeline.
    
    Args:
        bi_file: uploaded BI logging CSV
        risk_file: optional uploaded risk CSV
    
    Returns:
        fact: the transformed fact table
        dims: dictionary of dimensions
        dashboard_data: aggregated datasets for the dashboard (summary, trend, heatmap)
    """
    # 1️⃣ Extract
    raw_data = extract_all(bi_file, risk_file)
    
    # 2️⃣ Transform
    fact, dims = transform_all(raw_data)
    
    # 3️⃣ Load / prepare aggregated dashboard data
    dashboard_data = prepare_dashboard_data(fact)
    
    return fact, dims, dashboard_data
