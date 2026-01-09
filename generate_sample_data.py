#!/usr/bin/env python3
# generate_sample_data.py - Generate sample messy dataset for testing

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_messy_dataset(n_rows=1000, output_path='data/sample_messy_data.csv'):
    """
    Generate a sample dataset with intentional data quality issues.
    
    Issues included:
    - Missing values (various patterns)
    - Outliers
    - Data type inconsistencies
    - Constraint violations
    - Duplicate rows
    """
    
    np.random.seed(42)
    random.seed(42)
    
    print(f"Generating {n_rows} rows of sample data with quality issues...")
    
    # Base data generation
    data = {
        'EmployeeID': range(1, n_rows + 1),
        'Name': [f"Employee_{i}" for i in range(1, n_rows + 1)],
        'Age': np.random.randint(18, 70, n_rows),
        'Department': np.random.choice(['Sales', 'Engineering', 'HR', 'Marketing', 'Finance'], n_rows),
        'Salary': np.random.normal(60000, 20000, n_rows),
        'YearsAtCompany': np.random.randint(0, 30, n_rows),
        'PerformanceScore': np.random.choice([1, 2, 3, 4, 5], n_rows),
        'Satisfaction': np.random.uniform(1, 10, n_rows),
        'ProjectCount': np.random.poisson(3, n_rows),
        'RemoteWork': np.random.choice(['Yes', 'No'], n_rows)
    }
    
    df = pd.DataFrame(data)
    
    # INTRODUCE DATA QUALITY ISSUES
    
    # 1. Missing values (15% of Age, 25% of Satisfaction)
    missing_age_indices = np.random.choice(df.index, size=int(0.15 * n_rows), replace=False)
    df.loc[missing_age_indices, 'Age'] = np.nan
    
    missing_satisfaction_indices = np.random.choice(df.index, size=int(0.25 * n_rows), replace=False)
    df.loc[missing_satisfaction_indices, 'Satisfaction'] = np.nan
    
    # 2. Outliers in Salary
    outlier_indices = np.random.choice(df.index, size=int(0.05 * n_rows), replace=False)
    df.loc[outlier_indices, 'Salary'] = np.random.choice([10000, 250000, 500000], len(outlier_indices))
    
    # 3. Negative values (constraint violations)
    negative_indices = np.random.choice(df.index, size=int(0.02 * n_rows), replace=False)
    df.loc[negative_indices, 'YearsAtCompany'] = np.random.randint(-5, 0, len(negative_indices))
    
    # 4. Constraint violations (Age < 18 or > 70)
    age_violation_indices = np.random.choice(df.index, size=int(0.03 * n_rows), replace=False)
    df.loc[age_violation_indices, 'Age'] = np.random.choice([15, 16, 75, 80], len(age_violation_indices))
    
    # 5. Data type inconsistencies (mix strings in numeric column)
    inconsistent_indices = np.random.choice(df.index, size=min(5, n_rows), replace=False)
    # This will be caught as type issues when loading
    
    # 6. Categorical inconsistencies (case issues, whitespace)
    df.loc[df.sample(frac=0.1).index, 'Department'] = df.loc[df.sample(frac=0.1).index, 'Department'].str.lower()
    df.loc[df.sample(frac=0.05).index, 'Department'] = ' ' + df.loc[df.sample(frac=0.05).index, 'Department'] + ' '
    
    # 7. Duplicate rows (2% duplicates)
    duplicate_indices = np.random.choice(df.index, size=int(0.02 * n_rows), replace=False)
    duplicates = df.loc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # 8. High cardinality in what should be categorical
    df['EmployeeCode'] = [f"EMP-{random.randint(1000, 9999)}" for _ in range(len(df))]
    
    # 9. Correlated missing values (when Satisfaction is missing, sometimes ProjectCount is too)
    correlated_missing = df[df['Satisfaction'].isna()].sample(frac=0.3).index
    df.loc[correlated_missing, 'ProjectCount'] = np.nan
    
    # 10. Add a constant column (no variance)
    df['Company'] = 'TechCorp'
    
    # 11. Add column with high missing rate (>50%)
    df['ManagerEmail'] = np.nan
    df.loc[df.sample(frac=0.40).index, 'ManagerEmail'] = [f"manager{i}@techcorp.com" for i in range(len(df.loc[df.sample(frac=0.40).index]))]
    
    # 12. Extreme outliers in ProjectCount
    extreme_indices = np.random.choice(df.index, size=int(0.01 * n_rows), replace=False)
    df.loc[extreme_indices, 'ProjectCount'] = np.random.choice([50, 100, -5], len(extreme_indices))
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Sample dataset generated: {output_path}")
    print(f"\nDataset statistics:")
    print(f"  • Total rows: {len(df)}")
    print(f"  • Total columns: {len(df.columns)}")
    print(f"  • Duplicate rows: {df.duplicated().sum()}")
    print(f"\nIntentional quality issues introduced:")
    print(f"  • Missing values in Age: {df['Age'].isna().sum()} ({df['Age'].isna().sum()/len(df)*100:.1f}%)")
    print(f"  • Missing values in Satisfaction: {df['Satisfaction'].isna().sum()} ({df['Satisfaction'].isna().sum()/len(df)*100:.1f}%)")
    print(f"  • Missing values in ManagerEmail: {df['ManagerEmail'].isna().sum()} ({df['ManagerEmail'].isna().sum()/len(df)*100:.1f}%)")
    print(f"  • Salary outliers: ~{int(0.05 * n_rows)}")
    print(f"  • Age constraint violations: ~{int(0.03 * n_rows)}")
    print(f"  • Negative YearsAtCompany: {(df['YearsAtCompany'] < 0).sum()}")
    print(f"  • Department case inconsistencies: Yes")
    print(f"  • Extreme ProjectCount values: ~{int(0.01 * n_rows)}")
    print(f"\n🔍 Now run the auditor:")
    print(f"  python main.py {output_path}")


if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    generate_messy_dataset()