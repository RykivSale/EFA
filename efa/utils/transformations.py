import pandas as pd
import numpy as np

def filter_dataframe(df, filters):
    """Apply filters to a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        filters (list): List of filter dictionaries with format:
            {
                'column': str,
                'operation': str,
                'value': Any
            }
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    result = df.copy()
    for f in filters:
        col = f['column']
        op = f['operation']
        val = f['value']
        
        if op == 'equals':
            result = result[result[col] == val]
        elif op == 'not_equals':
            result = result[result[col] != val]
        elif op == 'contains':
            result = result[result[col].astype(str).str.contains(str(val), case=False)]
        elif op == 'greater_than':
            result = result[result[col] > val]
        elif op == 'less_than':
            result = result[result[col] < val]
        elif op == 'between':
            result = result[(result[col] >= val[0]) & (result[col] <= val[1])]
            
    return result

def aggregate_dataframe(df, group_cols, agg_cols, agg_funcs):
    """Aggregate a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        group_cols (list): Columns to group by
        agg_cols (list): Columns to aggregate
        agg_funcs (list): Aggregation functions to apply
        
    Returns:
        pd.DataFrame: Aggregated DataFrame
    """
    agg_dict = {col: agg_funcs for col in agg_cols}
    return df.groupby(group_cols).agg(agg_dict)

def join_dataframes(left_df, right_df, join_type, left_on, right_on):
    """Join two DataFrames.
    
    Args:
        left_df (pd.DataFrame): Left DataFrame
        right_df (pd.DataFrame): Right DataFrame
        join_type (str): Type of join ('inner', 'left', 'right', 'outer')
        left_on (str or list): Column(s) to join on from left DataFrame
        right_on (str or list): Column(s) to join on from right DataFrame
        
    Returns:
        pd.DataFrame: Joined DataFrame
    """
    return pd.merge(
        left_df,
        right_df,
        how=join_type,
        left_on=left_on,
        right_on=right_on
    )
