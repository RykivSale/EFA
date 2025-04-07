import pandas as pd
from pathlib import Path
import streamlit as st

def validate_file_size(file, max_size_mb=100):
    """Validate that the file size is within limits."""
    file_size_mb = file.size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        st.error(f"File size ({file_size_mb:.1f}MB) exceeds the limit of {max_size_mb}MB")
        return False
    return True

def load_file(uploaded_file):
    """Load a CSV or Parquet file into a pandas DataFrame."""
    if not validate_file_size(uploaded_file):
        return None
        
    try:
        file_extension = Path(uploaded_file.name).suffix.lower()
        if file_extension == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension == '.parquet':
            df = pd.read_parquet(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Parquet files.")
            return None
            
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def get_column_types(df):
    """Get column types and basic statistics."""
    return {
        'numeric': df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
        'categorical': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'datetime': df.select_dtypes(include=['datetime64']).columns.tolist(),
        'boolean': df.select_dtypes(include=['bool']).columns.tolist()
    }
