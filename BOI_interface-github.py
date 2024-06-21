# Streamlit-based user interface
# in terminal: streamlit run "C:\Users\eland\Desktop\code\BOI_interface.py"

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
from matplotlib.ticker import MultipleLocator
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
from lxml.html.clean import Cleaner
import numpy as np
import matplotlib.cm as cm
import speech_recognition as sr
import tempfile
import fitz
from bs4 import BeautifulSoup
import openai
from openai import OpenAI
from datetime import datetime
from translate import Translator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

#///////////////////////////////////////////////////////////////
## 1) Title and university logo ////////////////////////////////
#///////////////////////////////////////////////////////////////

### import and convert the image to bytes
def pil_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

response1 = requests.get("https://raw.githubusercontent.com/EliaLand/Bank-of-Italy-AI-based-report-generator-software/main/Graphics/Logo_Banca_d'Italia.png")
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
jpstat.options["estat.api_key"] = "YOUR API KEY"
dfI, note = jpstat.estat.get_data(statsDataId="0003427113")
### Data manipulation 
### Get the columns names 
dfI_column_names = dfI.columns
### We want to drop useless columns and rows to come with a clear, and yet comprehensive, final dataframe
### Keep only national level observations
dfI_alljapan = dfI[dfI["Area(2020-base)"].str.contains("All Japan")]
### Keep only specific disaggregated variables 
dfI1 = dfI_alljapan[dfI_alljapan["Items(2020-base)"].str.contains("All items|Food|Fuel, light & water charges|Electricity|Gas|Water & Sewerage charges|Transportation & Communication|All items, less fresh food and energy, seasonally adjusted|Goods, seasonally adjusted|Services, seasonally adjusted")]
### Drop undeleted rows 
phrases_to_drop = [
    "Gas, manufactured & piped",
    "Gas cooking tables",
   "Food wrap",
   "Gastrointestinal medicines",
   "Gasoline",
   "All items, less fresh food",
   "Food, less fresh food",
   "All items, less imputed rent",
   "All items, less imputed rent & fresh food",
   "All items, less fresh food and energy",
   "All items, less food (less alcoholic beverages) and energy",
   "Food products",
   "All items, less fresh food, seasonally adjusted",
]
dfI1 = dfI1[~dfI1["Items(2020-base)"].isin(phrases_to_drop)]
boolean_mask2 = dfI1["Tabulated variable"].str.contains("Change over the year", case=False, na=False)
dfI2 = dfI1.loc[boolean_mask2]
### Adapt the time format to MM/YYYY
### Not all the values are associated to a %b. %Y format, but some (May) are formatted on a %b %Y structure
def correct_dateformat(date):
    pattern = r"^[a-zA-Z]{3} \d{4}$"
    if re.match(pattern, date):
        corrected_date = date[:3] + ". " + date[4:]
        return corrected_date
    else:
        return date 
dfI2["Time"] = dfI2["Time"].apply(correct_dateformat)
dfI2["Time"] = pd.to_datetime(dfI2["Time"], format="%b. %Y", errors="coerce")
dfI2["Time"] = dfI2["Time"].dt.strftime("%m/%Y")
dfI3 = dfI2
### Reset the index
dfI3.reset_index(drop=True, inplace=True)
### Tabulation
dfI4 = {
    "Time": dfI3["Time"], 
    "Inflation Rate (% change over the year)": dfI3["Value"],
    "Class" : dfI3["Items(2020-base)"]    
}
df_IR = pd.DataFrame(dfI4)
df_IR = df_IR.sort_values(by="Time", ascending=True)
df_IR = df_IR.set_index("Time")

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
df_GDP = df_GDP.sort_values(by="Time", ascending=True)
df_GDP = df_GDP.set_index("Time")

### 3.1.3) Japanese Yen to U.S. Dollar Spot Exchange Rate 

### Retrieving data for Japanese Yen to U.S. Dollar Spot Exchange Rate 
### https://fred.stlouisfed.org/series/EXJPUS 
### Frequency: monthly
### Dataframe tag: yen
fred = Fred(api_key="YOUR API KEY")
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
df_exy = df_exy.sort_values(by="Time", ascending=True)
df_exy["Time"] = df_exy["Time"].dt.strftime("%m/%Y")
df_exy = df_exy.set_index("Time")

## 3.2) Data plotting

