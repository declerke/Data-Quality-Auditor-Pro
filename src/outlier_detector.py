import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats

class OutlierDetector:
    def __init__(self, df: pd.DataFrame, iqr_multiplier=1.5, zscore_threshold=3, isolation_contamination=0.1):
        self.df = df
        self.iqr_multiplier = iqr_multiplier
        self.zscore_threshold = zscore_threshold
        self.isolation_contamination = isolation_contamination
        self.results = {
            'summary': {
                'per_column_summary': {},
                'total_ml_outliers': 0
            }
        }

    def detect_all(self) -> dict:
        numeric_df = self.df.select_dtypes(include=[np.number]).dropna(axis=1, how='all')
        
        if numeric_df.empty:
            self.results = {
                'error': 'No numeric data available for outlier detection', 
                'summary': {'per_column_summary': {}, 'total_ml_outliers': 0}
            }
            return self.results

        per_column = {}
        for col in numeric_df.columns:
            series = self.df[col].dropna()
            
            if series.nunique() <= 1:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            iqr_outliers = series[(series < (q1 - self.iqr_multiplier * iqr)) | (series > (q3 + self.iqr_multiplier * iqr))].shape[0]
            
            z_scores = np.abs(stats.zscore(series))
            zscore_outliers = (z_scores > self.zscore_threshold).sum()
            
            per_column[col] = {
                'iqr_outliers': int(iqr_outliers),
                'zscore_outliers': int(zscore_outliers),
                'isolation_outliers': 0,
                'severity': 'high' if iqr_outliers > (0.05 * len(self.df)) else 'medium' if iqr_outliers > 0 else 'low'
            }

        valid_numeric_data = numeric_df.loc[:, numeric_df.nunique() > 1].fillna(numeric_df.median())
        
        total_iso_outliers = 0
        if not valid_numeric_data.empty:
            try:
                iso = IsolationForest(contamination=self.isolation_contamination, random_state=42)
                preds = iso.fit_predict(valid_numeric_data)
                total_iso_outliers = (preds == -1).sum()
            except Exception:
                pass

        self.results = {
            'summary': {
                'per_column_summary': per_column,
                'total_ml_outliers': int(total_iso_outliers)
            }
        }
        return self.results

    def print_report(self):
        print("\n" + "="*70)
        print("OUTLIER DETECTION REPORT")
        print("="*70)

        if 'error' in self.results:
            print(f"   • {self.results['error']}")
            return
            
        summary = self.results.get('summary', {'per_column_summary': {}, 'total_ml_outliers': 0})
        per_col = summary.get('per_column_summary', {})
        
        if not per_col and summary.get('total_ml_outliers') == 0:
            print("   • No outliers detected or no suitable numeric data found.")
            return

        print(f"   • Columns analyzed: {len(per_col)}")
        print(f"   • Potential ML-detected outliers: {summary.get('total_ml_outliers', 0)}")
