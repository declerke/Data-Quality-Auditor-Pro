import pytest
from src.profiler import DatasetProfiler
from src.missing_analyzer import MissingValueAnalyzer
from src.outlier_detector import OutlierDetector
from src.validator import DataValidator

def test_profiler(base_test_data):
    profiler = DatasetProfiler(base_test_data)
    profile = profiler.generate_profile()
    
    assert profile['metadata']['total_rows'] == 10
    assert profile['metadata']['total_columns'] == 5
    assert 'age' in profile['columns']
    assert len(profile['metadata']['constant_columns']) == 0

def test_missing_analyzer(base_test_data):
    analyzer = MissingValueAnalyzer(base_test_data)
    results = analyzer.analyze()
    
    assert results['overall_stats']['missing_percentage'] > 0
    salary_analysis = next(c for c in results['column_analysis'] if c['column'] == 'salary')
    assert salary_analysis['missing_count'] == 1

def test_outlier_detector(base_test_data):
    detector = OutlierDetector(base_test_data, zscore_threshold=1.0)
    results = detector.detect_all()
    
    assert 'summary' in results
    assert 'age' in results['summary']['per_column_summary']

def test_validator(base_test_data, quality_config):
    validator = DataValidator(base_test_data, quality_config['constraints'])
    results = validator.validate_all()
    
    assert results['summary']['total_issues'] > 0
    violations = results['constraint_violations']
    assert any(v['column'] == 'age' and v['constraint'] == 'max_value' for v in violations)