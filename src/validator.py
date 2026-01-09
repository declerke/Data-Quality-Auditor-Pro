import pandas as pd
import numpy as np

class DataValidator:
    def __init__(self, df: pd.DataFrame, constraints: dict):
        self.df = df
        self.constraints = constraints
        self.results = {}

    def validate_all(self) -> dict:
        violations = []
        total_violations_count = 0
        
        for col, rules in self.constraints.items():
            if col not in self.df.columns:
                continue
                
            if 'min' in rules:
                invalid = self.df[self.df[col] < rules['min']]
                if not invalid.empty:
                    violations.append({
                        'column': col, 'constraint': 'min_value',
                        'violations': len(invalid), 'percentage': (len(invalid)/len(self.df))*100,
                        'expected': f">= {rules['min']}", 'severity': 'error'
                    })
                    total_violations_count += len(invalid)

            if 'max' in rules:
                invalid = self.df[self.df[col] > rules['max']]
                if not invalid.empty:
                    violations.append({
                        'column': col, 'constraint': 'max_value',
                        'violations': len(invalid), 'percentage': (len(invalid)/len(self.df))*100,
                        'expected': f"<= {rules['max']}", 'severity': 'error'
                    })
                    total_violations_count += len(invalid)

            if 'relationship' in rules:
                try:
                    rel_invalid = self.df.query(f"not ({rules['relationship']})")
                    if not rel_invalid.empty:
                        violations.append({
                            'column': col, 'constraint': 'business_rule',
                            'violations': len(rel_invalid), 'percentage': (len(rel_invalid)/len(self.df))*100,
                            'rule': rules['relationship'], 'severity': 'warning'
                        })
                        total_violations_count += len(rel_invalid)
                except:
                    pass

        score = max(0, 100 - (total_violations_count / (len(self.df) * len(self.df.columns) or 1)) * 1000)
        if self.df.isna().sum().sum() > 0: score -= 5
        
        self.results = {
            'summary': {
                'data_quality_score': float(score),
                'validation_passed': score >= 80,
                'total_issues': len(violations),
                'severity_breakdown': {
                    'error': len([v for v in violations if v['severity'] == 'error']),
                    'warning': len([v for v in violations if v['severity'] == 'warning'])
                }
            },
            'constraint_violations': violations,
            'categorical_consistency': []
        }
        return self.results

    def print_report(self):
        summary = self.results['summary']
        print(f"   • Quality Score: {summary['data_quality_score']:.1f}/100")
        print(f"   • Violations found: {summary['total_issues']}")
