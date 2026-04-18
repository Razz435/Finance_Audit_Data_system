"""
Configuration file for Finance Audit Data System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'finance_audit.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Data paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, 'processed')

# Logs
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'finance_audit.log')

# ETL Configuration
ETL_BATCH_SIZE = 10000
ETL_MAX_WORKERS = 4

# API Configuration
API_HOST = '0.0.0.0'
API_PORT = 5000
API_DEBUG = True

# Data Configuration
TOTAL_RECORDS = 1000000  # 1M rows
TEST_RECORDS = 10000     # For testing

# Column mappings
AUDIT_COLUMNS = {
    'transaction_id': 'TEXT PRIMARY KEY',
    'date': 'DATE',
    'amount': 'REAL',
    'account_id': 'TEXT',
    'department': 'TEXT',
    'category': 'TEXT',
    'vendor': 'TEXT',
    'description': 'TEXT',
    'status': 'TEXT',
    'created_at': 'TIMESTAMP',
    'updated_at': 'TIMESTAMP'
}

# Data quality thresholds
MISSING_VALUE_THRESHOLD = 0.05  # 5% tolerance
ANOMALY_Z_SCORE = 3.0
DUPLICATE_CHECK = True

# Performance settings
USE_CACHE = True
CACHE_SIZE = 1000
CHUNK_SIZE = 50000
