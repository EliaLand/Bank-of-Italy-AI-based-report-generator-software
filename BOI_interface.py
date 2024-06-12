# Streamlit-based user interface
# in terminal: streamlit run ""C:\Users\eland\Desktop\code\BOI_interface.py""

#///////////////////////////////////////////////////////////////
## 0) Preliminary setup ////////////////////////////////////////
#///////////////////////////////////////////////////////////////

import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit.components.v1 as components
import os
from requests_html import HTMLSession
import jpstat
import json
import sys
import re
import wbgapi as wb
import fredapi as fa
from fredapi import Fred

#///////////////////////////////////////////////////////////////
## 1) Title and university logo ////////////////////////////////
#///////////////////////////////////////////////////////////////

### import and convert the image to bytes
def pil_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

response1 = requests.get("https://raw.githubusercontent.com/EliaLand/Bank-of-Italy-AI-based-report-generator-software/main/Graphics/BoI_logo.png")
image1 = Image.open(BytesIO(response1.content))

### define position and dimension
image1_64 = pil_to_base64(image1)

### create a container with customed settings
st.markdown(
    """
    <style>
    .container {
        display: flex;
        align-items: center; 
        padding: 10px;
    }
    .title { 
        font-size: 45px;
        font-weight: bold;
        font-family: "Roboto", sans-serif;
        margin-right: 20px
    }
    .logo {
        width: 150x;
        height: 150px;
        margin-right: 20px
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    f"""
    <div class="container">
        <img src="data:image/png;base64,{image1_64}" class="logo">
    </div>
    """,
    unsafe_allow_html=True
)
st.write("   ") 
st.write("   ")

#///////////////////////////////////////////////////////////////
## 2) Intro and infos //////////////////////////////////////////
#///////////////////////////////////////////////////////////////

### Define the introduction
st.markdown(
    """
    <div style="text-align: justify;">
        <p>
        The core feature of the Bank of Italy AI-Based Report Generator software is its AI-powered article and audio-derived text summarization capabilities. Leveraging the advanced capabilities of ChatGPT 4.0 (Da Vinci 2.0), the software scrapes real-time articles from various domestic sources (Japan in this peculiar case) based on specified topics. It then processes these articles to generate concise and informative summaries, enabling users to stay informed with the latest news and make data-driven decisions with ease. A similar elaboration process is then applied to audio tracks, from which a textual input is extracted and provided to the AI for further analysis. Eventually, the program is also equipped with textual sentiment analysis features through the deployment of the Natural Language Toolkit (NLTK) package and the Loughran McDonald Sentiment Dictionary.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

### Create the button
url1 = "https://github.com/EliaLand/Bank-of-Italy-AI-based-report-generator-software"
if st.button("more info"):
    js_code = f"""
    <script>
    window.open("{url1}");
    </script>
    """
    components.html(js_code)

#///////////////////////////////////////////////////////////////
## 3) General statistics ///////////////////////////////////////
#///////////////////////////////////////////////////////////////

st.write("## **GENERAL STATISTICS**")

## 3.1) Data import

### 3.1.1) Consumer Price Index 2020-Base Consumer Price Index

### Retrieving data for Consumer Price Index 2020-Base Consumer Price Index
### https://www.e-stat.go.jp/en/dbview?sid=0003427113 
### Frequency: monthly
### Dataframe tag: I
#jpstat.options["estat.api_key"] = "891d7fa0a7dc013ae13e2c2e5264a7f88bfc0d4c"
#dfI, note = jpstat.estat.get_data(statsDataId="0003427113")
### Data manipulation 
### Get the columns names 
#dfI_column_names = dfI.columns
### We want to drop useless columns and rows to come with a clear, and yet comprehensive, final dataframe
### Keep only national level observations
#dfI_alljapan = dfI[dfI["Area(2020-base)"].str.contains("All Japan")]
### Keep only specific disaggregated variables 
#dfI1 = dfI_alljapan[dfI_alljapan["Items(2020-base)"].str.contains("All items|Food|Fuel, light & water charges|Electricity|Gas|Water & Sewerage charges|Transportation & Communication|All items, less fresh food and energy, seasonally adjusted|Goods, seasonally adjusted|Services, seasonally adjusted")]
### Drop undeleted rows 
#phrases_to_drop = [
#    "Gas, manufactured & piped",
#    "Gas cooking tables",
#   "Food wrap",
#   "Gastrointestinal medicines",
#   "Gasoline",
#   "All items, less fresh food",
#   "Food, less fresh food",
#   "All items, less imputed rent",
#   "All items, less imputed rent & fresh food",
#   "All items, less fresh food and energy",
#   "All items, less food (less alcoholic beverages) and energy",
#   "Food products",
#   "All items, less fresh food, seasonally adjusted",
#]
#dfI1 = dfI1[~dfI1["Items(2020-base)"].isin(phrases_to_drop)]
#boolean_mask2 = dfI1["Tabulated variable"].str.contains("Change over the year", case=False, na=False)
#dfI2 = dfI1.loc[boolean_mask2]
### Adapt the time format to MM/YYYY
### Not all the values are associated to a %b. %Y format, but some (May) are formatted on a %b %Y structure
#def correct_dateformat(date):
#    pattern = r"^[a-zA-Z]{3} \d{4}$"
#    
#    if re.match(pattern, date):
#        corrected_date = date[:3] + ". " + date[4:]
#        return corrected_date
#    else:
#        return date 
#dfI2["Time"] = dfI2["Time"].apply(correct_dateformat)
#dfI2["Time"] = pd.to_datetime(dfI2["Time"], format="%b. %Y", errors="coerce")
#dfI2["Time"] = dfI2["Time"].dt.strftime("%m/%Y")
#dfI3 = dfI2
### Reset the index
#dfI3.reset_index(drop=True, inplace=True)
### Tabulation
#dfI4 = {
#    "Time": dfI3["Time"], 
#    "Category" : dfI3["Items(2020-base)"], 
#    "Inflation Rate (% change over the year)": dfI3["Value"],    
#}
#df_IR = pd.DataFrame(dfI4)
#df_IR = df_IR.set_index("Time")
#Inflation_Dataset = df_IR

### 3.1.2) GDP (current US$) - Japan

### Retrieving data for GDP (current US$) - Japan
### https://data.worldbank.org/indicator/NY.GDP.MKTP.CD?locations=JP 
### Frequency: yearly
### Dataframe tag: Y
dfY = wb.data.DataFrame("NY.GDP.MKTP.CD", "JPN").transpose()
### Data manipulation 
### Get the columns names 
dfY_column_names = dfY.columns
### Rename columns to better fit our vocabulary
dfY1 = dfY.rename(columns={"JPN": "GDP"})
### Reset the index, making "economy" a regular column and assign to that new column the name "Year" 
dfY1.reset_index(inplace=True) 
dfY1.rename(columns={"index": "Time"}, inplace=True) 
### Modify the time format, by extracting the year part from the "Year" column
dfY1["Time"] = dfY1["Time"].str.slice(start=2) 
### Tabulation
dfY2 = {
    "Time": dfY1["Time"],  
    "GDP (current US$)": dfY1["GDP"],    
}
df_GDP = pd.DataFrame(dfY2)
df_GDP = df_GDP.sort_values(by="Time", ascending=False)
df_GDP = df_GDP.set_index("Time")
GDP_Dataset = df_GDP

### 3.1.3) Japanese Yen to U.S. Dollar Spot Exchange Rate 

### Retrieving data for Japanese Yen to U.S. Dollar Spot Exchange Rate 
### https://fred.stlouisfed.org/series/EXJPUS 
### Frequency: monthly
### Dataframe tag: yen
fred = Fred(api_key="a8f0cdf1d0b64d1188b9c64ed64c77b6")
dfyen = fred.get_series("EXJPUS")
dfyen = dfyen.to_frame()
### Data manipulation 
### Get the columns names 
dfyen_column_names = dfyen.columns
### Rename columns to better fit our vocabulary
dfyen1 = dfyen.rename(columns={dfyen.columns[0]: "JPY/USD"})
### Reset the index, making the time index a regular column and assign to that new column the name "Year"
dfyen1.reset_index(inplace=True) 
dfyen1.rename(columns={"index": "Time"}, inplace=True) 
### Adapt the time format to MM/YYY
dfyen1["Time"] = pd.to_datetime(dfyen1["Time"], format="%m/%Y", errors="coerce")
dfyen2 = dfyen1
### Tabulation
dfyen3 = {
    "Time": dfyen2["Time"],  
    "JPY/USD Spot Exchange Rate": dfyen2["JPY/USD"],    
}
df_exy = pd.DataFrame(dfyen3)
df_exy = df_exy.sort_values(by="Time", ascending=False)
df_exy["Time"] = df_exy["Time"].dt.strftime("%m/%Y")
df_exy = df_exy.set_index("Time")
JPY_USD_SER_Dataset = df_exy

## 3.2) Datataset selection tool

## Tool setup
datasets_bundle = ["Inflation_Dataset", "GDP_Dataset", "JPY_USD_SER_Dataset"]
selected_datasets = st.multiselect("Select one or more datasets", datasets_bundle)
if selected_datasets:
## Save the selected datasets names in a list
    user_datasets = list(selected_datasets)