# TakeOff Weather Risk Model

# Takeoff weather risk model logic rule based
def takeoff_weather_risk(row):
    wind=row['wind_speed']
    vis=row['visibility']
    precip=row['precip']
    pressure=row['pressure']
    # High Risk
    if wind>30 or vis<3 or precip>0.3 or pressure<990:
        return "HIGH RISK"
    # Moderate Risk
    elif wind>20 or vis<5 or precip>0.1 or pressure<1000:
        return "MODERATE RISK"
    # Low Risk
    else:
        return "LOW RISK"