## Dataset selection Tool setup
datasets_txt_bundle = ["GDP Dataset", "JPY/USD Spot Exchange Rate Dataset", "Inflation Rate Dataset"]
dataset_loaders = {
    "GDP Dataset": df_GDP,
    "JPY/USD Spot Exchange Rate Dataset": df_exy,
#    "Inflation Rate Dataset": df_IR
}
selected_datasets = st.multiselect("Select one or more datasets", datasets_txt_bundle)
if selected_datasets:
## Save the selected datasets names in a list
#__________________________________________
    user_datasets = list(selected_datasets)
#__________________________________________     

### 3.2.1) GDP Dataset
### Time filtering tool  
    if "GDP Dataset" in user_datasets:
        df = dataset_loaders["GDP Dataset"]
        first_column_name = df.columns[0]
        st.write(f"### {first_column_name}")
        min_year = df.index.min()
        max_year = df.index.max()
#_____________________________________________________________________________________________________________________________________________________________   
        selected_years = st.slider("Select time span for GDP Dataset", min_value=int(min_year), max_value=int(max_year), value=(int(min_year), int(max_year)))
#_____________________________________________________________________________________________________________________________________________________________
### Plotting        
        plt.figure(figsize=(10, 6)) 
        x_min = f"{selected_years[0]}"
        x_max = f"{selected_years[1]}"
        time_filtered_df = df[(df.index >= str(x_min)) & (df.index <= str(x_max))]
#_____________________________________________________________________________________________________________________________                  
        plt.fill_between(time_filtered_df.index, time_filtered_df[first_column_name], linestyle="-", alpha=1, color="#FE420F")
#_____________________________________________________________________________________________________________________________               
## General graphical settings                   
        plt.title(f"{first_column_name} over time")
        plt.xlabel("Time")
        plt.ylabel("GDP (current US$, trillion)")
        plt.xticks(rotation=45)
        dfxt = plt.gca()
        dfxt.xaxis.set_major_locator(MultipleLocator(3)) 
        plt.grid(True, linestyle="--", linewidth=0.5, color="grey")                
        plt.legend(loc="upper left")
        st.pyplot(plt)
        
### 3.2.2) JPY/USD Spot Exchange Rate Dataset
### Time filtering tool
    if "JPY/USD Spot Exchange Rate Dataset" in user_datasets:
        df = dataset_loaders["JPY/USD Spot Exchange Rate Dataset"]
        first_column_name = df.columns[0]
        st.write(f"### {first_column_name}")       
### Convert dates to datetime format format for display
### Preserve the original format
        original_format_index = df.index.copy()
### Update to datetime format                
        df.index = pd.to_datetime(df.index)
        min_month = df.index.min().date()
        max_month = df.index.max().date()
#_______________________________________________________________________________________________________________________________________________________________________________________
        selected_months = st.slider("Select time span for JPY/USD Spot Exchange Rate Dataset", min_value=min_month, max_value=max_month, value=(min_month, max_month), format="MM/YYYY")
#_______________________________________________________________________________________________________________________________________________________________________________________
### Plotting
        plt.figure(figsize=(10, 6)) 
        x_min = f"{selected_months[0]}"
        x_max = f"{selected_months[1]}"
        time_filtered_df = df[(df.index >= str(x_min)) & (df.index <= str(x_max))]
#_________________________________________________________________________________________________________________________                    
        plt.plot(time_filtered_df.index, time_filtered_df[first_column_name], linestyle="-", linewidth=2, color="#C1F80A")
#_________________________________________________________________________________________________________________________
### General graphical settings
        plt.title(f"{first_column_name} over time")
        plt.xlabel("Time")
        plt.ylabel(f"{first_column_name}")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle="--", linewidth=0.5, color="grey")                
        plt.legend(loc="upper left")
        st.pyplot(plt)

### 3.2.3) Inflation Dataset
### Time filtering tool
    if "Inflation Rate Dataset" in user_datasets:
        df = dataset_loaders["Inflation Rate Dataset"]
        first_column_name = df.columns[0]
        st.write(f"### {first_column_name}")       
### Convert dates to datetime format format for display
### Preserve the original format
        original_format_index = df.index.copy()
### Update to datetime format                
        df.index = pd.to_datetime(df.index)
        min_month = df.index.min().date()
        max_month = df.index.max().date()
