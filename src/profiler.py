import pandas as pd
import numpy as np

class DatasetProfiler:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.profile = {}

    def generate_profile(self) -> dict:
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        boolean_cols = self.df.select_dtypes(include=['bool']).columns.tolist()
        
        constant_columns = [col for col in self.df.columns if self.df[col].nunique() <= 1]

        self.profile = {
            'metadata': {
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns),
                'duplicate_rows': self.df.duplicated().sum(),
                'memory_usage': self.df.memory_usage(deep=True).sum() / (1024 * 1024),
                'constant_columns': constant_columns
            },
            'data_types': {
                'numeric': numeric_cols,
                'categorical': categorical_cols,
                'datetime': datetime_cols,
                'boolean': boolean_cols
            },
            'columns': {}
        }

        for col in self.df.columns:
            col_data = self.df[col]
            stats = {
                'dtype': str(col_data.dtype),
                'missing_count': int(col_data.isna().sum()),
                'missing_percentage': (col_data.isna().sum() / len(self.df)) * 100,
                'unique_count': col_data.nunique(),
                'is_constant': col in constant_columns
            }
            
            if col in numeric_cols:
                stats.update({
                    'mean': float(col_data.mean()) if not col_data.empty else None,
                    'std': float(col_data.std()) if not col_data.empty else None,
                    'min': float(col_data.min()) if not col_data.empty else None,
                    'max': float(col_data.max()) if not col_data.empty else None,
                    'median': float(col_data.median()) if not col_data.empty else None
                })
            
            self.profile['columns'][col] = stats
            
        return self.profile

    def print_summary(self):
        meta = self.profile['metadata']
        print(f"   • Records: {meta['total_rows']:,}")
        print(f"   • Columns: {meta['total_columns']}")
        print(f"   • Duplicates: {meta['duplicate_rows']}")
        print(f"   • Constant Columns: {len(meta['constant_columns'])}")
        if meta['constant_columns']:
            print(f"     └─ {', '.join(meta['constant_columns'][:5])}{'...' if len(meta['constant_columns']) > 5 else ''}")