# Logic for Live Data For Module 2

import pandas as pd
from datetime import timedelta

# -----------------------------
# Threshold Definitions
# -----------------------------
THRESHOLDS = {
    "wind_speed": {"caution": 10, "critical": 15},
    "visibility": {"caution": 5, "critical": 2},
    "precip": {"caution": 2, "critical": 5}
}


# -----------------------------
# Filter Live Window
# -----------------------------
def filter_live(df, minutes):
    """
    Filters dataframe to last X minutes
    """
    latest_time = df["timestamp"].max()
    return df[df["timestamp"] >= latest_time - timedelta(minutes=minutes)]


# -----------------------------
# Add Weather Status Column
# -----------------------------
def add_status_column(df, parameter):
    """
    Adds 'status' column based on threshold comparison
    """
    caution = THRESHOLDS[parameter]["caution"]
    critical = THRESHOLDS[parameter]["critical"]

    def classify(value):
        if value > critical:
            return "Critical"
        elif value > caution:
            return "Caution"
        else:
            return "Normal"

    df = df.copy()
    df["status"] = df[parameter].apply(classify)
    return df


# -----------------------------
# Generate Live Insight Text
# -----------------------------
def generate_live_insight(df):
    """
    Generates simple human-readable insight
    """
    crossings = df[df["status"] != "Normal"].shape[0]

    if crossings > 10:
        return "Frequent threshold crossings observed in recent live window."
    elif crossings > 0:
        return "Occasional threshold spikes detected in live conditions."
    else:
        return "Weather conditions remained mostly stable in recent minutes."