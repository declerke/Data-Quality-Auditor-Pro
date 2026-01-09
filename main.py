#!/usr/bin/env python3

import pandas as pd
import argparse
import yaml
import os
import sys
from pathlib import Path

from src.profiler import DatasetProfiler
from src.missing_analyzer import MissingValueAnalyzer
from src.outlier_detector import OutlierDetector
from src.validator import DataValidator
from src.reporter import ReportGenerator
from src.cleaner import DataCleaner

class DataQualityAuditor:
    
    def __init__(self, data_path: str, config_path: str = None, output_dir: str = "reports"):
        self.data_path = data_path
        self.output_dir = output_dir
        self.config = self._load_config(config_path)
        self.df = None
        
        os.makedirs(output_dir, exist_ok=True)
    
    def _load_config(self, config_path: str) -> dict:
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        return {
            'outlier_detection': {
                'iqr_multiplier': 1.5,
                'zscore_threshold': 3,
                'isolation_contamination': 0.1
            },
            'missing_values': {
                'warning_threshold': 0.05,
                'critical_threshold': 0.30
            },
            'constraints': {},
            'reporting': {
                'generate_html': True,
                'generate_json': True,
                'generate_csv': True
            }
        }
    
    def load_data(self):
        print(f"\n{'='*70}")
        print(f"LOADING DATA: {self.data_path}")
        print(f"{'='*70}")
        
        file_ext = Path(self.data_path).suffix.lower()
        
        try:
            if file_ext == '.csv':
                self.df = pd.read_csv(self.data_path)
            elif file_ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.data_path)
            elif file_ext == '.json':
                self.df = pd.read_json(self.data_path)
            elif file_ext == '.parquet':
                self.df = pd.read_parquet(self.data_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            print(f"✅ Successfully loaded {len(self.df)} rows and {len(self.df.columns)} columns")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def run_audit(self, clean_data: bool = False):
        if self.df is None:
            if not self.load_data():
                return False
        
        print(f"\n{'='*70}")
        print("STARTING DATA QUALITY AUDIT")
        print(f"{'='*70}\n")
        
        print("📊 Step 1/4: Profiling dataset...")
        profiler = DatasetProfiler(self.df)
        profile = profiler.generate_profile()
        profiler.print_summary()
        
        print("\n❌ Step 2/4: Analyzing missing values...")
        missing_config = self.config.get('missing_values', {})
        missing_analyzer = MissingValueAnalyzer(
            self.df,
            warning_threshold=missing_config.get('warning_threshold', 0.05),
            critical_threshold=missing_config.get('critical_threshold', 0.30)
        )
        missing_analysis = missing_analyzer.analyze()
        missing_analyzer.print_report()
        
        print("\n📊 Step 3/4: Detecting outliers...")
        outlier_config = self.config.get('outlier_detection', {})
        outlier_detector = OutlierDetector(
            self.df,
            iqr_multiplier=outlier_config.get('iqr_multiplier', 1.5),
            zscore_threshold=outlier_config.get('zscore_threshold', 3),
            isolation_contamination=outlier_config.get('isolation_contamination', 0.1)
        )
        outlier_results = outlier_detector.detect_all()
        outlier_detector.print_report()
        
        print("\n✓ Step 4/4: Validating data...")
        validator = DataValidator(self.df, self.config.get('constraints', {}))
        validation_results = validator.validate_all()
        validator.print_report()
        
        if clean_data:
            print(f"\n{'='*70}")
            print("AUTOMATED DATA CLEANING")
            print(f"{'='*70}")
            
            cleaner = DataCleaner(self.df)
            
            # 1. Enforce expected types from config
            expected_types = self.config.get('expected_types', {})
            cleaner.enforce_types(expected_types)
            
            # 2. Drop constant columns found during profiling
            cleaner.drop_constant_columns(profile['metadata']['constant_columns'])
            
            # 3. Drop duplicate rows
            cleaner.drop_duplicates()
            
            # 4. Handle missing values based on analyzer logic
            cleaner.handle_missing_values(missing_analysis['column_analysis'])
            
            # 5. Handle outliers based on detector results
            cleaner.handle_outliers(outlier_results['summary']['per_column_summary'])
            
            cleaner.print_cleaning_summary()
            
            clean_filename = f"cleaned_{Path(self.data_path).stem}.csv"
            clean_path = os.path.join(self.output_dir, clean_filename)
            cleaner.get_cleaned_data().to_csv(clean_path, index=False)
            print(f"\n✨ Cleaned dataset saved to: {clean_path}")

        print(f"\n{'='*70}")
        print("GENERATING REPORTS")
        print(f"{'='*70}\n")
        
        reporter = ReportGenerator(
            self.df,
            profile,
            missing_analysis,
            outlier_results,
            validation_results
        )
        
        report_config = self.config.get('reporting', {})
        
        if report_config.get('generate_html', True):
            html_path = os.path.join(self.output_dir, 'data_quality_report.html')
            reporter.generate_html_report(html_path)
        
        if report_config.get('generate_json', True):
            json_path = os.path.join(self.output_dir, 'data_quality_report.json')
            reporter.generate_json_report(json_path)
        
        if report_config.get('generate_csv', True):
            csv_path = os.path.join(self.output_dir, 'data_quality_summary.csv')
            reporter.generate_csv_summary(csv_path)
        
        print(f"\n{'='*70}")
        print("✅ AUDIT COMPLETE!")
        print(f"{'='*70}")
        
        quality_score = validation_results['summary']['data_quality_score']
        emoji = "🟢" if quality_score >= 90 else "🟡" if quality_score >= 70 else "🟠" if quality_score >= 50 else "🔴"
        print(f"\n{emoji} Overall Data Quality Score: {quality_score:.1f}/100\n")
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Data Quality Auditor - Comprehensive data quality analysis tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('data_path', type=str, help='Path to the dataset')
    parser.add_argument('--config', '-c', type=str, default='config/quality_rules.yaml')
    parser.add_argument('--output', '-o', type=str, default='reports')
    parser.add_argument('--clean', action='store_true', help='Perform automated cleaning based on audit results')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_path):
        print(f"❌ Error: File not found: {args.data_path}")
        sys.exit(1)
    
    auditor = DataQualityAuditor(
        data_path=args.data_path,
        config_path=args.config if os.path.exists(args.config) else None,
        output_dir=args.output
    )
    
    success = auditor.run_audit(clean_data=args.clean)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