#___________________________________________________________________________________________________________________________________________________________________________
        selected_months = st.slider("Select time span for Inflation Rate Dataset", min_value=min_month, max_value=max_month, value=(min_month, max_month), format="MM/YYYY")
#___________________________________________________________________________________________________________________________________________________________________________
### Class selection tool 
        classes_txt_bundle = ["All items", "Food", "Fuel, light & water charges", "Electricity", "Gas", "Water & Sewerage charges", "Transportation & Communication", "All items, less fresh food and energy, seasonally adjusted", "Goods, seasonally adjusted", "Services, seasonally adjusted"]
#___________________________________________________________________________________________________    
        selected_classes = st.multiselect("Select one or more classes of items", classes_txt_bundle)
#___________________________________________________________________________________________________
### Plotting
        plt.figure(figsize=(10, 6))
        x_min = f"{selected_months[0]}"
        x_max = f"{selected_months[1]}"
        time_filtered_df = df[(df.index >= str(x_min)) & (df.index <= str(x_max))]           
### General classes
        if "All items" in selected_classes:
            class_filtered_df = time_filtered_df[time_filtered_df["Class"] == "All items"]
            plt.fill_between(class_filtered_df.index, class_filtered_df["Inflation Rate (% change over the year)"], color="#01153E", alpha=1, label="All items")
        if "All items, less fresh food and energy, seasonally adjusted" in selected_classes: 
            class_filtered_df = time_filtered_df[time_filtered_df["Class"] == "All items, less fresh food and energy, seasonally adjusted"]
            plt.fill_between(class_filtered_df.index, class_filtered_df["Inflation Rate (% change over the year)"], color="#E50000", alpha=1, label="All items, less fresh food and energy, seasonally adjusted")
### Specific classes        
        if any(cl in selected_classes for cl in ["Food", "Fuel, light & water charges", "Electricity", "Gas", "Water & Sewerage charges", "Transportation & Communication", "Goods, seasonally adjusted", "Services, seasonally adjusted"]):
            specific_classes = ["Food", "Fuel, light & water charges", "Electricity", "Gas", "Water & Sewerage charges", "Transportation & Communication", "Goods, seasonally adjusted", "Services, seasonally adjusted"] 
            colors=cm.get_cmap("tab10", len(specific_classes))
            for i,cl in specific_classes: 
                if cl in selected_classes:
                    class_filtered_df = time_filtered_df[time_filtered_df["Class"] == cl]
#_____________________________________________________________________________________________________________________________________________________________
                    plt.plot(class_filtered_df.index, class_filtered_df["Inflation Rate (% change over the year)"], linestyle="-", color=colors(i), label=cl) 
#_____________________________________________________________________________________________________________________________________________________________
### General graphical settings
        plt.title(f"{first_column_name} over time")
        plt.xlabel("Time")
        plt.ylabel(f"{first_column_name}")
        plt.xticks(rotation=45)
        dfxt.xaxis.set_major_locator(MultipleLocator(2)) 
        plt.style.use("default") 
        plt.style.use("default")                
        plt.legend(loc="upper left")
        plt.show()

#///////////////////////////////////////////////////////////////
## 4) Textual Input ////////////////////////////////////////////
#///////////////////////////////////////////////////////////////

st.write("## **TEXTUAL INPUT**")

## 4.1) Text file input
st.write("### 1) PDF file")
## Define the text uploader tool, including multiple type of objects 
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
pdf_input = ""
if pdf_file is not None:
## Use fitz to open the the PDF file     
    pdf_content = pdf_file.read()
    pdf_document = fitz.open(stream=pdf_content, filetype="pdf")      
## Iterate through each page in the PDF and extract text
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
#__________________________________        
        pdf_input += page.get_text()
#__________________________________        
#   st.write(pdf_input)

## 4.2) Audio track input
st.write("### 2) Audio track")
## Define the audio track uploader tool, including multiple type of objects 
audio_file = st.file_uploader("Upload an audio file", type=["wav", "ogg", "flac"])
## Use SpeechRecognition to transcribe the audio file, i.e., get the text from the PDF source
recognizer = sr.Recognizer()
audio_input = ""
if audio_file is not None:
## Convert and save the audio track in a wav format to be handle by the tool for speech recognition    
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            try:
#___________________________________________________________________                
                audio_text = recognizer.recognize_google(audio_data)
