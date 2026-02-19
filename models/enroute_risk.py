# Enroute Weather Risk Model

# Enroute Weather Risk Model logic rule based
def enroute_weather_risk(row):
    wind=row['wind_speed']
    vis=row['visibility']
    precip=row['precip']
    pressure=row['pressure']
    # High Risk - Unsafe Airspace
    if wind > 35 or precip > 0.5 or vis < 3 or pressure < 980:
        return "ENROUTE CRITICAL"  #Avoid airspace due to severe weather
    # Moderate Risk - turbulence/weather cells
    elif wind > 25 or precip > 0.2 or vis < 6 or pressure < 1000:
        return "ENROUTE CAUTION" #Turbulence or weather cells present
    # Low Risk - smooth enroute conditions
    else:
        return "ENROUTE SAFE" #Enroute conditions stable
