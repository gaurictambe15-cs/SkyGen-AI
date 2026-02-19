# Import libraries
import pandas as pd
import numpy as np
# Load dataset
df=pd.read_csv("madrid_weather_selected.csv")
df.to_csv("madrid_weather_selected.csv",index=False)
#Fix minor for WindDirDegrees coln
df['WindDirDegrees'].replace(-1,np.nan,inplace=True)
df.dropna(inplace=True)
print("Mode:",df['WindDirDegrees'].mode().tolist())
print("val_count:",df['WindDirDegrees'].value_counts().head())
#Fix minor for Precipitationmm coln
print("Precipitation:",df['Precipitationmm'].value_counts().head())
# Display dataset
print(df.head())
print(df.columns)
print(df.shape)
# Overall description
#print(df.describe())
# Statistics
print(df.head())
print("Column wise Stats:")
df.select_dtypes(include='number').columns
for col in df.columns:
    print(f"Columns:{col}")
    print(f"Min={df[col].min()}")
    print(f"Max={df[col].median()}")
    print(f"Median:{df[col].median()}")
    print(f"Standard Deviation:{df[col].std()}")
    print(f"Variance:{df[col].var()}")
# Outliers
print("Column wise Stats:")
num_cols=df.select_dtypes(include='number').columns
for col in num_cols:
    Q1=df[col].quantile(0.25)
    Q3=df[col].quantile(0.75)
    IQR=Q3-Q1
    lower=Q1-1.5*IQR
    upper=Q3+1.5*IQR
    outliers=df[(df[col]<lower)|(df[col]>upper)]
    print(f"{col}:{outliers.shape[0]} outliers")
    
