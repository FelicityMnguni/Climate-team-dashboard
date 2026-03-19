# run_pipeline.py
from pipeline.extract import extract_all
from pipeline.transform import transform_all
from pipeline.load import prepare_dashboard_data  # your load function

def run_pipeline(bi_file, risk_file):
    raw_data = extract_all(bi_file, risk_file)
    fact, dims = transform_all(raw_data)
    dashboard_data = prepare_dashboard_data(fact)  # aggregated summaries for dashboard
    return fact, dims, dashboard_data
