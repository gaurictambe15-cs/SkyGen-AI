# Analysis of historical dataset using preprocesses and models 

# Import libraries
import pandas as pd
from preprocess.preprocess_logic import basic_preprocess
from models.takeoff_risk import takeoff_weather_risk
from models.landing_risk import landing_weather_risk
from models.enroute_risk import enroute_weather_risk

# Load historical dataset
df=pd.read_csv("data/madrid_cleaned.csv")

# Preprocess
df=basic_preprocess(df)

# Apply models
df['takeoff_risk']=df.apply(takeoff_weather_risk,axis=1)
df['landing_risk']=df.apply(landing_weather_risk,axis=1)
df['enroute_risk']=df.apply(enroute_weather_risk,axis=1)

# Save output
df.to_csv("data/processed/madrid_risk_output.csv",index=False)

# Display
print("Risk analysis completed successfully!")