# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 21:12:27 2024

@author: perla
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data
def load_data():
    # Replace 'username', 'repository', 'branch', and 'filename.csv' with your actual GitHub info
    url = 'https://github.com/PerlaMazloum/Viz-320/blob/main/253e7b1c8f53c3b20d011a5cec87aedc_20240907_120736.csv'
    data = pd.read_csv(url)
    
    # Filter for 'Food Price Inflation' category
    data = data[data['Item'] == "Food price inflation"]
    
    # Convert EndDate to datetime and clean the dataset
    data['EndDate'] = pd.to_datetime(data['EndDate'], errors='coerce')
    data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
    
    # Drop rows with missing values
    data = data.dropna(subset=['EndDate', 'Year', 'Value'])
    
    return data

df = load_data()

# Page Title and Intro
st.title("Interactive Visualizations: Food Price Inflation")
st.write("""
This interactive dashboard presents data on food price inflation over time, allowing you to explore trends in Consumer Price Index (CPI) values for food. 
You can interact with the data by selecting specific years, months, and chart types to gain insights into how food prices have changed over time.
Use the sidebar to customize your view of the data!
""")

# Sidebar filters
st.sidebar.header("Filter Options")

# Year range slider
year_range = st.sidebar.slider("Select Year Range", int(df['Year'].min()), int(df['Year'].max()), (2000, 2020))

# Month selector
month_options = df['Month'].unique()
selected_month = st.sidebar.multiselect("Select Month(s)", month_options, default=month_options)

# Chart type selector
chart_type = st.sidebar.selectbox("Select Chart Type", ['Line Chart', 'Bar Chart', 'Area Chart'])

# Filter data based on the selections
filtered_data = df[(df['Year'].between(year_range[0], year_range[1])) & (df['Month'].isin(selected_month))]

# Customized context based on the chart type
st.subheader(f"Food Price Inflation Data from {year_range[0]} to {year_range[1]}")
if chart_type == 'Line Chart':
    st.write(f"""
    The **line chart** below shows the food price inflation trends over time. Line charts are ideal for observing trends and fluctuations in food prices, 
    helping you visualize how inflation has progressed across different months and years. This chart will highlight both subtle and major shifts in CPI values.
    """)
elif chart_type == 'Bar Chart':
    st.write(f"""
    The **bar chart** provides a comparison of food price inflation values over the selected period. Bar charts are useful when comparing CPI values for different time frames, 
    making it easy to see which months or years have experienced higher inflation. The height of each bar reflects the magnitude of the price increase.
    """)
else:  # Area chart
    st.write(f"""
    The **area chart** below shows the cumulative food price inflation over time. It is particularly useful for showing the total inflationary pressure built over the years. 
    This type of chart emphasizes the magnitude of the inflation, making it easier to see which time periods contributed the most to cumulative price increases.
    """)

# Display the filtered data
st.write(f"Displaying data for Food Price Inflation between {year_range[0]} and {year_range[1]} for the months: {', '.join(selected_month)}")

# Choose chart type based on user input
if chart_type == 'Line Chart':
    fig = px.line(filtered_data, x='EndDate', y='Value', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]})',
                  labels={'EndDate': 'Date', 'Value': 'CPI Value'}, markers=True)
elif chart_type == 'Bar Chart':
    fig = px.bar(filtered_data, x='EndDate', y='Value', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]})',
                 labels={'EndDate': 'Date', 'Value': 'CPI Value'})
else:  # Area chart
    fig = px.area(filtered_data, x='EndDate', y='Value', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]})',
                  labels={'EndDate': 'Date', 'Value': 'CPI Value'})

# Show the chart
st.plotly_chart(fig)

# Enhanced insights based on data
st.subheader("Key Insights:")
st.write("""
- **Long-term Trend**: Over the selected years, you can observe whether food price inflation has been gradually rising, stabilizing, or fluctuating. This can be correlated with external factors such as economic downturns, global events, or changes in food supply.
- **Seasonal Patterns**: By focusing on specific months, such as peak harvest or holiday seasons, you can explore how food prices behave annually. Typically, inflationary pressures may rise during certain months due to higher demand or supply chain constraints.
- **Economic Impact**: Sharp increases in food prices may be indicative of inflationary pressure in the broader economy. Observing how food prices change compared to general CPI can provide clues about the impact on household spending and overall economic health.
- **Short-term Shocks**: Sudden spikes in food price inflation may indicate short-term supply chain disruptions, such as natural disasters, political instability, or pandemics. These can cause temporary but significant price changes.
- **Regional Comparisons**: Although this dataset focuses on overall food inflation, it can provide a foundation for comparing regional or global inflation trends and how external factors influence different regions.
- **Impact of Policies**: Changes in food subsidies, tariffs, or trade policies may reflect in price inflation. Identifying sharp changes in CPI after major policy announcements can provide insight into the effectiveness of these measures.
""")
