import pandas as pd

class MissingValueAnalyzer:
    def __init__(self, df: pd.DataFrame, warning_threshold=0.05, critical_threshold=0.30):
        self.df = df
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.results = {}

    def analyze(self) -> dict:
        total_rows = len(self.df)
        col_analysis = []
        
        for col in self.df.columns:
            missing_count = int(self.df[col].isna().sum())
            missing_pct = missing_count / total_rows if total_rows > 0 else 0
            
            severity = 'none'
            if missing_pct > self.critical_threshold:
                severity = 'error'
            elif missing_pct > self.warning_threshold:
                severity = 'warning'
            elif missing_pct > 0:
                severity = 'info'
                
            strategies = []
            if severity != 'none':
                if self.df[col].dtype in ['int64', 'float64']:
                    strategies = ["Impute with mean/median", "Fill with constant (0)"]
                else:
                    strategies = ["Impute with mode", "Fill with 'Unknown'"]
                strategies.append("Drop rows if target variable")

            col_analysis.append({
                'column': col,
                'missing_count': missing_count,
                'missing_percentage': missing_pct * 100,
                'severity': severity,
                'dtype': str(self.df[col].dtype),
                'strategies': strategies
            })

        complete_rows = self.df.dropna().shape[0]
        
        self.results = {
            'overall_stats': {
                'missing_percentage': (self.df.isna().sum().sum() / self.df.size) * 100 if self.df.size > 0 else 0,
                'complete_rows_percentage': (complete_rows / total_rows) * 100 if total_rows > 0 else 0
            },
            'column_analysis': col_analysis,
            'recommendations': [c for c in col_analysis if c['missing_percentage'] > 0]
        }
        return self.results

    def print_report(self):
        stats = self.results['overall_stats']
        print(f"   • Overall Completeness: {stats['complete_rows_percentage']:.1f}%")
        missing_cols = [c for c in self.results['column_analysis'] if c['missing_count'] > 0]
        print(f"   • Columns with missing data: {len(missing_cols)}")
