# Finance Audit Data System

A comprehensive **end-to-end data engineering solution** for financial audit systems with 1M+ rows of data, including data ingestion, ETL pipeline, quality checks, anomaly detection, and REST API.

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│            Data Ingestion Layer                              │
│  Generate 1M synthetic records & Load from CSV               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            ETL Pipeline Layer                                │
│  Extract → Transform → Load                                 │
│  • Data normalization & cleaning                            │
│  • Missing value handling & deduplication                   │
│  • Derived column creation                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│        Database Layer (SQLite)                               │
│  Optimized schema with indices for 1M row performance       │
│  • transactions table                                        │
│  • audit_logs table                                         │
│  • data_quality_checks table                                │
│  • anomalies table                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
        ┌──────────┬─────────┬────────────┐
        │ Quality  │Analytics│ Anomaly    │
        │ Checks   │Pipeline │ Detection  │
        └──────────┴─────────┴────────────┘
              │        │        │
              └────────┼────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │     REST API Layer       │
        │  Flask-based API with    │
        │  comprehensive endpoints │
        └──────────────────────────┘
```

## 🚀 Key Features

### Data Ingestion
- **Generation**: Create synthetic 1M+ financial transaction records
- **Realistic data**: Distribution of amounts, dates, departments, categories
- **CSV import**: Read and process data from CSV files

### ETL Pipeline
- **Extract**: Read data in chunks for memory efficiency
- **Transform**: 
  - Amount normalization (remove negatives, cap outliers)
  - Date validation and standardization
  - Text field standardization
  - Missing value handling
  - Duplicate removal
  - Derived column creation (quarter, year, month, brackets)
- **Load**: Batch insert into SQLite database

### Data Quality & Validation
- **Completeness**: Check for missing values per column
- **Accuracy**: Validate numeric/date formats and ranges
- **Consistency**: Verify categorical values and patterns
- **Duplicates**: Detect duplicate transactions
- **Quality Score**: 0-100 scoring system

### Anomaly Detection
- **Z-score outlier detection**: Identify statistical outliers
- **IQR method**: Detect outliers using quartiles
- **Pattern analysis**: Find unusual transaction patterns
- **Fraud indicators**: Identify high-risk transactions

### Analytics
- Summary statistics (total, mean, median, std)
- Aggregations by department, category, status
- Top vendors and accounts analysis
- Time-series aggregations

### REST API
- Transaction retrieval with filtering
- Statistics endpoints (by department, category, status)
- Data quality validation
- Anomaly detection
- Top values queries

## 📁 Project Structure

```
finance_audit_system/
├── config.py                      # Configuration settings
├── main.py                        # Main execution script
├── requirements.txt               # Python dependencies
├── README.md                      # This file
│
├── database/
│   ├── __init__.py
│   └── db_manager.py             # Database operations & schema
│
├── modules/
│   ├── __init__.py
│   ├── data_generator.py         # Synthetic data generation
│   ├── data_transformer.py       # Transform, normalize, aggregate
│   └── data_quality.py           # QA checks & anomaly detection
│
├── etl/
│   ├── __init__.py
│   └── etl_pipeline.py           # Complete ETL pipeline
│
├── api/
│   ├── __init__.py
│   └── api_server.py             # Flask REST API
│
├── data/
│   ├── raw/                      # Raw CSV files
│   └── processed/                # Processed data
│
├── logs/                         # Log files
├── tests/                        # Unit tests
└── database/
    └── finance_audit.db          # SQLite database
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Windows 10/11 (or any OS with Python support)

### Setup

1. **Clone/Create Project**:
```bash
cd c:\Users\rahul\Documents\finance_audit_system
```

2. **Create Virtual Environment** (optional but recommended):
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

## 📋 Usage

### Running the Complete Pipeline

```bash
python main.py full
```
This runs all steps: Generate Data → Initialize DB → ETL → Quality → Analytics

### Individual Commands

**Generate Synthetic Data (1M rows)**:
```bash
python main.py generate --records 1000000
```

**Generate Sample Data (10K rows for testing)**:
```bash
python main.py generate --sample
```

**Initialize Database**:
```bash
python main.py init-db
```

**Run ETL Pipeline**:
```bash
python main.py etl
```

**Run Data Quality Checks**:
```bash
python main.py quality
```

**Run Analytics Pipeline**:
```bash
python main.py analytics
```

**Start REST API Server**:
```bash
python main.py api --host 0.0.0.0 --port 5000
```

## 🔌 REST API Endpoints

### Health & Info
- `GET /api/health` - Health check

### Transactions
- `GET /api/transactions` - Get all transactions (with filters)
  - Query params: `limit`, `offset`, `status`, `department`, `min_amount`, `max_amount`
- `GET /api/transactions/<transaction_id>` - Get specific transaction
- `GET /api/transactions/count` - Get total count

### Statistics
- `GET /api/statistics/summary` - Summary statistics
- `GET /api/statistics/by-department` - Stats grouped by department
- `GET /api/statistics/by-category` - Stats grouped by category
- `GET /api/statistics/by-status` - Stats grouped by status

