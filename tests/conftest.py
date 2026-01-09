import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def base_test_data():
    return pd.DataFrame({
        'id': range(1, 11),
        'age': [20, 25, 30, 35, 40, 45, 50, 55, 60, 150],
        'salary': [50000, 52000, 54000, 56000, 58000, 60000, 62000, 64000, 66000, np.nan],
        'department': ['IT', 'IT', 'HR', 'HR', 'Sales', 'Sales', 'IT', 'IT', 'HR', 'IT'],
        'remote': [True, True, False, False, True, False, True, False, True, True]
    })

@pytest.fixture
def quality_config():
    return {
        'outlier_detection': {
            'iqr_multiplier': 1.5,
            'zscore_threshold': 3,
            'isolation_contamination': 0.1
        },
        'constraints': {
            'age': {'min': 18, 'max': 100},
            'salary': {'min': 0}
        }
    }