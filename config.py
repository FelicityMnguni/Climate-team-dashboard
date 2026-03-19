# config.py - Streamlit prototype version
import os

ERROR_LOG_PATH = os.path.join(os.getcwd(), "error_logs") + os.sep

# -----------------------------
# IMS weights for scoring
# -----------------------------
IMS_WEIGHTS = {
    "urgency": 0.25,
    "horizon": 0.20,
    "internal_link": 0.15,
    "acceleration": 0.25,
    "region": 0.15
}

# -----------------------------
# Horizon & urgency mappings
# -----------------------------
HORIZON_MAP = {"H1": 1.0, "H2": 0.7, "H3": 0.4}
URGENCY_MAP = {"Very high": 1.0, "High": 0.75, "Medium": 0.5, "Low": 0.25}

# -----------------------------
# Escalation thresholds
# -----------------------------
ESCALATION_PERCENTILE = 0.85
ESCALATION_ACCEL_THRESHOLD = 0.2
