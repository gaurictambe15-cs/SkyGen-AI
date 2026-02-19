# ATC Decision Support

# Reuse data from previous modules
import pandas as pd
from live.live_data_analysis import build_live_processed_df
from live.live_flight_data import fetch_live_flights_with_weather
from live.live_weather_logic import add_status_column,THRESHOLDS

# Columns we need for Module 4
COLUMNS_NEEDED = [
    "flight_id",
    "wind_speed",
    "visibility",
    "precip",
    "status",
    "timestamp",
    "takeoff_risk",
    "landing_risk",
    "enroute_risk",
]

def fetch_recent_data(selected_airport):
    """
    Fetch only already created columns from previous modules
    """
    
    icao="KJFK"
    airport_name="JFK"

    
    # 1️⃣ Get processed live weather + risk
    df_weather = build_live_processed_df(icao=icao, airport_name=selected_airport, minutes=60)

    # 2️⃣ Ensure status column exists for all 3 parameters
    df_weather = add_status_column(df_weather, parameter="wind_speed")
    df_weather = add_status_column(df_weather, parameter="visibility")
    df_weather = add_status_column(df_weather, parameter="precip")
    
    
    # 3️⃣ Filter last N minutes (weather timestamp)
    # Ensure datetime type
    df_weather["timestamp"] = pd.to_datetime(
    df_weather.get("timestamp") or df_weather.get("timestamp") or df_weather.get("time") or df_weather.get("obs_time", pd.NaT),
    errors="coerce"
    )
   
    # Ensure timestamp exists
    if "timestamp" not in df_weather.columns:
        df_weather["timestamp"] = pd.Timestamp.now()
    print("weather:",df_weather["timestamp"].head())

    # Ensure correct type
    df_weather["timestamp"] = pd.to_datetime(df_weather["timestamp"], errors="coerce")
    

    # 4️⃣ Get live flights (flight number + flight timestamp)
    df_flights = fetch_live_flights_with_weather()
    
    
    if not df_flights.empty:
        df_flights.rename(columns={"timestamp": "flight_timestamp"}, inplace=True)

    
    #Merge weather data into flights (Using flight_timestamp as the only time)
    if not df_weather.empty:
        latest_weather = df_weather.iloc[-1]
        n = len(df_flights)
        
        # Fill data columns
        for col in ["wind_speed", "status", "takeoff_risk", "landing_risk", "enroute_risk"]:
            if col in latest_weather:
                df_flights[col] = [latest_weather[col]] * n

        df_flights["visibility"] = [abs(float(latest_weather.get("visibility", 0)))] * n
        df_flights["precip"] = [abs(float(latest_weather.get("precip", 0)))] * n

    # 4. Final Columns (Notice: 'timestamp' is GONE)
    df_combined = df_flights[[
        "flight_number",
        "flight_timestamp",
        "wind_speed",
        "visibility",
        "precip",
        "status",
        "takeoff_risk",
        "landing_risk",
        "enroute_risk"
    ]].copy()
    

    print("columns:",df_combined.head())
    
    return df_combined

def get_top_critical_flights(df, phase="Takeoff", top_n=5):
    risk_col = {
        "Takeoff": "takeoff_risk",
        "Landing": "landing_risk",
        "Enroute": "enroute_risk"
    }[phase]

    critical_flights = df[df[risk_col] == "HIGH RISK"] \
        .sort_values(by="flight_timestamp", ascending=False) \
            .head(top_n)

    
    return critical_flights

