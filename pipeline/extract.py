import pandas as pd

def extract_all():

    bi = pd.read_csv("data/bi_logging.csv", 
                     parse_dates=["Date"],
                     dayfirst=True)
    bi["Horizon"] = bi["Horizon"].astype(str).str.strip().str.upper()
    
    risk = pd.read_csv("data/internal_risks.csv")
    sdg = pd.read_csv("data/SDGs.csv")
    wef_short = pd.read_csv("data/WEF Risks- short term.csv")
    wef_long = pd.read_csv("data/WEF Risks- long term.csv")

    return {
        "bi": bi,
        "risk": risk,
        "sdg": sdg,
        "wef_short": wef_short,
        "wef_long": wef_long
    }
