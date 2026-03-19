# run_pipeline.py
from extract import extract_all
from transform import transform_all
from load import export_all
from load import EXPORT_PATH  # import path for logging

def run():
    print("Starting ETL pipeline...")

    # 1. Extract
    raw_data = extract_all()
    print("Data extraction complete.")

    # 2. Transform
    fact, dims = transform_all(raw_data)
    print("Data transformation complete.")

    # 3. Load
    export_all(fact, dims)
    print(f"ETL complete. All files saved to: {EXPORT_PATH}")

if __name__ == "__main__":
    run()
