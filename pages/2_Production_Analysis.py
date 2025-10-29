import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# Import utility functions
from utils.data_loader import load_production_data, get_sample_data_path
from utils.visualization import plot_production_trend
from utils.session_state import initialize_session_state, set_production_data
from utils.style_manager import load_css, apply_theme, display_header_image

apply_theme(theme="light")  # or "dark"
load_css()
#display_header_image("assets/header_banner.png", height="220px")
display_header_image(
    "assets/header_banner.png",
    title="Oil & Gas Data Dashboard",
    subtitle="",
    height="225px"
)

# Set page configuration
st.set_page_config(
    page_title="Production Analysis",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
initialize_session_state()

# Main title
st.title("Production Data Analysis")

# Sidebar for data loading and controls
st.sidebar.header("Data Loading")

# Option to use sample data or upload own data
data_source = st.sidebar.radio("Select Data Source", ["Use Sample Data", "Upload CSV File"])

if data_source == "Use Sample Data":
    sample_path = get_sample_data_path('production')
    if sample_path and os.path.exists(sample_path):
        df = load_production_data(sample_path)
        if df is not None:
            set_production_data(df)
            st.sidebar.success("Sample data loaded successfully!")
    else:
        st.sidebar.error("Sample data not found. Please upload your own data.")
        data_source = "Upload CSV File"

if data_source == "Upload CSV File":
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = load_production_data(uploaded_file)
        if df is not None:
            set_production_data(df)
            st.sidebar.success("File uploaded successfully!")

# Check if data is loaded
if st.session_state.production_data is not None:
    df = st.session_state.production_data
    
    # Display the DataFrame
    st.subheader("Production Data")
    st.dataframe(df.head())
    
    # Check if required columns exist
    required_columns = ['Date']
    production_columns = [col for col in df.columns if 'production' in col.lower() or 'oil' in col.lower() or 'gas' in col.lower()]
    
    if all(col in df.columns for col in required_columns) and production_columns:
        # Set Date as index for resampling
        df_indexed = df.set_index('Date')
        
        # Check if Well_ID column exists for grouping
        if 'Well_ID' in df.columns:
            # Sidebar for well selection
            st.sidebar.header("Well Selection")
            available_wells = df['Well_ID'].unique().tolist()
            selected_wells = st.sidebar.multiselect("Select Wells", available_wells, default=available_wells)
            
            if selected_wells:
                # Filter data by selected wells
                filtered_df = df[df['Well_ID'].isin(selected_wells)]
                
                # Group by Well_ID and Date, then resample
                st.subheader("Resampled Production Data")
                resample_freq = st.selectbox("Select Resampling Frequency", ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])
                
                freq_map = {
                    "Daily": "D",
                    "Weekly": "W",
                    "Monthly": "M",
                    "Quarterly": "Q",
                    "Yearly": "Y"
                }
                
                # Set Date as index
                filtered_df_indexed = filtered_df.set_index('Date')
                
                # Group by Well_ID and resample
                resampled_dfs = []
                for well in selected_wells:
                    well_data = filtered_df_indexed[filtered_df_indexed['Well_ID'] == well]
                    resampled = well_data.resample(freq_map[resample_freq]).sum()
                    resampled['Well_ID'] = well
                    resampled_dfs.append(resampled)
                
                if resampled_dfs:
                    resampled_df = pd.concat(resampled_dfs).reset_index()
                    st.dataframe(resampled_df.head())
                    
                    # Production trend visualization
                    st.subheader("Production Trends")
                    
                    # Select production column to visualize
                    production_col = st.selectbox("Select Production Column", production_columns)
                    
                    # Create production trend plot
                    fig = plot_production_trend(resampled_df, production_col, 'Well_ID')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate and plot moving averages
                    st.subheader("Moving Averages")
                    
                    # Group by date to get total production
                    total_production = resampled_df.groupby('Date')[production_col].sum().reset_index()
                    
                    # Calculate moving averages
                    window_size = st.slider("Moving Average Window Size", 2, 12, 3)
                    total_production[f'{window_size}-Period MA'] = total_production[production_col].rolling(window=window_size).mean()
                    
                    # Plot total production with moving average
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=total_production['Date'], y=total_production[production_col],
                                            mode='lines', name='Total Production'))
                    fig.add_trace(go.Scatter(x=total_production['Date'], y=total_production[f'{window_size}-Period MA'],
                                            mode='lines', name=f'{window_size}-Period Moving Average'))
                    
                    fig.update_layout(title=f"Total {production_col} with {window_size}-Period Moving Average",
                                    xaxis_title="Date",
                                    yaxis_title=production_col,
                                    hovermode="x unified")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Decline curve analysis
                    st.subheader("Decline Curve Analysis")
                    
                    # Simple exponential decline model
                    if st.checkbox("Show Decline Curve Analysis"):
                        # Filter out zero or NaN values
                        valid_data = total_production[total_production[production_col] > 0].copy()
                        
                        if len(valid_data) > 5:  # Need enough data points for meaningful analysis
                            # Convert dates to numeric (days since first date)
                            valid_data['Days'] = (valid_data['Date'] - valid_data['Date'].min()).dt.days
                            
                            # Take log of production for linear regression
                            valid_data['Log_Production'] = np.log(valid_data[production_col])
                            
                            # Simple linear regression on log-transformed data
                            from scipy import stats
                            slope, intercept, r_value, p_value, std_err = stats.linregress(
                                valid_data['Days'], valid_data['Log_Production'])
                            
                            # Calculate decline rate
                            decline_rate = -slope * 365  # Annual decline rate
                            
                            # Generate prediction
                            max_days = valid_data['Days'].max()
                            forecast_days = np.arange(0, max_days * 1.5)  # Extend 50% into the future
                            forecast_production = np.exp(intercept + slope * forecast_days)
                            
                            # Create forecast dates
                            first_date = valid_data['Date'].min()
                            forecast_dates = [first_date + pd.Timedelta(days=int(d)) for d in forecast_days]
                            
                            # Plot actual vs forecast
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=valid_data['Date'], y=valid_data[production_col],
                                                    mode='markers', name='Actual Production'))
                            fig.add_trace(go.Scatter(x=forecast_dates, y=forecast_production,
                                                    mode='lines', name='Exponential Decline Model'))
                            
                            fig.update_layout(title=f"Decline Curve Analysis (Annual Decline Rate: {decline_rate:.1%})",
                                            xaxis_title="Date",
                                            yaxis_title=production_col,
                                            hovermode="x unified")
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Display decline parameters
                            st.write(f"**Exponential Decline Parameters:**")
                            st.write(f"Initial Production (q_i): {np.exp(intercept):.2f}")
                            st.write(f"Decline Rate (D): {decline_rate:.4f} per year ({decline_rate:.1%} per year)")
                            st.write(f"R-squared: {r_value**2:.4f}")
                        else:
                            st.warning("Not enough valid data points for decline curve analysis.")
            else:
                st.warning("Please select at least one well.")
        else:
            # No Well_ID column, treat as single well
            st.subheader("Resampled Production Data")
            resample_freq = st.selectbox("Select Resampling Frequency", ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])
            
            freq_map = {
                "Daily": "D",
                "Weekly": "W",
                "Monthly": "M",
                "Quarterly": "Q",
                "Yearly": "Y"
            }
            
            # Resample data
            resampled_df = df_indexed.resample(freq_map[resample_freq]).sum().reset_index()
            st.dataframe(resampled_df.head())
            
            # Production trend visualization
            st.subheader("Production Trends")
            
            # Select production column to visualize
            production_col = st.selectbox("Select Production Column", production_columns)
            
            # Create production trend plot
            fig = plot_production_trend(resampled_df, production_col)
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and plot moving averages
            st.subheader("Moving Averages")
            
            # Calculate moving averages
            window_size = st.slider("Moving Average Window Size", 2, 12, 3)
            resampled_df[f'{window_size}-Period MA'] = resampled_df[production_col].rolling(window=window_size).mean()
            
            # Plot production with moving average
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=resampled_df['Date'], y=resampled_df[production_col],
                                    mode='lines', name='Production'))
            fig.add_trace(go.Scatter(x=resampled_df['Date'], y=resampled_df[f'{window_size}-Period MA'],
                                    mode='lines', name=f'{window_size}-Period Moving Average'))
            
            fig.update_layout(title=f"{production_col} with {window_size}-Period Moving Average",
                            xaxis_title="Date",
                            yaxis_title=production_col,
                            hovermode="x unified")
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("The data does not have the required columns (Date and production data columns).")
else:
    st.info("Please upload a CSV file or use sample data to begin analysis.")