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
chart_type = st.sidebar.selectbox("Select Chart Type", ['Line Chart', 'Bar Chart', 'Area Chart', 'Box Plot', 'Pie Chart'])

# Aggregation type selector
aggregation_type = st.sidebar.selectbox("Select Aggregation Type", ['Sum', 'Average', 'Median'])

# Filter data based on the selections
filtered_data = df[(df['Year'].between(year_range[0], year_range[1])) & (df['Month'].isin(selected_month))]

# Group the data based on the selected aggregation type
if aggregation_type == 'Sum':
    grouped_data = filtered_data.groupby(['Month', 'Year'], as_index=False).agg({'Value': 'sum'})
elif aggregation_type == 'Average':
    grouped_data = filtered_data.groupby(['Month', 'Year'], as_index=False).agg({'Value': 'mean'})
else:
    grouped_data = filtered_data.groupby(['Month', 'Year'], as_index=False).agg({'Value': 'median'})

# Customized context based on the chart type
st.subheader(f"Food Price Inflation Data from {year_range[0]} to {year_range[1]} ({aggregation_type})")
fig = None  # Initialize `fig` to avoid NameError

# Add Interactive Tooltips for each chart type
if chart_type == 'Line Chart':
    st.write(f"""
    The **line chart** below shows the food price inflation trends over time, aggregated by {aggregation_type}. 
    Line charts are ideal for observing trends and fluctuations in food prices, helping you visualize how inflation has progressed across different months and years.
    """)
    fig = px.line(grouped_data, x='Year', y='Value', color='Month', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]}) - {aggregation_type}',
                  labels={'Year': 'Year', 'Value': 'CPI Value'})
    fig.update_traces(hovertemplate='<b>Year</b>: %{x}<br><b>CPI Value</b>: %{y}')

elif chart_type == 'Bar Chart':
    st.write(f"""
    The **bar chart** provides a comparison of food price inflation values over the selected period, aggregated by {aggregation_type}. 
    Bar charts are useful when comparing CPI values for different time frames, making it easy to see which months or years have experienced higher inflation.
    """)
    fig = px.bar(grouped_data, x='Year', y='Value', color='Month', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]}) - {aggregation_type}',
                 labels={'Year': 'Year', 'Value': 'CPI Value'})
    fig.update_traces(hovertemplate='<b>Year</b>: %{x}<br><b>CPI Value</b>: %{y}')

elif chart_type == 'Area Chart':
    st.write(f"""
    The **area chart** below shows the cumulative food price inflation over time, aggregated by {aggregation_type}. 
    It emphasizes the magnitude of the inflation, making it easier to see which time periods contributed the most to cumulative price increases.
    """)
    fig = px.area(grouped_data, x='Year', y='Value', color='Month', title=f'Food Price Inflation ({year_range[0]} - {year_range[1]}) - {aggregation_type}',
                  labels={'Year': 'Year', 'Value': 'CPI Value'})
    fig.update_traces(hovertemplate='<b>Year</b>: %{x}<br><b>CPI Value</b>: %{y}')

elif chart_type == 'Box Plot':
    st.write(f"""
    The **box plot** below shows the distribution of CPI values across different months, aggregated by {aggregation_type}. This chart is helpful for identifying seasonal patterns and outliers in the data.
    """)
    # Ensure the correct chronological order of months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # Convert the 'Month' column to a categorical type with the defined order
    grouped_data['Month'] = pd.Categorical(grouped_data['Month'], categories=month_order, ordered=True)
    
    # Sort the DataFrame by the ordered months
    grouped_data = grouped_data.sort_values(by='Month')
    
    # Create the box plot
    fig = px.box(grouped_data, x='Month', y='Value', title=f'Box Plot of CPI Distribution by Month ({aggregation_type})',
                 labels={'Month': 'Month', 'Value': 'CPI Value'})
    fig.update_traces(hovertemplate='<b>Month</b>: %{x}<br><b>CPI Value</b>: %{y}')

elif chart_type == 'Pie Chart':
    st.write(f"""
    The **pie chart** below shows the distribution of CPI values across different months for the most recent year, aggregated by {aggregation_type}.
    """)
    # Filter the dataset to include data from the most recent year available
    latest_year = grouped_data['Year'].max()
    df_latest_year = grouped_data[grouped_data['Year'] == latest_year]
    
    # Group data by Month to get the total CPI for each month
    df_latest_year_grouped = df_latest_year.groupby('Month', as_index=False).agg({'Value': 'sum'})
    
    # Sort by CPI values for better clarity in color assignment
    df_latest_year_grouped = df_latest_year_grouped.sort_values(by='Value', ascending=False)
    
    # Create a pie chart to show CPI distribution by month
    fig = px.pie(df_latest_year_grouped, 
                 values='Value', 
                 names='Month', 
                 title=f'CPI Distribution by Month for {latest_year} ({aggregation_type})',
                 color='Value',
                 color_discrete_sequence=px.colors.sequential.Viridis)

    # Update hover information
    fig.update_traces(hovertemplate='<b>Month</b>: %{label}<br><b>CPI Value</b>: %{value:.2f}')

# Ensure `fig` is not None before trying to display it
if fig is not None:
    st.plotly_chart(fig)
else:
    st.write("No chart is available for the selected options. Please adjust the filters.")

# Key Insights Section
st.subheader("Key Insights:")
st.write(f"""
- **Aggregation Method**: The data displayed is aggregated by the selected method: {aggregation_type}. This allows you to explore different summaries of the data.
- **Long-term Trend**: Over the selected years, you can observe whether food price inflation has been gradually rising, stabilizing, or fluctuating. This can be correlated with external factors such as economic downturns, global events, or changes in food supply.
- **Seasonal Patterns**: By focusing on specific months, such as peak harvest or holiday seasons, you can explore how food prices behave annually. Typically, inflationary pressures may rise during certain months due to higher demand or supply chain constraints.
- **Economic Impact**: Sharp increases in food prices may be indicative of inflationary pressure in the broader economy. Observing how food prices change compared to general CPI can provide clues about the impact on household spending and overall economic health.
""")
