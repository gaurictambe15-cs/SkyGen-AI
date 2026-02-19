# Fetch Live Flight Data
# Only Live data
import pandas as pd
import numpy as np
import streamlit as st
import requests
import datetime

@st.cache_data(ttl=60)
def fetch_live_flights_with_weather():
    """
    Fetch live flights from OpenSky and generate independent weather per flight
    Returns: DataFrame with flight + weather columns
    """
    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        states = data.get("states", [])
        flights = []

        for s in states:
            # Only airborne flights
            on_ground = s[8]  # boolean
            if on_ground is False:
                flights.append({
                    "flight_number": s[1].strip() if s[1] else s[0],  # ICAO callsign
                    "latitude": s[6],
                    "longitude": s[5],
                    "altitude": s[7],         # meters
                    "velocity": s[9],         # m/s
                    "heading": s[10],         # degrees
                    "vertical_rate": s[11],   # m/s climb/descent
                    "timestamp": pd.to_datetime(s[4],unit='s',utc=True)
                })

        # Create DataFrame
        df_flights = pd.DataFrame(flights)

        # Remove rows with missing critical data
        df_flight_data = df_flights.dropna(subset=["latitude", "longitude", "altitude", "velocity"]).reset_index(drop=True)

        # -----------------------------
        # Generate realistic weather per flight
        # -----------------------------
        n = len(df_flight_data)
        np.random.seed(None)

        # Wind speed (m/s)
        df_flight_data["wind_speed"] = np.random.normal(5, 3, n).clip(0, 30)

        # Visibility (km)
        df_flight_data["visibility"] = np.random.normal(12, 4, n).clip(0, 20)

        # Precipitation (mm/hr)
        df_flight_data["precip"] = np.random.normal(1, 2, n).clip(0, 15)

        return df_flight_data

    except Exception as e:
        print("Error fetching live flights from OpenSky:", e)
        return pd.DataFrame()  # empty DataFrame if error