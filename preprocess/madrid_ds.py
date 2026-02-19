# Cleaning Original dataset
# import libraries
import pandas as pd
df=pd.read_csv("weather_madrid_LEMD_1997_2015.csv")
print(df.head())

# data cleaning
core_features = [
    'Mean TemperatureC', 'MeanDew PointC', ' Mean Humidity', ' Mean Sea Level PressurehPa',
    ' Mean VisibilityKm', ' Mean Wind SpeedKm/h', ' Max Gust SpeedKm/h', 'WindDirDegrees',
    'Precipitationmm', ' CloudCover'
]
cols_to_keep=[c for c in core_features if c in df.columns]
df = df[cols_to_keep]
# Printing selected columns
print("✅ Columns cleaned successfully")
print(df.columns.tolist())
# Cleaning duplicates and null values
df=df.drop_duplicates()
df=df.dropna()
# Reset index after dropping unwanted data
df=df.reset_index(drop=True)
# Convert all values into numerical format (decimal) and display correct format
df=df.apply(pd.to_numeric,errors='coerce')
df=df.dropna()
print("data type of col:",df.dtypes)
# Display overall dataset after cleaned
print(df.head(5))
print(df.tail(5))
print("null values:",df.isnull().sum())
print("duplicate values:",df.duplicated().sum())
print(df.info())