#___________________________________________________________________
                audio_input += audio_text + "\n\n"                
                st.write("Audio succesfully transcripted")
                st.write(audio_input)
            except sr.UnknownValueError:
                st.write("Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                st.write(f"Could not request results from Google Speech Recognition service; {e}")

## 4.3) Web scraping
st.write("### 3) Web scraping")

### 4.3.1) Region selector tool
### Define regional boundaries to restrict the range of articles/papers inherent to a specific geographic area
regions_bundle = ["Japan", "Asia-Pacific", "Global", "Italy", "USA", "China"]
selected_regions = st.multiselect("Select one geographic region", regions_bundle) 

### 4.3.2) Topic selector tool
### Introduce a restriction on selected topics
topics_bundle = ["GDP", "Inflation", "Interest Rates", "Public Debt", "Monetary Policy"]
selected_topics = st.multiselect("Select one or more topics", topics_bundle)

### 4.3.3) Date selector tool
### pick a date to limit the retrieved articles to those released on the selected date 
selected_date = st.date_input("Pick a date to restrict the time frame", datetime.now())

### 4.3.4) Source selector tool 
### Select specific web/newspaper/economic journals as source to train the AI
sources_bundle = ["Japan News (Yomiuri)", "The Asahi Shimbun", "Mainichi Shimbun"]
selected_sources = st.multiselect("Select one or more Japanese domestic sources to scrape", sources_bundle)

### 4.3.5) Scraping function  
### Set parameters 
region = selected_regions
topic = selected_topics
date = selected_date
### Define a function to translate the inputs from English to Japanese for sources in Japanese language
def translate_to_japanese(text):
    translator = Translator(to_lang="ja")
    translation = translator.translate(text)
    return translation
### Define the function to scrape the selected web sources given the parameters (geographic region, date and topic)
def web_scrape_function(region, topic, date, sources):
    urls = []
    for source in sources:
        if source == "Japan News (Yomiuri)":
            urls.extend(scrape_yomiuri(region, topic, date))
        if source == "The Asahi Shimbun":
            urls.extend(scrape_asahi(region, topic, date))
        if source == "Mainichi Shimbun":
            urls.extend(scrape_mainichi(region, topic, date))
    return urls

#### 4.3.5.1) Scraping functions for Japan News (Yomiuri)
def scrape_yomiuri(region, topic, date):
#### Source base url
    date_string = date.strftime("%Y%m%d")
    base_url = f"https://japannews.yomiuri.co.jp"
    url = f"{base_url}/?s={region}+{topic}"
#### Web scraping                         
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    urls = []
#### Extract data
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        urls.append(href)
#### Filter relevant urls by inherence and date
    urls = [url for url in urls if date_string in url]
#______________
    return urls
#______________

#### 4.3.5.2) Scraping functions for The Asahi Shimbun
def scrape_asahi(region, topic, date):
#### Source base url
    base_url = f"https://www.asahi.com/ajw/search/results"
    url = f"{base_url}/?keywords={region}+{topic}+{date}"
#### Web scraping                         
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    urls = []
#### Extract data
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        urls.append(href)
#### Filter relevant urls by inherence and chronological relevance
    urls = [f"https://www.asahi.com{url}" for url in urls if "articles/" in url]
    urls = urls[:3]
#______________
    return urls
#______________

#### 4.3.5.3) Scraping functions for Mainichi Shimbun
def scrape_mainichi(region, topic, date):
#### Input traduction
    date_string = date.strftime("%Y%m%d")
    txt_input = f"{region} {topic}"
    trad_txt_input = translate_to_japanese(txt_input)
#### Source base url
    base_url = f"https://mainichi.jp"
    url = f"{base_url}/search?q=%20{trad_txt_input}&op=and&da=all&la=ja-JP"
#### Web scraping                         
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    urls = []
#### Extract data
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        urls.append(href)
#### Filter relevant urls by inherence and date
    urls = [f"https:{url}" for url in urls if "articles/" in url]
    urls = [url for url in urls if date_string in url]
#______________
    return urls
#______________

### 4.3.6) Text extraction function
def extract_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.find_all("p")   
    text = "" "".join(paragraph.text for paragraph in paragraphs)
    return text
### Define a function to translate the articles from  Japanese to English for sources in Japanese language
def translate_to_english(text):
    translator = Translator(from_lang="ja", to_lang="en")
    translation = translator.translate(text)
    return translation

### 4.3.7) Web scrape button
### Set the source textual input
web_input = ""

#__________________________________________________
### Button settings in order to avoiding page rerun
if "WEB_scrape_clicked" not in st.session_state:
    st.session_state["WEB_scrape_clicked"] = False
if "WEB_get_text_clicked" not in st.session_state:
    st.session_state["WEB_get_text_clicked"] = False
if "AI_scrape_clicked" not in st.session_state:
    st.session_state["AI_scrape_clicked"] = False
if "AI_get_text_clicked" not in st.session_state:
    st.session_state["AI_get_text_clicked"] = False
if "AI_summarize_clicked" not in st.session_state:
    st.session_state["AI_summarize_clicked"] = False
#__________________________________________________

### The object turns on the scraping function, given the selected parameters for region, topic, date and source
if st.button("WEB scrape"):
    st.session_state["WEB_scrape_clicked"] = not st.session_state["WEB_scrape_clicked"]
if st.session_state["WEB_scrape_clicked"]:
### Merge all the selected sources url lists into a single one
    for region in selected_regions:
        st.write(f"### Found articles related to {region} in the following topics (at {selected_date})")
        for topic in selected_topics:
            st.write(f"#### {topic}")
#_______________________________________________________________________________            
            web_results = web_scrape_function(region, topic, date, selected_sources)
#_______________________________________________________________________________            
            for url in web_results:
                st.write(url)

### 4.3.8) WEB get text button
    if st.button("WEB get text"):
        st.session_state["WEB_get_text_clicked"] = not st.session_state["WEB_get_text_clicked"]
    if st.session_state["WEB_get_text_clicked"]:
    ### Merge all the selected sources url lists into a single list
        web_urls = []
        for region in selected_regions:
            for topic in selected_topics:
                web_results = web_scrape_function(region, topic, date, selected_sources)            
                web_urls.extend(web_results)
### Clean the folder by removing duplicates
#_____________________________________
        web_urls = list(set(web_urls))
#_____________________________________    
        web_input = ""
        for url in web_urls:
### Differentiate across English and Japanese language sources
### However we keep the original text to avoid breaking the query allowance
            try:
                if "https://mainichi.jp" in url: 
#                   st.write(f"#### {url}")
                    article_text = extract_article_text(url)
#                   st.write(f"#### {article_text}")
                    article_text = translate_to_english(article_text)           
                else:
#                   st.write(f"#### {url}")            
                    article_text = extract_article_text(url)
#                   st.write(f"#### {article_text}")              
### Merge each article text into a single textual input for web scraping results
#_________________________________________________
                web_input += article_text + "\n\n"
#_________________________________________________ 
            except Exception as e:
                st.error(f"Error processing {url}: {e}")       
#           st.write(web_input)

## 4.4) AI scraping
st.write("### 4) AI scraping")

### 4.4.1) AI settings 
### to check program credit usage
### https://platform.openai.com/usage
### Set up OpenAI API key
### DISCLAIMER: the so API key is strictly personal and you should refrain from sharing it with strangers
### you can generate an API key on https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key by registrating a valid account and adding some credit 
### OpenAI API key-example: YOUR API KEY  
openai.api_key = "YOUR API KEY"

### 4.4.2) Define custom tools
selected_regions_ai = st.text_input("Enter your target geographic region:") 
selected_topics_ai = st.text_input("Enter the topic you are interested in:")
selected_date_ai = st.date_input("Relase date:", datetime.now())

### 4.4.3) Scraping function 
### Set parameters 
region_ai = selected_regions_ai
topic_ai = selected_topics_ai
date_ai = selected_date_ai 
### Train the AI to retrieve local sources given regional, topical and chronological parameters in order to get additional local sources that would be quite complicated to extract otherwise
def ai_scrape_function(region_ai, topic_ai, date_ai):
### Scrape using ChatGPT
    MODEL = "gpt-3.5-turbo"
    scrape_prompt = f"You are working for the Bank of Italy (Asia-Pacific delegation) and you are task is to retrieve a Python list (no comments or introduction) of urls referring to economic articles in Japanese from local sources released on {date_ai} and inherent to {region_ai}{topic_ai} (only valid urls must be accepted)."
    ai_response = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": scrape_prompt}],
        temperature=0,
        max_tokens = 100
    )
