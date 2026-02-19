# Landing Weather Risk Model

# Landing Weather Risk model logic rule based
def landing_weather_risk(row):
    wind=row['wind_speed']
    vis=row['visibility']
    precip=row['precip']
    pressure=row['pressure']
    # High Risk - landing unsafe
    if vis<2 or wind>25 or precip>0.4 or pressure<985:
        return "HIGH RISK"
    # Moderate landing - caution landing
    elif vis<4 or wind>18 or precip>0.15 or pressure<1000:
        return "MODERATE RISK"
    # LOW RISK - safe landing
    else:
        return "LOW RISK"