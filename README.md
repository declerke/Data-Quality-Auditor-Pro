# 📊 Data Quality Auditor: Automated Profiling & Cleaning

This project is a high-performance Data Quality engine designed to automate the auditing and refinement of tabular datasets. It identifies structural inconsistencies, detects statistical anomalies using Machine Learning, and provides an automated cleaning pipeline to prepare "messy" data for downstream analysis.



---

## 📂 Repository Structure

* **`src/profiler.py`**: Generates high-level metadata, memory usage stats, and identifies constant/useless columns.
* **`src/missing_analyzer.py`**: Performs deep-dive sparsity analysis and recommends imputation strategies.
* **`src/outlier_detector.py`**: Uses a hybrid approach (IQR, Z-Score, and Isolation Forest) to find anomalies.
* **`src/cleaner.py`**: An automated engine for type enforcement, missing value imputation, and outlier clipping.
* **`src/reporter.py`**: Generates interactive HTML dashboards and machine-readable JSON/CSV audit summaries.
* **`main.py`**: The CLI orchestrator that integrates the full audit and cleaning workflow.

---

## 🛠️ Technical Stack

* **Language**: Python 3.12+
* **Data Processing**: Pandas, NumPy
* **Scientific Computing**: SciPy (Statistical Z-scores)
* **Machine Learning**: Scikit-Learn (Isolation Forest)
* **Testing**: Pytest (Test-Driven Development)
* **Reporting**: Matplotlib, Seaborn (Visual Dashboards)

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the dependencies:

```bash
pip install pandas numpy scikit-learn pyyaml matplotlib seaborn pytest
```

### 2. Configuration
The system is rule-driven. Update `config/quality_rules.yaml` to define your specific business constraints (min/max ranges) and expected data types.

### 3. Execution
To run a full audit and generate reports:

```bash
python main.py data/your_dataset.csv
```

To run the audit AND generate an automatically cleaned dataset:

```bash
python main.py data/your_dataset.csv --clean
```

---

## 📊 Pipeline Logic



The auditor follows a four-stage logic to ensure data integrity:

1.  **Profiling**: Detects row/column counts, duplicates, and identifies constant columns that provide no analytical value.
2.  **Analysis**: Evaluates missing value severity and runs hybrid outlier detection (combining traditional statistics with ML anomaly detection).
3.  **Validation**: Checks data against YAML-defined constraints (e.g., Age must be 18–70) and enforces correct data types.
4.  **Cleaning (Optional)**:
    * **Enforce**: Casts columns to correct types.
    * **Drop**: Removes constant columns and duplicate rows.
    * **Impute**: Fills missing values using median/mode based on data distribution.
    * **Handle**: Clips outliers to statistical boundaries.

---

## 🧪 Quality Assurance

This project utilizes `pytest` to maintain logic integrity across all modules.

```bash
python -m pytest tests/
```

The test suite validates:
* Accurate detection of constant columns.
* Correct Z-score calculation.
* Severity-based imputation logic.
* Clipping vs. Removal strategies in the cleaner.

---

## 📝 Reporting

The system outputs three formats:
* **HTML**: A visual dashboard with distribution plots and severity warnings.
* **JSON**: Machine-readable audit results for integration into CI/CD pipelines.
* **CSV**: A flat-file summary of column-level quality scores.

---

### Final Project Tip
When you initialize your GitHub repo, make sure to add a **`.gitignore`** file specifically for Python so that local environment and report folders aren't uploaded.

```text
.venv/
__pycache__/
*.pyc
reports/
data/*.csv
!data/sample_messy_data.csv
```
