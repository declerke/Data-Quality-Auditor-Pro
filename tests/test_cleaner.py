import pytest
import pandas as pd
import numpy as np
from src.cleaner import DataCleaner

def test_drop_constant_columns(base_test_data):
    df = base_test_data.copy()
    df['constant'] = 'SameValue'
    cleaner = DataCleaner(df)
    
    cleaned_df = cleaner.drop_constant_columns(['constant'])
    
    assert 'constant' not in cleaned_df.columns
    assert "Dropped constant columns" in cleaner.history[0]

def test_handle_missing_values(base_test_data):
    cleaner = DataCleaner(base_test_data)
    
    missing_analysis = [
        {'column': 'salary', 'severity': 'warning', 'dtype': 'float64'}
    ]
    
    cleaned_df = cleaner.handle_missing_values(missing_analysis)
    
    assert cleaned_df['salary'].isna().sum() == 0
    assert "Imputed missing salary" in cleaner.history[0]

def test_handle_outliers_clipping(base_test_data):
    cleaner = DataCleaner(base_test_data)
    
    outlier_summary = {
        'age': {'iqr_outliers': 1}
    }
    
    cleaned_df = cleaner.handle_outliers(outlier_summary, method='clip')
    
    assert cleaned_df['age'].max() < 150
    assert "Clipped outliers in age" in cleaner.history[0]

def test_enforce_types():
    df = pd.DataFrame({'age': ['25', '30', 'not_a_number']})
    cleaner = DataCleaner(df)
    expected = {'numeric_columns': ['age']}
    
    cleaned_df = cleaner.enforce_types(expected)
    
    assert pd.api.types.is_numeric_dtype(cleaned_df['age'])
    assert cleaned_df['age'].isna().sum() == 1  # 'not_a_number' becomes NaN
