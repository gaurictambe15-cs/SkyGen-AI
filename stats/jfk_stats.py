# Import Libraries
import pandas as pd

# import original csv
df=pd.read_csv("jfk_cleaned.csv")
print(df.head())
print(df.shape)

# Statistics
# Description
print(df.describe())

# Convert to numeric values
num_val=df.select_dtypes(include=['number']).columns
df[num_val]=df[num_val].apply(pd.to_numeric,errors='coerce')
print(df.dtypes)

# Cloumn wise description
for col in df.select_dtypes(include='number').columns:
    print(f"\nColumns:{col}")
    print("Min:",df[col].min())
    print("Max:",df[col].max())
    print("Mean:",df[col].mean())
    print("Median:",df[col].median())
    print("Var:",df[col].var())
    print("Std Deviation:",df[col].std())
    print(df['origin'].value_counts())

# Mode for wind_dir
print("Mode:",df['wind_dir'].mode())
print(df['wind_dir'].value_counts().head())
print(df.shape)

# Outliers
num_cols=['temp','dewp','humid','wind_speed','precip','pressure','visib']
for col in num_cols:
    Q1=df[col].quantile(0.25)
    Q3=df[col].quantile(0.75)
    IQR=Q3-Q1
    lower=Q1-1.5*IQR
    upper=Q3+1.5*IQR
    outliers=df[(df[col]<lower)|(df[col]>upper)]
    print(f"{col}:{outliers.shape[0]} outliers")
print(df.shape)