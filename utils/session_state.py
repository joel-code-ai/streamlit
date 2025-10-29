import streamlit as st

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'well_log_data' not in st.session_state:
        st.session_state.well_log_data = None
    
    if 'production_data' not in st.session_state:
        st.session_state.production_data = None
    
    if 'drilling_data' not in st.session_state:
        st.session_state.drilling_data = None
    
    if 'selected_well' not in st.session_state:
        st.session_state.selected_well = None
    
    if 'depth_range' not in st.session_state:
        st.session_state.depth_range = None

def set_well_log_data(df):
    """Set well log data in session state."""
    st.session_state.well_log_data = df

def set_production_data(df):
    """Set production data in session state."""
    st.session_state.production_data = df

def set_drilling_data(df):
    """Set drilling data in session state."""
    st.session_state.drilling_data = df

def set_selected_well(well_name):
    """Set selected well in session state."""
    st.session_state.selected_well = well_name

def set_depth_range(depth_range):
    """Set depth range in session state."""
    st.session_state.depth_range = depth_range