import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# Import utility functions
from utils.data_loader import load_las_file, load_production_data, load_drilling_data, get_sample_data_path
from utils.visualization import create_kpi_card
from utils.session_state import initialize_session_state
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
    page_title="Oil & Gas Data Dashboard",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()

# Main title
#st.title(" ")

# Introduction
st.markdown("""
Welcome to the Oil & Gas Data Dashboard. This application provides comprehensive analysis tools for well log data, 
production data, and drilling KPIs. Use the navigation menu on the left to explore different analyses.
""")

# Load sample data if not already loaded
if st.session_state.well_log_data is None:
    well_log_path = get_sample_data_path('well_log')
    if os.path.exists(well_log_path):
        _, well_log_df = load_las_file(well_log_path)
        st.session_state.well_log_data = well_log_df

if st.session_state.production_data is None:
    production_path = get_sample_data_path('production')
    if os.path.exists(production_path):
        production_df = load_production_data(production_path)
        st.session_state.production_data = production_df

if st.session_state.drilling_data is None:
    drilling_path = get_sample_data_path('drilling')
    if os.path.exists(drilling_path):
        drilling_df = load_drilling_data(drilling_path)
        st.session_state.drilling_data = drilling_df

# Dashboard overview
st.header("Dashboard Overview")

# Create KPI cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.session_state.well_log_data is not None:
        depth_range = st.session_state.well_log_data['DEPTH'].max() - st.session_state.well_log_data['DEPTH'].min()
        create_kpi_card("Well Depth Range", f"{depth_range:.1f}", unit="m")
    else:
        create_kpi_card("Well Depth Range", "N/A", unit="m")

with col2:
    if st.session_state.production_data is not None:
        total_production = st.session_state.production_data['Oil_Production_bbl'].sum()
        create_kpi_card("Total Oil Production", f"{total_production:.1f}", unit="bbl")
    else:
        create_kpi_card("Total Oil Production", "N/A", unit="bbl")

with col3:
    if st.session_state.drilling_data is not None:
        avg_rop = st.session_state.drilling_data['ROP'].mean()
        create_kpi_card("Average ROP", f"{avg_rop:.1f}", unit="m/hr")
    else:
        create_kpi_card("Average ROP", "N/A", unit="m/hr")

with col4:
    if st.session_state.production_data is not None and 'Well_ID' in st.session_state.production_data.columns:
        well_count = st.session_state.production_data['Well_ID'].nunique()
        create_kpi_card("Well Count", well_count)
    else:
        create_kpi_card("Well Count", "N/A")

# Summary visualizations
st.header("Summary Visualizations")

# Create tabs for different summary visualizations
tab1, tab2, tab3 = st.tabs(["Well Log Summary", "Production Summary", "Drilling Summary"])

with tab1:
    if st.session_state.well_log_data is not None:
        st.subheader("Well Log Curve Statistics")
        st.dataframe(st.session_state.well_log_data.describe())
        
        # Create a histogram of GR values if available
        if 'GR' in st.session_state.well_log_data.columns:
            st.subheader("Gamma Ray Distribution")
            fig = px.histogram(st.session_state.well_log_data, x='GR', nbins=30,
                              title="Gamma Ray Distribution")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No well log data available. Please upload data on the Well Log Analysis page.")

with tab2:
    if st.session_state.production_data is not None:
        st.subheader("Production Data Summary")
        
        # Create a time series of total production
        if 'Date' in st.session_state.production_data.columns and 'Oil_Production_bbl' in st.session_state.production_data.columns:
            # Group by date if there are multiple wells
            if 'Well_ID' in st.session_state.production_data.columns:
                daily_production = st.session_state.production_data.groupby('Date')['Oil_Production_bbl'].sum().reset_index()
            else:
                daily_production = st.session_state.production_data[['Date', 'Oil_Production_bbl']]
            
            # Resample to monthly
            daily_production = daily_production.set_index('Date')
            monthly_production = daily_production.resample('M').sum().reset_index()
            
            st.subheader("Monthly Oil Production")
            fig = px.line(monthly_production, x='Date', y='Oil_Production_bbl',
                         title="Monthly Oil Production")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No production data available. Please upload data on the Production Analysis page.")

with tab3:
    if st.session_state.drilling_data is not None:
        st.subheader("Drilling Data Summary")
        
        # Create a scatter plot of ROP vs Depth
        if 'Depth' in st.session_state.drilling_data.columns and 'ROP' in st.session_state.drilling_data.columns:
            st.subheader("Rate of Penetration vs Depth")
            fig = px.scatter(st.session_state.drilling_data, x='ROP', y='Depth',
                            title="ROP vs Depth")
            fig.update_yaxes(autorange="reversed")  # Depth increases downward
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No drilling data available. Please upload data on the Drilling KPI page.")

# Quick navigation section
st.header("Quick Navigation")
st.markdown("""
Use these links to quickly navigate to specific analysis pages:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/1_Well_Log_Analysis.py", label="Well Log Analysis", icon="📊")

with col2:
    st.page_link("pages/2_Production_Analysis.py", label="Production Analysis", icon="📈")

with col3:
    st.page_link("pages/3_Drilling_KPIs.py", label="Drilling KPIs", icon="🔍")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>© 2025 Oil & Gas Data Dashboard | Created with Streamlit</p>
</div>
""", unsafe_allow_html=True)