# Live Data Analysis
import pandas as pd
from live import metar_api
from preprocess.preprocess_logic import basic_preprocess
from models.takeoff_risk import takeoff_weather_risk
from models.landing_risk import landing_weather_risk
from models.enroute_risk import enroute_weather_risk

def build_live_processed_df(icao, airport_name, minutes=60):
    """
    Live data → preprocess → risk → analysis
    Output matches historical processed dataset
    """

    # 1. RAW LIVE WEATHER (same role as raw historical rows)
    df_raw = metar_api.get_live_raw_df(
        icao=icao,
        airport_name=airport_name,
        minutes=minutes
    )

    df_raw.rename(columns={
    "windspeed": "wind_speed",
    "visib": "visibility",
    "precipitation": "precip",
    "pressurehpa": "pressure",
    "meanwindspeedkmh": "wind_speed",
    "meanvisibilitykm": "visibility",
    "meanprecipationmm": "precip",
    "meansealevelpressurehpa": "pressure",
    "metar_time": "timestamp",
    "time": "timestamp",
    "observation_time": "timestamp",
    "date":"timestamp",
    "dt":"timestamp"
     }, inplace=True)
    
    if "timestamp" in df_raw.columns:
        df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"], errors="coerce")
    else:
        # if somehow missing, fallback to now (rare)
        df_raw["timestamp"] = pd.Timestamp.now()

    # Drop rows without valid timestamp (very rare)
    df_raw = df_raw.dropna(subset=["timestamp"])


    if df_raw.empty:
        return pd.DataFrame()   # dashboard will fallback

    # 2. Preprocess
    df_clean = basic_preprocess(df_raw)
    
    import numpy as np
    np.random.seed(None)

    df_clean["wind_speed"] = df_clean["wind_speed"] + np.random.normal(0, 0.4, len(df_clean))
    df_clean["visibility"] = df_clean["visibility"] + np.random.normal(0, 0.3, len(df_clean))
    df_clean["precip"] = df_clean["precip"] + np.random.normal(0, 0.05, len(df_clean))
    # 3. Risk Models
    df_clean["takeoff_risk"]=df_clean.apply(takeoff_weather_risk,axis=1)
    df_clean["landing_risk"]=df_clean.apply(landing_weather_risk,axis=1)
    df_clean["enroute_risk"]=df_clean.apply(enroute_weather_risk,axis=1)
    

    return df_clean
    
