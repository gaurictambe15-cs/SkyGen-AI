# LIVE DATA
# METAR api

import pandas as pd
import requests
from datetime import datetime,timedelta,timezone
from metar.Metar import Metar
# ---------------- METAR RAW ----------------
def fetch_raw_metar(icao):
    url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT"
    r = requests.get(url, timeout=15)
    lines = r.text.splitlines()

    obs_time = lines[0].strip()
    metar_raw = lines[-1].strip()
    
    try:
        m = Metar(metar_raw)
        windspeed = m.wind_speed.value("KT")  # knots
        visibility = m.vis.value("KM")        # km
        pressure = m.press.value("HPA")       # hPa
        temp = m.temp.value("C")
        precip = 0                            # optional, METAR often has no direct precip info
    except:
        windspeed = visibility = pressure = temp = precip = None
    return {
        "icao": icao,
        "raw_metar": metar_raw,
        "obs_time": obs_time,
        "windspeed": windspeed,
        "visib": visibility,
        "precipitation": precip,
        "pressurehpa": pressure
    }


# ---------------- OPENSKY RAW ----------------
def fetch_raw_flights(icao, minutes):
    end = int(datetime.now().timestamp())
    start = int((datetime.now() - timedelta(minutes=minutes)).timestamp())

    url = (
        f"https://opensky-network.org/api/flights/departure"
        f"?airport={icao}&begin={start}&end={end}"
    )
    r = requests.get(url, timeout=5)
    data = r.json() if r.status_code == 200 else []
    return data
    

# ---------------- RAW LIVE DF ----------------
def get_live_raw_df(icao, airport_name, minutes=60):

    metar = fetch_raw_metar(icao)
    flights = fetch_raw_flights(icao, minutes)

    flight_count = len(flights)

    # fallback if API quiet
    if flight_count < 5:
        flight_count = 10
 
    df = pd.DataFrame({
        "airport": [airport_name] * flight_count,
        "icao": [icao] * flight_count,
        "raw_metar": [metar["raw_metar"]] * flight_count,
        "obs_time": [metar["obs_time"]] * flight_count,
        "windspeed":[metar["windspeed"]]*flight_count,
        "visib": [metar["visib"]]*flight_count,
        "precipitation": [metar["precipitation"]]*flight_count,
        "pressurehpa": [metar["pressurehpa"]]*flight_count
    })

    return df