def generate_suggested_actions(df, phase="Takeoff"):
    """
    Create ATC actionable guidance based on thresholds.
    Simplified and easy to read.
    """
    actions = []

    for idx, row in df.iterrows():
        msg = None
        param = None
        value = None

         # ---------------- Takeoff ----------------
        if phase == "Takeoff":
            if row["wind_speed"] > THRESHOLDS["wind_speed"]["critical"]:
                msg, param, value = f"Flight {row['flight_number']} → High wind! Delay Takeoff 5 min", "Wind", row["wind_speed"]
            elif row["wind_speed"] > THRESHOLDS["wind_speed"]["caution"]:
                msg, param, value = f"Flight {row['flight_number']} → Wind caution. Monitor closely", "Wind", row["wind_speed"]

            if row["visibility"] < THRESHOLDS["visibility"]["critical"]:
                msg, param, value = f"Flight {row['flight_number']} → Very low visibility! Go-around recommended!", "Visibility", row["visibility"]
            elif row["visibility"] < THRESHOLDS["visibility"]["caution"]:
                msg, param, value = f"Flight {row['flight_number']} → Visibility caution. Reduce speed", "Visibility", row["visibility"]

            if row["precip"] > THRESHOLDS["precip"]["critical"]:
                msg, param, value = f"Flight {row['flight_number']} → Heavy precipitation! Delay Takeoff", "Precipitation", row["precip"]
            elif row["precip"] > THRESHOLDS["precip"]["caution"]:
                msg, param, value = f"Flight {row['flight_number']} → Precipitation caution. Monitor closely", "Precipitation", row["precip"]

        # ---------------- Landing ----------------
        elif phase == "Landing":
            if row["wind_speed"] > THRESHOLDS["wind_speed"]["critical"]:
                msg, param, value = f"Flight {row['flight_number']} → High wind. Use alternate runway", "Wind", row["wind_speed"]
            elif row["wind_speed"] > THRESHOLDS["wind_speed"]["caution"]:
                msg, param, value = f"Flight {row['flight_number']} → Wind caution. Approach carefully", "Wind", row["wind_speed"]

            if row["visibility"] < THRESHOLDS["visibility"]["critical"]:
                msg, param, value = f"Flight {row['flight_number']} → Very low visibility. Go-around recommended!", "Visibility", row["visibility"]
            elif row["visibility"] < THRESHOLDS["visibility"]["caution"]:
                msg, param, value = f"Flight {row['flight_number']} → Visibility caution. Reduce speed", "Visibility", row["visibility"]

            if row["precip"] > THRESHOLDS["precip"]["critical"]:
                msg, param, value = f"Flight {row['flight_number']} → Heavy precipitation. Landing advisory", "Precipitation", row["precip"]
            elif row["precip"] > THRESHOLDS["precip"]["caution"]:
                msg, param, value = f"Flight {row['flight_number']} → Precipitation caution. Approach carefully", "Precipitation", row["precip"]

        # Add to list if any action is triggered
        if msg:
            actions.append({
                "Time": row["flight_timestamp"].strftime("%H:%M")
                if pd.notna(row["flight_timestamp"]) else "N/A",
                "Flight": row["flight_number"],
                "Parameter": param,
                "Value": value,
                "Action": msg
            })

    return pd.DataFrame(actions)

def operational_trend_strip(df, minutes=60):
    """
    Backend logic for Operational Trend Strip.
    Returns recent data with thresholds for Wind, Visibility, Precipitation.
    """

    # 1️⃣ Filter last N minutes
    df_recent = df.copy()
    df_recent=df.sort_values("flight_timestamp")
    # 2️⃣ Define parameters to track
    parameters = ["wind_speed", "visibility", "precip"]

    # 3️⃣ Prepare trend data dictionary
    trends = {}
    for param in parameters:
        trends[param] = {
            "timestamps": df_recent["flight_timestamp"].tolist(),
            "values": df_recent[param].tolist(),
            "caution": THRESHOLDS[param]["caution"],
            "critical": THRESHOLDS[param]["critical"]
        }

    return trends

def prepare_heatmap_data(df, minutes=60):
    """
    Prepare flight vs parameter data for heatmap.
    Rows = parameters, Columns = flights, Values = parameter readings
    """
    # Filter last N minutes
    
    df_recent = df.copy()
    
    if df_recent.empty:
        return None

    parameters = ["wind_speed", "visibility", "precip"]
    
    # Pivot so rows = parameters, columns = flight_id, values = last reading
    heatmap_df = df_recent.groupby("flight_number")[parameters].last().T
    return heatmap_df
