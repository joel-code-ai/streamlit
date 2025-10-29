import streamlit as st
import pandas as pd
import lasio
from io import StringIO
import os

# Cache the data loading functions to improve performance
@st.cache_data
def load_las_file(file_path):
    """Load a LAS file and return both the LAS object and a DataFrame."""
    try:
        if isinstance(file_path, str):
            # Load from file path
            las = lasio.read(file_path)
        else:
            # Load from uploaded file
            stringio = StringIO(file_path.getvalue().decode("utf-8"))
            las = lasio.read(stringio)
        
        # Convert to DataFrame
        df = las.df()
        df = df.reset_index()
        df = df.rename(columns={'index': 'DEPTH'})
        
        return las, df
    except Exception as e:
        st.error(f"Error loading LAS file: {e}")
        return None, None

@st.cache_data
def load_production_data(file_path):
    """Load production data from a CSV file."""
    try:
        if isinstance(file_path, str):
            # Load from file path
            df = pd.read_csv(file_path)
        else:
            # Load from uploaded file
            df = pd.read_csv(file_path)
        
        # Convert date column to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        
        return df
    except Exception as e:
        st.error(f"Error loading production data: {e}")
        return None

@st.cache_data
def load_drilling_data(file_path):
    """Load drilling data from a CSV file."""
    try:
        if isinstance(file_path, str):
            # Load from file path
            df = pd.read_csv(file_path)
        else:
            # Load from uploaded file
            df = pd.read_csv(file_path)
        
        # Convert timestamp column to datetime
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
        
        return df
    except Exception as e:
        st.error(f"Error loading drilling data: {e}")
        return None

def get_sample_data_path(data_type):
    """Get the path to sample data files."""
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    if data_type == 'well_log':
        return os.path.join(base_dir, 'synthetic_well.las')
    elif data_type == 'production':
        return os.path.join(base_dir, 'production_data.csv')
    elif data_type == 'drilling':
        return os.path.join(base_dir, 'drilling_data.csv')
    else:
        return None