### Top Values
- `GET /api/top-vendors?limit=10` - Top vendors
- `GET /api/top-accounts?limit=10` - Top accounts

### Data Quality
- `GET /api/quality/validate` - Validate data quality
- `GET /api/quality/anomalies` - Detect anomalies

### Example API Calls

```bash
# Get summary statistics
curl http://localhost:5000/api/statistics/summary

# Get transactions from Sales department
curl "http://localhost:5000/api/transactions?department=SALES&limit=20"

# Get transactions with amount between 1000 and 10000
curl "http://localhost:5000/api/transactions?min_amount=1000&max_amount=10000"

# Run quality validation
curl http://localhost:5000/api/quality/validate

# Detect anomalies
curl http://localhost:5000/api/quality/anomalies

# Get top 5 vendors
curl "http://localhost:5000/api/top-vendors?limit=5"
```

## 📊 Data Schema

### Transactions Table
```sql
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    amount REAL NOT NULL,
    account_id TEXT NOT NULL,
    department TEXT NOT NULL,
    category TEXT NOT NULL,
    vendor TEXT,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Related Tables
- **audit_logs** - Track changes to transactions
- **data_quality_checks** - Quality check results
- **anomalies** - Detected anomalies

## 📈 Performance Optimization

### For 1M+ Rows
1. **Batch Processing**: ETL processes data in 10k-row chunks
2. **Database Indices**: Created on frequently queried columns
3. **Memory Efficient**: Uses pandas chunked reading
4. **Query Optimization**: Proper SQL indexing on date, amount, department, etc.

### Configuration (config.py)
```python
TOTAL_RECORDS = 1000000        # Total records to generate
ETL_BATCH_SIZE = 10000         # Batch size for processing
CHUNK_SIZE = 50000             # Database chunk size
USE_CACHE = True               # Enable caching
CACHE_SIZE = 1000              # Cache size
```

## 🔍 Data Quality Checks

**Completeness**: % of missing values per column
**Accuracy**: Valid formats and value ranges
**Consistency**: Proper categorical values
**Duplicates**: Duplicate transaction detection
**Quality Score**: Composite 0-100 score

## 🚨 Anomaly Detection

1. **Z-score Outliers**: Identify statistical outliers (>3σ)
2. **IQR Outliers**: Quartile-based outlier detection
3. **Pattern Analysis**: Unusual transaction patterns
4. **Fraud Indicators**: High-value rejections, very large amounts, old pending transactions

## 📝 Logging

All operations logged to:
- `logs/main.log` - Main execution logs
- `logs/database.log` - Database operations
- `logs/api.log` - API server logs

## 🧪 Testing

Example test scenarios:

```python
# Test data transformation
from modules.data_transformer import DataTransformer
import pandas as pd

df = pd.read_csv('data/raw/raw_audit_data.csv')
transformer = DataTransformer(df)
transformed = transformer.normalize_amounts().normalize_dates().get_dataframe()

# Test quality checks
from modules.data_quality import DataQualityChecker

checker = DataQualityChecker(transformed)
report = checker.generate_report()
print(f"Quality Score: {report['quality_score']}")

# Test anomaly detection
from modules.data_quality import AnomalyDetector

detector = AnomalyDetector(transformed)
summary = detector.detect_all()
print(f"Anomalies found: {summary['total_anomalies']}")
```

## 🎯 Use Cases

1. **Financial Audit**: Detect irregularities in transactions
2. **Compliance**: Validate data quality and completeness
3. **Fraud Detection**: Identify suspicious patterns
4. **Analytics**: Generate business reports
5. **Data Governance**: Monitor data quality metrics

## ⚡ Performance Metrics

**Expected Performance** (on modern hardware):
- Data Generation (1M rows): ~2-3 minutes
- ETL Processing: ~5-7 minutes
- Quality Checks: ~1-2 minutes
- API Response Time: <500ms for typical queries

## 🔒 Security Considerations

1. **SQL Injection Prevention**: Using parameterized queries
2. **Data Validation**: Comprehensive input validation
3. **Error Handling**: Proper error handling without exposing sensitive data
4. **Logging**: Comprehensive audit logging

## 💡 Best Practices Implemented

✅ Modular architecture - Reusable components
✅ Error handling - Comprehensive exception handling
✅ Logging - Track all operations
✅ Configuration management - Centralized settings
✅ Data validation - Multi-layer validation
✅ Performance optimization - Batch processing, indexing
✅ Documentation - Code and user documentation
✅ RESTful API - Standard HTTP methods and status codes

## 📚 Technologies Used

- **Python 3.8+**: Core language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **SQLite**: Lightweight database
- **Flask**: REST API framework
- **SciPy**: Statistical analysis
- **Logging**: Built-in Python logging

## 🤝 Contributing

This is a learning project demonstrating:
- Data Engineering best practices
- ETL pipeline design
- API development
- Data quality management
- Performance optimization
