# pipeline/extract.py
import pandas as pd

def extract_all(bi_file, risk_file=None):
    """
    Extract BI logging data and optionally internal risks.
    Accepts:
        bi_file: file-like object or path (uploaded CSV from Streamlit)
        risk_file: file-like object or path (optional)
    Returns:
        dict with keys: 'bi', 'risk'
    """
    # --- BI logging data ---
    bi = pd.read_csv(
        bi_file,
        parse_dates=["Date"],
        dayfirst=True
    )
    
    # Standardize Horizon column
    if "Horizon" in bi.columns:
        bi["Horizon"] = bi["Horizon"].astype(str).str.strip().str.upper()
    
    # --- Internal Risks ---
    if risk_file is not None:
        risk = pd.read_csv(risk_file)
    else:
        # If not provided, create empty DataFrame
        risk = pd.DataFrame(columns=["Risk Description"])
    
    return {
        "bi": bi,
        "risk": risk
    }
