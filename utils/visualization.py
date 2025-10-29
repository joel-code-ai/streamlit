import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def plot_well_log(df, curve, depth_range=None):
    """Create a well log plot for a specific curve."""
    if depth_range:
        df = df[(df['DEPTH'] >= depth_range[0]) & (df['DEPTH'] <= depth_range[1])]
    
    fig = px.line(df, x=curve, y="DEPTH")
    fig.update_yaxes(autorange="reversed")  # Depth increases downward
    return fig

def plot_multi_well_log(df, curves, depth_range=None):
    """Create a multi-track well log plot."""
    if depth_range:
        df = df[(df['DEPTH'] >= depth_range[0]) & (df['DEPTH'] <= depth_range[1])]
    
    fig = make_subplots(rows=1, cols=len(curves), shared_yaxes=True,
                        subplot_titles=curves)
    
    for i, curve in enumerate(curves):
        fig.add_trace(go.Scatter(x=df[curve], y=df['DEPTH'], name=curve), row=1, col=i+1)
    
    fig.update_yaxes(autorange="reversed")  # Depth increases downward
    return fig

def plot_production_trend(df, y_column, color_column=None):
    """Create a production trend plot."""
    if color_column:
        fig = px.line(df, x='Date', y=y_column, color=color_column)
    else:
        fig = px.line(df, x='Date', y=y_column)
    
    fig.update_layout(hovermode='x unified')
    return fig

def plot_drilling_kpi(df, parameter, depth_based=True):
    """Create a drilling KPI plot."""
    if depth_based:
        fig = px.line(df, x=parameter, y='Depth')
        fig.update_yaxes(autorange="reversed")  # Depth increases downward
    else:
        fig = px.line(df, x='Timestamp', y=parameter)
    
    return fig

def create_kpi_card(title, value, delta=None, unit=""):
    """Create a KPI card with a title, value, and optional delta."""
    if delta is not None:
        st.metric(title, f"{value} {unit}", f"{delta} {unit}")
    else:
        st.metric(title, f"{value} {unit}")