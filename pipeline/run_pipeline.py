# run_pipeline.py

from .extract import extract_all
from .transform import transform_all
from .load import prepare_dashboard_data  # your load function

def run_pipeline(bi_file, risk_file=None):
    """
    Run full ETL pipeline.
    bi_file: path or uploaded file object for BI logging CSV
    risk_file: optional path or file object for internal risks
    """
    # 1️⃣ Extract
    raw_data = extract_all(bi_file, risk_file)  

    # 2️⃣ Transform
    fact, dims = transform_all(raw_data)

    # 3️⃣ Prepare dashboard summaries
    dashboard_data = prepare_dashboard_data(fact)

    return fact, dims, dashboard_data
