# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 21:12:27 2024"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data
def load_data():
    url = 'https://raw.githubusercontent.com/PerlaMazloum/Viz-320/main/CPI.csv'
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

# Dynamic Theme Switching
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])

# Apply selected theme
if theme == "Dark":
    st.write('<style>body{background-color: #1e1e1e; color: #fff;}</style>', unsafe_allow_html=True)

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

# CPI Value Range slider
min_cpi, max_cpi = st.sidebar.slider("Select CPI Value Range", float(df['Value'].min()), float(df['Value'].max()), (float(df['Value'].min()), float(df['Value'].max())))

# Chart type selector
chart_type = st.sidebar.selectbox("Select Chart Type", ['Line Chart', 'Bar Chart', 'Area Chart', 'Box Plot', 'Pie Chart'])

# Filter data based on the selections
filtered_data = df[(df['Year'].between(year_range[0], year_range[1])) & 
                   (df['Month'].isin(selected_month)) & 
                   (df['Value'].between(min_cpi, max_cpi))]

# Customized context based on the chart type
st.subheader(f"Food Price Inflation Data from {year_range[0]} to {year_range[1]} (CPI Range: {min_cpi:.2f} to {max_cpi:.2f})")
fig = None  # Initialize `fig` to avoid NameError

# Add Interactive Tooltips for each chart type
if chart_type == 'Line Chart':
    st.write("""
    The **line chart** below shows the food price inflation trends over time, filtered by the selected CPI value range. 
    Line charts are ideal for observing trends and fluctuations in food prices, helping you visualize how inflation has progressed across different months and years.
    """)
    fig = px.line(filtered_data, x='EndDate', y='Value', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]})',
                  labels={'EndDate': 'Date', 'Value': 'CPI Value'}, markers=True)
    fig.update_traces(hovertemplate='<b>Date</b>: %{x}<br><b>CPI Value</b>: %{y}')
    
elif chart_type == 'Bar Chart':
    st.write("""
    The **bar chart** provides a comparison of food price inflation values over the selected period, filtered by the selected CPI value range. 
    Bar charts are useful when comparing CPI values for different time frames, making it easy to see which months or years have experienced higher inflation.
    """)
    fig = px.bar(filtered_data, x='EndDate', y='Value', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]})',
                 labels={'EndDate': 'Date', 'Value': 'CPI Value'})
    fig.update_traces(hovertemplate='<b>Date</b>: %{x}<br><b>CPI Value</b>: %{y}')

elif chart_type == 'Area Chart':
    st.write("""
    The **area chart** below shows the cumulative food price inflation over time, filtered by the selected CPI value range. 
    It emphasizes the magnitude of the inflation, making it easier to see which time periods contributed the most to cumulative price increases.
    """)
    fig = px.area(filtered_data, x='EndDate', y='Value', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]})',
                  labels={'EndDate': 'Date', 'Value': 'CPI Value'})
    fig.update_traces(hovertemplate='<b>Date</b>: %{x}<br><b>CPI Value</b>: %{y}')

elif chart_type == 'Box Plot':
    st.write("""
    The **box plot** below shows the distribution of CPI values across different months, filtered by the selected CPI value range.
    This chart is helpful for identifying seasonal patterns and outliers in the data, as well as the spread of CPI values throughout the year.
    """)
    # Ensure the correct chronological order of months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # Convert the 'Month' column to a categorical type with the defined order
    filtered_data['Month'] = pd.Categorical(filtered_data['Month'], categories=month_order, ordered=True)
    
    # Sort the DataFrame by the ordered months
    filtered_data = filtered_data.sort_values(by='Month')
    
    # Create the box plot
    fig = px.box(filtered_data, x='Month', y='Value', title='Box Plot of CPI Distribution by Month',
                 labels={'Month': 'Month', 'Value': 'CPI Value'})
    fig.update_traces(hovertemplate='<b>Month</b>: %{x}<br><b>CPI Value</b>: %{y}')

elif chart_type == 'Pie Chart':
    st.write("""
    The **pie chart** below shows the distribution of CPI values across different months for the most recent year, filtered by the selected CPI value range.
    """)
    # Filter the dataset to include data from the most recent year available
    latest_year = filtered_data['Year'].max()
    df_latest_year = filtered_data[filtered_data['Year'] == latest_year]
    
    # Group data by Month to get the total CPI for each month
    df_latest_year_grouped = df_latest_year.groupby('Month', as_index=False).agg({'Value': 'sum'})
    
    # Sort by CPI values for better clarity in color assignment
    df_latest_year_grouped = df_latest_year_grouped.sort_values(by='Value', ascending=False)
    
    # Create a pie chart to show CPI distribution by month
    fig = px.pie(df_latest_year_grouped, 
                 values='Value', 
                 names='Month', 
                 title=f'CPI Distribution by Month for {latest_year}',
                 color='Value',
                 color_discrete_sequence=px.colors.sequential.Viridis)

    # Update hover information
    fig.update_traces(hovertemplate='<b>Month</b>: %{label}<br><b>CPI Value</b>: %{value:.2f}')

# Ensure `fig` is not None before trying to display it
if fig is not None:
    st.plotly_chart(fig)
else:
    st.write("No chart is available for the selected options. Please adjust the filters.")

# Downloadable Report Section
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(filtered_data)

st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='filtered_food_price_inflation_data.csv',
    mime='text/csv',
)



# Key Insights Section
st.subheader("Key Insights:")
st.write(f"""
- **CPI Range Filtering**: The data displayed is filtered to show only CPI values between {min_cpi:.2f} and {max_cpi:.2f}. This allows you to focus on specific ranges of inflation.
- **Long-term Trend**: Over the selected years, you can observe whether food price inflation has been gradually rising, stabilizing, or fluctuating. This can be correlated with external factors such as economic downturns, global events, or changes in food supply.
- **Seasonal Patterns**: By focusing on specific months, such as peak harvest or holiday seasons, you can explore how food prices behave annually. Typically, inflationary pressures may rise during certain months due to higher demand or supply chain constraints.
- **Economic Impact**: Sharp increases in food prices may be indicative of inflationary pressure in the broader economy. Observing how food prices change compared to general CPI can provide clues about the impact on household spending and overall economic health.
""")
