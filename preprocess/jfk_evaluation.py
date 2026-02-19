# Import Libraries
import pandas as pd

# import original csv
df=pd.read_csv("4. Hourly weather data.csv")
print(df.shape)
# selecting only JFK data 2013  
jfk=df[df['origin']=='JFK']
print(jfk.head())
print(jfk.shape)    # 8706 rows     columns before dropping =15
# Drop unwanted columns
jfk=jfk.drop(columns=['year','month','day','hour'])
print("Updated dataset:\n",jfk.head())
# Drop only nan column
jfk=jfk.drop(columns=['wind_gust'])
print(jfk.shape)

# Save only JFK data into new csv
jfk.to_csv("jfk_cleaned.csv",index=False)
print("Shape:",jfk.shape)
print("Last few data:",jfk.tail(5))
print(jfk.columns)
print(jfk.shape)

