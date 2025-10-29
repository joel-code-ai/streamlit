import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Import utility functions
from utils.data_loader import load_drilling_data, get_sample_data_path
from utils.visualization import plot_drilling_kpi
from utils.session_state import initialize_session_state, set_drilling_data
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
    page_title="Drilling KPIs",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
initialize_session_state()

# Main title
st.title("Drilling KPI Visualization")

# Sidebar for data loading and controls
st.sidebar.header("Data Loading")

# Option to use sample data or upload own data
data_source = st.sidebar.radio("Select Data Source", ["Use Sample Data", "Upload CSV File"])

if data_source == "Use Sample Data":
    sample_path = get_sample_data_path('drilling')
    if sample_path and os.path.exists(sample_path):
        df = load_drilling_data(sample_path)
        if df is not None:
            set_drilling_data(df)
            st.sidebar.success("Sample data loaded successfully!")
    else:
        st.sidebar.error("Sample data not found. Please upload your own data.")
        data_source = "Upload CSV File"

if data_source == "Upload CSV File":
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = load_drilling_data(uploaded_file)
        if df is not None:
            set_drilling_data(df)
            st.sidebar.success("File uploaded successfully!")

# Check if data is loaded
if st.session_state.drilling_data is not None:
    df = st.session_state.drilling_data
    
    # Display the DataFrame
    st.subheader("Drilling Data")
    st.dataframe(df.head())
    
    # Check if required columns exist
    required_columns = ['Depth']
    kpi_columns = [col for col in df.columns if col not in ['Depth', 'Timestamp', 'Formation', 'Formation_Hardness']]
    
    if all(col in df.columns for col in required_columns) and kpi_columns:
        # Sidebar for depth range selection
        st.sidebar.header("Depth Range")
        min_depth = float(df['Depth'].min())
        max_depth = float(df['Depth'].max())
        depth_range = st.sidebar.slider("Depth Range (m)", min_depth, max_depth, (min_depth, max_depth))
        
        # Filter data by depth range
        filtered_df = df[(df['Depth'] >= depth_range[0]) & (df['Depth'] <= depth_range[1])]
        
        # Check if Formation column exists
        if 'Formation' in df.columns:
            # Sidebar for formation selection
            st.sidebar.header("Formation Selection")
            available_formations = df['Formation'].unique().tolist()
            selected_formations = st.sidebar.multiselect("Select Formations", available_formations, default=available_formations)
            
            if selected_formations:
                # Further filter by formation
                filtered_df = filtered_df[filtered_df['Formation'].isin(selected_formations)]
        
        # Visualization options
        st.sidebar.header("Visualization Options")
        plot_type = st.sidebar.selectbox("Select Plot Type", ["Depth-Based", "Time-Based", "Crossplot", "KPI Summary"])
        
        if plot_type == "Depth-Based":
            st.subheader("Depth-Based Drilling Parameters")
            
            # Select parameters to display
            params = st.multiselect("Select Parameters", kpi_columns, default=kpi_columns[:3])
            
            if params:
                # Create a depth-based multi-parameter plot
                fig = make_subplots(rows=1, cols=len(params), shared_yaxes=True,
                                    subplot_titles=params,
                                    horizontal_spacing=0.02)
                
                # Colors for different parameters
                colors = ['green', 'blue', 'red', 'purple', 'orange', 'brown', 'pink', 'gray']
                
                # Add traces for each parameter
                for i, param in enumerate(params):
                    fig.add_trace(go.Scatter(
                        x=filtered_df[param], 
                        y=filtered_df["Depth"],
                        mode="lines", 
                        name=param, 
                        line=dict(color=colors[i % len(colors)])
                    ), row=1, col=i+1)
                
                # Reverse y-axis (depth increases downward)
                fig.update_yaxes(autorange="reversed")
                
                st.plotly_chart(fig, use_container_width=True)
        
        elif plot_type == "Time-Based":
            if 'Timestamp' in df.columns:
                st.subheader("Time-Based Drilling Parameters")
                
                # Select parameters to display
                params = st.multiselect("Select Parameters", ['Depth'] + kpi_columns, default=['Depth', kpi_columns[0]])
                
                if params:
                    fig = go.Figure()
                    
                    # Colors for different parameters
                    colors = ['black', 'green', 'blue', 'red', 'purple', 'orange', 'brown', 'pink', 'gray']
                    
                    # Add traces for each parameter
                    for i, param in enumerate(params):
                        fig.add_trace(go.Scatter(
                            x=filtered_df["Timestamp"], 
                            y=filtered_df[param],
                            mode="lines", 
                            name=param, 
                            line=dict(color=colors[i % len(colors)])
                        ))
                    
                    fig.update_layout(title="Time-Based Drilling Parameters",
                                    xaxis_title="Time",
                                    yaxis_title="Parameter Value",
                                    hovermode="x unified")
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Time-based visualization requires a 'Timestamp' column in the data.")
        
        elif plot_type == "Crossplot":
            st.subheader("Parameter Crossplot")
            
            col1, col2 = st.columns(2)
            
            with col1:
                x_param = st.selectbox("X-Axis Parameter", kpi_columns, index=0)
            
            with col2:
                y_param = st.selectbox("Y-Axis Parameter", kpi_columns, index=min(1, len(kpi_columns)-1))
            
            color_by = st.selectbox("Color By", ["Depth", "None"] + (["Formation"] if "Formation" in df.columns else []), index=0)
            
            if color_by == "None":
                fig = px.scatter(filtered_df, x=x_param, y=y_param,
                                title=f"{y_param} vs {x_param} Relationship")
            else:
                fig = px.scatter(filtered_df, x=x_param, y=y_param, color=color_by,
                                title=f"{y_param} vs {x_param} Relationship",
                                color_continuous_scale="Viridis" if color_by == "Depth" else None)
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif plot_type == "KPI Summary":
            st.subheader("Drilling KPI Summary")
            
            # Calculate summary statistics
            summary_stats = filtered_df[kpi_columns].describe().T[['mean', 'std', 'min', 'max']]
            st.dataframe(summary_stats)
            
            # If Formation column exists, calculate KPIs by formation
            if 'Formation' in filtered_df.columns:
                st.subheader("KPIs by Formation")
                
                # Select KPI to display
                kpi = st.selectbox("Select KPI", kpi_columns, index=0)
                
                # Calculate average KPIs by formation
                formation_kpis = filtered_df.groupby('Formation')[kpi].mean().reset_index()
                
                # Create bar chart
                fig = px.bar(formation_kpis, x="Formation", y=kpi,
                            title=f"Average {kpi} by Formation",
                            color="Formation")
                
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("The data does not have the required columns (Depth and KPI columns).")
else:
    st.info("Please upload a CSV file or use sample data to begin analysis.")