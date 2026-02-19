# Risk Visualizations For MADRID Dataset

# Import libraries
import pandas as pd

# Load both processed datasets
madrid=pd.read_csv("data/processed/madrid_risk_output.csv")

# Plot Risk Distribution Logic
# Takeoff risk logic
def takeoff_risk_distribution(df=madrid):
    return df["takeoff_risk"].value_counts()
# Landing risk logic
def landing_risk_distribution(df=madrid):
    return df["landing_risk"].value_counts()
# Enroute risk logic
def enroute_risk_distribution(df=madrid):
    return df["enroute_risk"].value_counts()