import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import StringIO
import os

# Import utility functions
from utils.data_loader import load_las_file, get_sample_data_path
from utils.visualization import plot_well_log, plot_multi_well_log
from utils.session_state import initialize_session_state, set_well_log_data
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
    page_title="Well Log Analysis",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
initialize_session_state()

# Main title
st.title("Well Log Analysis")

# Sidebar for data loading and controls
st.sidebar.header("Data Loading")

# Option to use sample data or upload own data
data_source = st.sidebar.radio("Select Data Source", ["Use Sample Data", "Upload LAS File"])

if data_source == "Use Sample Data":
    sample_path = get_sample_data_path('well_log')
    if sample_path and os.path.exists(sample_path):
        las, df = load_las_file(sample_path)
        if df is not None:
            set_well_log_data(df)
            st.sidebar.success("Sample data loaded successfully!")
    else:
        st.sidebar.error("Sample data not found. Please upload your own data.")
        data_source = "Upload LAS File"

if data_source == "Upload LAS File":
    uploaded_file = st.sidebar.file_uploader("Choose a LAS file", type="las")
    if uploaded_file is not None:
        las, df = load_las_file(uploaded_file)
        if df is not None:
            set_well_log_data(df)
            st.sidebar.success("File uploaded successfully!")

# Check if data is loaded
if st.session_state.well_log_data is not None:
    df = st.session_state.well_log_data
    
    # Display well header information if available
    if 'las' in locals() and las is not None:
        st.subheader("Well Header Information")
        well_info = {}
        for item in las.well:
            well_info[item.mnemonic] = f"{item.value} {item.unit}"
        st.json(well_info)
    
    # Display the DataFrame
    st.subheader("Well Log Data")
    st.dataframe(df.head())
    
    # Display descriptive statistics
    st.subheader("Descriptive Statistics")
    st.dataframe(df.describe())
    
    # Sidebar for plot controls
    st.sidebar.header("Plotting Options")
    
    # Select curves to plot
    available_curves = list(df.columns)
    available_curves.remove('DEPTH')  # Remove depth as it's the y-axis
    
    # Single curve plot
    st.subheader("Single Curve Plot")
    selected_curve = st.selectbox("Select a curve to plot", available_curves)
    
    # Depth range slider
    min_depth = float(df['DEPTH'].min())
    max_depth = float(df['DEPTH'].max())
    depth_range = st.slider("Depth Range", min_depth, max_depth, (min_depth, max_depth))
    
    # Create plot
    fig = plot_well_log(df, selected_curve, depth_range)
    st.plotly_chart(fig, use_container_width=True)
    
    # Multi-curve plot
    st.subheader("Multi-Curve Plot")
    selected_curves = st.multiselect("Select curves", available_curves, default=[available_curves[0]])
    
    if selected_curves:
        fig = plot_multi_well_log(df, selected_curves, depth_range)
        st.plotly_chart(fig, use_container_width=True)
    
    # Crossplot
    st.subheader("Crossplot")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        x_curve = st.selectbox("X-axis", available_curves, index=0)
    
    with col2:
        y_curve = st.selectbox("Y-axis", available_curves, index=min(1, len(available_curves)-1))
    
    with col3:
        color_by = st.selectbox("Color by", ["None"] + available_curves)
    
    # Filter data by depth range
    filtered_df = df[(df['DEPTH'] >= depth_range[0]) & (df['DEPTH'] <= depth_range[1])]
    
    if color_by == "None":
        fig = px.scatter(filtered_df, x=x_curve, y=y_curve, title=f"{y_curve} vs {x_curve}")
    else:
        fig = px.scatter(filtered_df, x=x_curve, y=y_curve, color=filtered_df[color_by],
                        title=f"{y_curve} vs {x_curve} (colored by {color_by})")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation matrix
    st.subheader("Correlation Matrix")
    correlation_matrix = filtered_df.drop('DEPTH', axis=1).corr()
    fig = px.imshow(correlation_matrix, text_auto=True, color_continuous_scale='RdBu_r',
                   title="Well Log Correlation Matrix")
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("Please upload a LAS file or use sample data to begin analysis.")