### Filter out model infos
    ai_urls = ai_response.choices[0].message.content
    filtered_ai_urls = re.findall(r'"(https?://[^\"]+)"', ai_urls)
    return filtered_ai_urls

### 4.4.4) AI scrape button
### The object turns on the AI-based scraping function, given the selected parameters for region, topic, date
### Set the source textual input
ai_input = ""
if st.button("AI scrape"):
    st.session_state["AI_scrape_clicked"] = not st.session_state["AI_scrape_clicked"]
if st.session_state["AI_scrape_clicked"]:
    st.write(f"### Found articles related to {region_ai} for {topic_ai} (at {selected_date_ai})")
    ai_urls = []
    results_ai = ai_scrape_function(region_ai, topic_ai, date_ai)
    ai_urls.extend(results_ai)
### Clean the folder by removing duplicates
#_______________________________
    ai_urls = list(set(ai_urls))
#_______________________________
    for url in ai_urls:
        st.write(url)

### 4.4.5) AI get text button
    if st.button("AI get text"):
        st.session_state["AI_get_text_clicked"] = not st.session_state["AI_get_text_clicked"]
    if st.session_state["AI_get_text_clicked"]:
### Clean the folder by removing duplicates   
        for url in ai_urls:
#           st.write(f"#### {url}") 
            article_text = extract_article_text(url)
