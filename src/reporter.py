# src/reporter.py
"""
Report Generator - Creates comprehensive HTML reports with visualizations
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO


class ReportGenerator:
    """Generates comprehensive data quality reports in multiple formats."""
    
    def __init__(self, df: pd.DataFrame, profile: Dict, missing_analysis: Dict, 
                 outlier_results: Dict, validation_results: Dict):
        self.df = df
        self.profile = profile
        self.missing_analysis = missing_analysis
        self.outlier_results = outlier_results
        self.validation_results = validation_results
        
        # Set plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
    
    def generate_html_report(self, output_path: str = 'data_quality_report.html'):
        """Generate comprehensive HTML report."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Quality Audit Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            border-bottom: 4px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-align: center;
        }}
        h2 {{
            color: #764ba2;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 5px solid #764ba2;
            font-size: 1.8em;
        }}
        h3 {{
            color: #555;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            color: white;
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .stat-value {{
            font-size: 2.2em;
            font-weight: bold;
        }}
        .issue-card {{
            background: #fff5f5;
            border-left: 4px solid #fc8181;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .warning-card {{
            background: #fffaf0;
            border-left: 4px solid #f6ad55;
        }}
        .info-card {{
            background: #f0f9ff;
            border-left: 4px solid #63b3ed;
        }}
        .success-card {{
            background: #f0fff4;
            border-left: 4px solid #68d391;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background-color: #f8f9ff;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 0 5px;
        }}
        .badge-error {{ background: #fc8181; color: white; }}
        .badge-warning {{ background: #f6ad55; color: white; }}
        .badge-info {{ background: #63b3ed; color: white; }}
        .badge-success {{ background: #68d391; color: white; }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .timestamp {{
            text-align: center;
            color: #888;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        .quality-score {{
            text-align: center;
            margin: 30px 0;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
        }}
        .quality-score .score {{
            font-size: 4em;
            font-weight: bold;
            margin: 20px 0;
        }}
        .recommendation {{
            background: #f0f9ff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #63b3ed;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Data Quality Audit Report</h1>
        
        {self._generate_executive_summary()}
        {self._generate_profile_section()}
        {self._generate_missing_values_section()}
        {self._generate_outliers_section()}
        {self._generate_validation_section()}
        {self._generate_recommendations_section()}
        
        <div class="timestamp">
            Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report generated: {output_path}")
        return output_path
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary section."""
        meta = self.profile['metadata']
        summary = self.missing_analysis['overall_stats']
        val_summary = self.validation_results['summary']
        
        html = f"""
        <div class="quality-score">
            <h2 style="color: white; border: none; padding: 0; margin: 0;">Overall Data Quality Score</h2>
            <div class="score">{val_summary['data_quality_score']:.1f}/100</div>
            <p>{'✅ Dataset meets quality standards' if val_summary['validation_passed'] else '⚠️ Quality issues detected'}</p>
        </div>
        
        <h2>📊 Executive Summary</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Records</div>
                <div class="stat-value">{meta['total_rows']:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Columns</div>
                <div class="stat-value">{meta['total_columns']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Missing Data</div>
                <div class="stat-value">{summary['missing_percentage']:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Complete Rows</div>
                <div class="stat-value">{summary['complete_rows_percentage']:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Duplicate Rows</div>
                <div class="stat-value">{meta['duplicate_rows']:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Quality Issues</div>
                <div class="stat-value">{val_summary['total_issues']}</div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_profile_section(self) -> str:
        """Generate dataset profile section."""
        types = self.profile['data_types']
        
        html = f"""
        <h2>📋 Dataset Profile</h2>
        
        <h3>Column Distribution by Type</h3>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Numeric Columns</div>
                <div class="stat-value">{len(types['numeric'])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Categorical Columns</div>
                <div class="stat-value">{len(types['categorical'])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">DateTime Columns</div>
                <div class="stat-value">{len(types['datetime'])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Boolean Columns</div>
                <div class="stat-value">{len(types['boolean'])}</div>
            </div>
        </div>
        
        {self._generate_missing_heatmap()}
        """
        
        return html
    
    def _generate_missing_values_section(self) -> str:
        """Generate missing values analysis section."""
        col_analysis = self.missing_analysis['column_analysis']
        
        # Filter columns with missing values
        columns_with_missing = [c for c in col_analysis if c['missing_percentage'] > 0]
        
        if not columns_with_missing:
            return """
            <h2>✅ Missing Values Analysis</h2>
            <div class="success-card">
                <h3>No Missing Values Detected</h3>
                <p>All columns are complete with no missing data.</p>
            </div>
            """
        
        html = f"""
        <h2>❌ Missing Values Analysis</h2>
        
        <h3>Columns with Missing Data</h3>
        <table>
            <thead>
                <tr>
                    <th>Column</th>
                    <th>Missing Count</th>
                    <th>Missing %</th>
                    <th>Severity</th>
                    <th>Data Type</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for col in columns_with_missing[:20]:  # Top 20
            severity_badge = f"badge-{col['severity']}"
            html += f"""
                <tr>
                    <td><strong>{col['column']}</strong></td>
                    <td>{col['missing_count']:,}</td>
                    <td>{col['missing_percentage']:.2f}%</td>
                    <td><span class="badge {severity_badge}">{col['severity'].upper()}</span></td>
                    <td>{col['dtype']}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        
        # Add recommendations
        recommendations = self.missing_analysis.get('recommendations', [])
        if recommendations:
            html += "<h3>Recommended Actions</h3>"
            for rec in recommendations[:10]:
                html += f"""
                <div class="recommendation">
                    <strong>{rec['column']}</strong> ({rec['missing_percentage']:.1f}% missing)
                    <ul style="margin-top: 10px; margin-left: 20px;">
                """
                for strategy in rec['strategies']:
                    html += f"<li>{strategy}</li>"
                html += """
                    </ul>
                </div>
                """
        
        return html
    
    def _generate_outliers_section(self) -> str:
        """Generate outliers detection section."""
        if 'error' in self.outlier_results:
            return f"""
            <h2>📊 Outlier Detection</h2>
            <div class="info-card">
                <p>{self.outlier_results['error']}</p>
            </div>
            """
        
        summary = self.outlier_results.get('summary', {})
        
        html = f"""
        <h2>📊 Outlier Detection</h2>
        
        <h3>Detection Methods</h3>
        <p>Outliers detected using: IQR (Interquartile Range), Z-score, and Isolation Forest (ML-based)</p>
        
        <h3>Per-Column Outlier Summary</h3>
        <table>
            <thead>
                <tr>
                    <th>Column</th>
                    <th>IQR Method</th>
                    <th>Z-score Method</th>
                    <th>ML Method</th>
                    <th>Severity</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for col, col_sum in summary.get('per_column_summary', {}).items():
            severity_class = 'error' if col_sum['severity'] == 'high' else 'warning' if col_sum['severity'] == 'medium' else 'info'
            html += f"""
                <tr>
                    <td><strong>{col}</strong></td>
                    <td>{col_sum['iqr_outliers']}</td>
                    <td>{col_sum['zscore_outliers']}</td>
                    <td>{col_sum['isolation_outliers']}</td>
                    <td><span class="badge badge-{severity_class}">{col_sum['severity'].upper()}</span></td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        
        return html
    
    def _generate_validation_section(self) -> str:
        """Generate validation results section."""
        violations = self.validation_results.get('constraint_violations', [])
        cat_issues = self.validation_results.get('categorical_consistency', [])
        
        html = """<h2>✓ Data Validation Results</h2>"""
        
        if violations:
            html += """
            <h3>Constraint Violations</h3>
            """
            for v in violations:
                severity_class = 'error' if v['severity'] == 'error' else 'warning'
                html += f"""
                <div class="{severity_class}-card">
                    <h4>{v['column']} - {v['constraint']}</h4>
                    <p><strong>Violations:</strong> {v['violations']:,} ({v['percentage']:.2f}%)</p>
                    <p><strong>Expected:</strong> {v.get('expected', v.get('rule', 'N/A'))}</p>
                </div>
                """
        
        if cat_issues:
            html += """
            <h3>Categorical Data Issues</h3>
            """
            for issue in cat_issues:
                html += f"""
                <div class="warning-card">
                    <h4>{issue['column']} - {issue['issue_type'].replace('_', ' ').title()}</h4>
                    <p>{issue.get('recommendation', '')}</p>
                </div>
                """
        
        if not violations and not cat_issues:
            html += """
            <div class="success-card">
                <h3>✅ All Validations Passed</h3>
                <p>No constraint violations or data consistency issues detected.</p>
            </div>
            """
        
        return html
    
    def _generate_recommendations_section(self) -> str:
        """Generate overall recommendations."""
        html = """
        <h2>💡 Key Recommendations</h2>
        <div class="recommendation">
            <h4>Priority Actions:</h4>
            <ul style="margin-left: 20px; margin-top: 10px;">
        """
        
        # Collect top recommendations
        val_summary = self.validation_results['summary']
        
        if val_summary['severity_breakdown']['error'] > 0:
            html += f"<li><strong>Critical:</strong> Address {val_summary['severity_breakdown']['error']} constraint violations immediately</li>"
        
        missing_summary = self.missing_analysis['overall_stats']
        if missing_summary['missing_percentage'] > 10:
            html += f"<li><strong>Missing Data:</strong> {missing_summary['missing_percentage']:.1f}% of data is missing - implement imputation strategy</li>"
        
        if self.profile['metadata']['duplicate_rows'] > 0:
            html += f"<li><strong>Duplicates:</strong> Remove {self.profile['metadata']['duplicate_rows']:,} duplicate rows</li>"
        
        html += """
            </ul>
        </div>
        """
        
        return html
    
    def _generate_missing_heatmap(self) -> str:
        """Generate missing values heatmap."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create missing values matrix
            missing_matrix = self.df.isna()
            
            # Only show columns with missing values
            cols_with_missing = missing_matrix.columns[missing_matrix.any()]
            
            if len(cols_with_missing) == 0:
                plt.close()
                return ""
            
            # Sample if too many rows
            if len(self.df) > 1000:
                sample_indices = self.df.sample(1000, random_state=42).index
                missing_matrix = missing_matrix.loc[sample_indices, cols_with_missing]
            else:
                missing_matrix = missing_matrix[cols_with_missing]
            
            sns.heatmap(missing_matrix, cmap='RdYlGn_r', cbar_kws={'label': 'Missing'}, ax=ax)
            ax.set_title('Missing Values Heatmap', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Columns', fontsize=12)
            ax.set_ylabel('Rows (sample)' if len(self.df) > 1000 else 'Rows', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return f"""
            <div class="chart-container">
                <h3>Missing Values Heatmap</h3>
                <img src="data:image/png;base64,{image_base64}" alt="Missing Values Heatmap">
            </div>
            """
        except Exception as e:
            print(f"Warning: Could not generate heatmap: {e}")
            return ""
    
    def generate_json_report(self, output_path: str = 'data_quality_report.json'):
        """Generate JSON report for programmatic access."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'profile': self.profile,
            'missing_analysis': self.missing_analysis,
            'outlier_detection': self.outlier_results,
            'validation': self.validation_results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ JSON report generated: {output_path}")
        return output_path
    
    def generate_csv_summary(self, output_path: str = 'data_quality_summary.csv'):
        """Generate CSV summary of key metrics."""
        summary_data = []
        
        # Add column-level metrics
        for col, col_profile in self.profile['columns'].items():
            summary_data.append({
                'column': col,
                'dtype': col_profile['dtype'],
                'missing_count': col_profile['missing_count'],
                'missing_percentage': col_profile['missing_percentage'],
                'unique_count': col_profile['unique_count'],
                'mean': col_profile.get('mean'),
                'std': col_profile.get('std'),
                'min': col_profile.get('min'),
                'max': col_profile.get('max')
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_path, index=False)
        
        print(f"✅ CSV summary generated: {output_path}")
        return output_path