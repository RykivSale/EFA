# DataPlayground

DataPlayground is a low-code interface for transforming tabular data in CSV and Parquet formats. It provides an intuitive web interface for data analysis and transformation without writing code.

## Features

- Upload CSV and Parquet files
- Interactive data preview and information
- Data filtering and sorting
- Column selection
- Grouping and aggregations
- Export results in CSV or Parquet format

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Upload your CSV or Parquet file using the sidebar
2. Select operations from the available tabs:
   - Preview & Info: View basic dataset information and preview data
   - Filter & Sort: Filter rows and sort data
   - Group & Aggregate: Perform grouping and aggregation operations
   - Export: Download transformed data

## Limitations

- Maximum file size: 100MB
- Supported formats: CSV and Parquet
- Response time: <1s for datasets up to 100k rows