#           st.write(f"#### {article_text}")
            article_text = translate_to_english(article_text)                         
### Merge each article text into a single textual input for web scraping results
#____________________________________________
            ai_input += article_text + "\n\n"
#____________________________________________        
#       st.write(ai_input)

#///////////////////////////////////////////////////////////////
## 5) AI ELABORATION ///////////////////////////////////////////
#///////////////////////////////////////////////////////////////

st.write("## **AI ELABORATION**")

## 5.1) AI summarize function
## Function to create a summary out of an article using AI (gpt-3.5-turbo)
## https://github.com/openai/openai-python/blob/main/src/openai/types/chat/completion_create_params.py 
def ai_summarize_function(pdf=None, audio=None, web=None, ai=None):
## Summarize by deploying gpt-3.5-turbo
    MODEL = "gpt-3.5-turbo"
    summary_prompt = f"You are working for the Bank of Italy (Asia-Pacific delegation) and you are ask to summarize the textual sources (newspaper articles, research articles, press-conference reports, etc.), which will be soon provided, in less than 400 words (mandatory), as part of a daily economic report on the Asia-Pacific region, which is the main focus of our analysis (in British English). Keep in mind that you are writing an economic report and not a literature review, the provided sources must be considered part of your consolidated knowledge on the argument. Hence, write your statements as if they were the Bank of Italy's statements and avoid mentioniong any source, unless for the sake of fostering your stances by introducing references. Here the sources are:\n"
## Add sources to the prompt if they are provided
    if pdf:
        summary_prompt += f"1) research articles: \n{pdf_input}\n"
    if audio:
        summary_prompt += f"2) press-conference reports: \n{audio_input}\n"
    if web:
        summary_prompt += f"3) newspaper economic articles: \n{web_input}\n"
    if ai:
        summary_prompt += f"4) additional sources: \n{ai_input}\n"
## AI engine settings
    ai_summary_response = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0,
        max_tokens = 500
    )
#______________________________________________________________    
    ai_summary = ai_summary_response.choices[0].message.content
#______________________________________________________________    
    return ai_summary

## 5.2) AI summary button
## The object turns on the AI-based summary function, given the previouslyretrieved textual sources
ai_summary_results = ""
if st.button("AI summarize"):
    st.session_state["AI_summarize_clicked"] = not st.session_state["AI_summarize_clicked"]
if st.session_state["AI_summarize_clicked"]:
## Set parameters
    pdf = pdf_input
    audio = audio_input
    web = web_input
    ai = ai_input
## Deploy the summarizing function
    summary_results = ai_summarize_function(pdf, audio, web, ai)
    ai_summary_results += summary_results + "\n\n"            
    st.write(ai_summary_results)

## 5.3) Tailor-made changes to the AI-generated summary
## Here we introduce a text box which can be leveraged by the user to make personalized changes into the AI-generated summary 
revised_report = st.text_input("Enter your desired report by copying and pasting the AI-generated summary into the text box and, if necessary, by manually adding your changes to the original format:")