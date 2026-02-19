# AI Risk Prediction
# Only Live data
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.tree import DecisionTreeClassifier

# -----------------------------
# Realistic thresholds (aviation approximate)
# -----------------------------
STANDARD_THRESHOLDS = {
    "wind_speed": {"caution": 10, "critical": 15},   # m/s 
    "visibility": {"caution": 5, "critical": 2},    # km
    "precip": {"caution": 2, "critical": 5}         # mm/hr
}

# -----------------------------
# Merge flight + weather (live)
# -----------------------------
def merge_flight_weather_live(df_flight):
    """
    df_flight: live flight df with weather columns added during fetch
    Returns df with realistic variations for each flight
    """
    df_merged = df_flight.copy()

    # Add small random noise for realism
    np.random.seed(None)
    for col, sigma in [("wind_speed", 0.5), ("visibility", 0.5), ("precip", 0.1)]:
        if col in df_merged.columns:
            df_merged[col] = df_merged[col] + np.random.normal(0, sigma, size=len(df_merged))
            df_merged[col] = df_merged[col].clip(lower=0)

    return df_merged

# -----------------------------
# Train threshold-based Decision Tree
# -----------------------------
@st.cache_resource
def train_threshold_model(thresholds=STANDARD_THRESHOLDS):
    """
    Generates training data based on standard aviation thresholds
    """
    rows = []
    for param, vals in thresholds.items():
        c, cr = vals["caution"], vals["critical"]
        for v in range(0, int(cr) + 5):
            if v < c:
                risk = 0  # Normal
            elif c <= v < cr:
                risk = 1  # Caution
            else:
                risk = 2  # Critical
            row = {
                "wind_speed": v if param == "wind_speed" else 0,
                "visibility": v if param == "visibility" else 10,
                "precip": v if param == "precip" else 0,
                "risk": risk
            }
            rows.append(row)

    df_train = pd.DataFrame(rows)
    X = df_train[["wind_speed", "visibility", "precip"]]
    y = df_train["risk"]

    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X, y)
    return model

# -----------------------------
# Predict Risk
# -----------------------------
def predict_risk_live(df_flights_weather, model):
    """
    Predict risk (Normal / Caution / Critical) for live flights
    """
    if df_flights_weather.empty:
        df_flights_weather["predicted_risk"] = None
        return df_flights_weather

    X = df_flights_weather[["wind_speed", "visibility", "precip"]]
    y_pred = model.predict(X)
    risk_map = {0: "Normal", 1: "Caution", 2: "Critical"}
    df_flights_weather["predicted_risk"] = [risk_map[r] for r in y_pred]
    return df_flights_weather

# -----------------------------
# Combined utility (Module 3)
# -----------------------------
def get_live_flight_risk(df_flight_live, num_display=None):
    """
    df_flight_live: live flight df fetched with weather columns included
    num_display: number of top flights to consider for all outputs
    Returns: df with predicted risk column (sliced if num_display set)
    """
    df_merged = merge_flight_weather_live(df_flight_live)
    model = train_threshold_model()
    df_risk = predict_risk_live(df_merged, model)

    # Slice only top flights selected by user
    if num_display is not None:
        df_risk = df_risk.head(num_display)

    return df_risk