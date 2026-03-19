from pipeline.extract import extract_data
from pipeline.transform import transform_data
from pipeline.validation import validate_data
from pipeline.load import prepare_dashboard_data

def run_pipeline(file):
    df = extract_data(file)
    df = transform_data(df)
    df = validate_data(df)
    dashboard_data = prepare_dashboard_data(df)

    return df, dashboard_data
