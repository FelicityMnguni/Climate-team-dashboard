import pandas as pd


def extract_all(bi_file, risk_file, sdg_file=None, wef_short_file=None, wef_long_file=None):
    bi = pd.read_csv(bi_file, parse_dates=["Date"], dayfirst=True)
    bi["Horizon"] = bi["Horizon"].astype(str).str.strip().str.upper()

    risk = pd.read_csv(risk_file)
    sdg = pd.read_csv(sdg_file) if sdg_file else pd.DataFrame()
    wef_short = pd.read_csv(wef_short_file) if wef_short_file else pd.DataFrame()
    wef_long = pd.read_csv(wef_long_file) if wef_long_file else pd.DataFrame()

    return {
        "bi": bi,
        "risk": risk,
        "sdg": sdg,
        "wef_short": wef_short,
        "wef_long": wef_long
    }
