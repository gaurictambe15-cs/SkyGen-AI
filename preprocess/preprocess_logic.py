# Preprocess Logic (Mapping + cleaning)
# Import Libraries
import pandas as pd

def basic_preprocess(df):
    # normalize column names
    df.columns=(df.columns.str.lower().str.replace(" ","").str.replace("/",""))
    # simple column mapping -> Standard names
    column_mapping={
        "wind_speed":["meanwindspeedkmh","meanwindspeed","windspeedkmh","windspeed","wind_speed"],
        "visibility":["meanvisibilitykm","meanvisibility","visibilitykm","visibility","visib"],
        "precip":["meanprecipationmm","precipitationmm","precipitation","precip"],
        "pressure":["meansealevelpressurehpa","meansealevelpressurepa","sealevelpressure","pressure"]
    }
    selected={}
    # choose best column for each feature
    for std_col,possible_cols in column_mapping.items():
        for col in possible_cols:
            if col in df.columns:
                selected[std_col]=col
                break

    # validation
    required=["wind_speed","visibility","precip","pressure"]

    for col in required:
        if col not in selected:
            raise ValueError(f"Missing required weather feature: {col}")

    # rename selected columns only
    df=df.rename(columns={v: k for k,v in selected.items()})
    # keep only needed columns
    df=df[required]
    # convert to numeric (force errors to NaN )
    df=df.apply(pd.to_numeric,errors="coerce")
    # drop NaN rows 
    df=df.dropna()
    print(df.head())
    print(df.tail())
    print(df.shape)
    return df

