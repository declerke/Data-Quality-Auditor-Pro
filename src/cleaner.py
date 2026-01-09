import pandas as pd
import numpy as np

class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.history = []

    def enforce_types(self, expected_types: dict):
        if not expected_types:
            return self.df
            
        for col in expected_types.get('numeric_columns', []):
            if col in self.df.columns:
                initial_dtype = self.df[col].dtype
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                if initial_dtype != self.df[col].dtype:
                    self.history.append(f"Enforced numeric type for {col}")
                
        for col in expected_types.get('categorical_columns', []):
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).replace('nan', np.nan)
                self.history.append(f"Enforced categorical type for {col}")
                
        return self.df

    def drop_constant_columns(self, constant_cols: list):
        if not constant_cols:
            return self.df
        self.df.drop(columns=constant_cols, inplace=True)
        self.history.append(f"Dropped constant columns: {', '.join(constant_cols)}")
        return self.df

    def drop_duplicates(self):
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        dropped = initial_rows - len(self.df)
        if dropped > 0:
            self.history.append(f"Dropped {dropped} duplicate rows")
        return self.df

    def handle_missing_values(self, missing_analysis: list):
        for col_info in missing_analysis:
            col = col_info['column']
            if col not in self.df.columns:
                continue
                
            if col_info['severity'] == 'error':
                self.df.dropna(subset=[col], inplace=True)
                self.history.append(f"Dropped rows with missing {col} (High Severity)")
            else:
                if self.df[col].dtype in ['int64', 'float64']:
                    fill_value = self.df[col].median()
                    self.df[col] = self.df[col].fillna(fill_value)
                    self.history.append(f"Imputed missing {col} with median ({fill_value})")
                else:
                    fill_value = self.df[col].mode()[0] if not self.df[col].mode().empty else "Unknown"
                    self.df[col] = self.df[col].fillna(fill_value)
                    self.history.append(f"Imputed missing {col} with mode ({fill_value})")
        return self.df

    def handle_outliers(self, outlier_summary: dict, method='clip'):
        for col, stats in outlier_summary.items():
            if col not in self.df.columns or stats.get('iqr_outliers', 0) == 0:
                continue
                
            q1 = self.df[col].quantile(0.25)
            q3 = self.df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            
            if method == 'clip':
                self.df[col] = self.df[col].clip(lower=lower, upper=upper)
                self.history.append(f"Clipped outliers in {col}")
            elif method == 'remove':
                self.df = self.df[(self.df[col] >= lower) & (self.df[col] <= upper)]
                self.history.append(f"Removed rows with outliers in {col}")
        
        return self.df

    def get_cleaned_data(self) -> pd.DataFrame:
        return self.df

    def print_cleaning_summary(self):
        print("\n======================================================================")
        print("CLEANING SUMMARY")
        print("======================================================================")
        if not self.history:
            print("   • No cleaning actions performed.")
        for action in self.history:
            print(f"   • {action}")