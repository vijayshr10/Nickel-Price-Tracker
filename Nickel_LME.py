import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import plotly.express as px


# Function to fetch and parse data
def fetch_nickel_data():
    url = "https://www.trmsa.org.tw/front/metal?qryMetal=ni"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    script_tag = soup.find('script', string=re.compile('mainJsonString'))
    if script_tag:
        json_data_match = re.search(r'var mainJsonString = (\[.*?\]);', script_tag.string, re.DOTALL)
        if json_data_match:
            data_list = json.loads(json_data_match.group(1))
            df = pd.DataFrame(data_list)
            
            # Keep only 'date', 'spotLow', and 'spotHigh' columns and rename them
            if 'date' in df.columns and 'spotHigh' in df.columns and 'spotLow' in df.columns:
                df = df[['date', 'spotLow', 'spotHigh']]
                df = df.rename(columns={'spotLow': 'Bid', 'spotHigh': 'Offer'})
                
                # Convert 'date' column to datetime and keep only the date (no time)
                df['date'] = pd.to_datetime(df['date']).dt.date
                
                # Remove rows where 'Bid' and 'Offer' are both 0
                df = df[(df['Bid'] != 0) | (df['Offer'] != 0)]
                
                # Sort data by 'date'
                df = df.sort_values(by='date')
                
                # Calculate the difference between 'Offer' and 'Bid'
                df['Difference'] = df['Offer'] - df['Bid']
                
                # Remove rows where 'Difference' is 0 or NaN
                df = df[df['Difference'].notna() & (df['Difference'] != 0)]
                
            return df
    return pd.DataFrame()

# Streamlit App Layout
st.title("Nickel Price Data Visualization")

st.write("Fetching latest Nickel price data.")

# Fetch and store sorted data
data = fetch_nickel_data()

if not data.empty:
    # Upper part (Nickel Price plot)
    st.subheader("Nickel Price Trend (Bid & Offer)")
    fig = px.line(data, x='date', y=['Bid', 'Offer'], title='Nickel Price Trend')
    fig.update_traces(mode='lines+markers')
    st.plotly_chart(fig)
    
    st.subheader("Nickel Price Volatility, Difference (Offer - Bid)")
    fig_diff = px.bar(data, x='date', y='Difference', title='Difference between Offer and Bid (Offer - Bid)')
    st.plotly_chart(fig_diff)

    
    st.subheader("Latest Data")
    st.dataframe(data)  # Show the sorted data table
    st.write("Table can also be downloaded.")

else:
    st.error("Failed to fetch data. Try again later.")

