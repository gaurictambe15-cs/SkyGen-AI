# Risk Visualizations For Charts

# Plot Risk Distribution Logic
# Takeoff risk logic
def takeoff_risk_distribution(df):
    return df["takeoff_risk"].value_counts()
# Landing risk logic
def landing_risk_distribution(df):
    return df["landing_risk"].value_counts()
# Enroute risk logic
def enroute_risk_distribution(df):
    return df["enroute_risk"].value_counts()
