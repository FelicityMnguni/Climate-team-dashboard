def classify_risk(score):
    if score >= 80:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"
