"""
REST API for Finance Audit System
"""
from flask import Flask, request, jsonify, g
import logging
import os
from datetime import datetime
from functools import wraps
import json
from config import API_HOST, API_PORT, API_DEBUG, LOGS_DIR
from database.db_manager import DatabaseManager
from modules.data_transformer import DataValidator, DataAggregator
from modules.data_quality import DataQualityChecker, AnomalyDetector
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'api.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


def get_db():
    """Get request-local database connection"""
    if 'db' not in g:
        g.db = DatabaseManager()
        g.db.connect()
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def error_handler(f):
    """Decorator for error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({'error': str(e), 'status': 'error'}), 400
    return decorated_function


# Root Endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        'status': 'success',
        'message': 'Finance Audit System API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'transactions': {
                'list': '/api/transactions',
                'get': '/api/transactions/<id>',
                'count': '/api/transactions/count'
            },
            'statistics': {
                'summary': '/api/statistics/summary',
                'by_department': '/api/statistics/by-department',
                'by_category': '/api/statistics/by-category',
                'by_status': '/api/statistics/by-status'
            },
            'quality': {
                'validate': '/api/quality/validate',
                'anomalies': '/api/quality/anomalies'
            },
            'top': {
                'vendors': '/api/top-vendors',
                'accounts': '/api/top-accounts'
            }
        }
    }), 200


# Health Check Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = get_db()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Finance Audit System API'
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


# Transaction Endpoints
@app.route('/api/transactions', methods=['GET'])
@error_handler
def get_transactions():
    """Get all transactions with filtering"""
    db = get_db()
    
    # Query parameters
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    status = request.args.get('status')
    department = request.args.get('department')
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    
    # Build query
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status.lower())
    if department:
        query += " AND department = ?"
        params.append(department.upper())
    if min_amount is not None:
        query += " AND amount >= ?"
        params.append(min_amount)
    if max_amount is not None:
        query += " AND amount <= ?"
        params.append(max_amount)
    
    query += f" LIMIT {limit} OFFSET {offset}"
    
    results = db.fetch_all(query, params)
    transactions = [dict(row) for row in results]
    
    return jsonify({
        'status': 'success',
        'count': len(transactions),
        'limit': limit,
        'offset': offset,
        'data': transactions
    }), 200


@app.route('/api/transactions/<transaction_id>', methods=['GET'])
@error_handler
def get_transaction(transaction_id):
    """Get specific transaction"""
    db = get_db()
    
    query = "SELECT * FROM transactions WHERE transaction_id = ?"
    result = db.fetch_one(query, [transaction_id])
    
    if result:
        return jsonify({
            'status': 'success',
            'data': dict(result)
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Transaction not found'
        }), 404


@app.route('/api/transactions/count', methods=['GET'])
@error_handler
def get_transaction_count():
    """Get total transaction count"""
    db = get_db()
    count = db.get_transaction_count()
    
    return jsonify({
        'status': 'success',
        'total_transactions': count
    }), 200


# Statistics Endpoints
@app.route('/api/statistics/summary', methods=['GET'])
@error_handler
def get_summary_statistics():
    """Get summary statistics"""
    db = get_db()
    
    results = db.fetch_all("SELECT * FROM transactions")
    if not results:
        return jsonify({'status': 'error', 'message': 'No data'}), 404
    
    df = pd.DataFrame([dict(row) for row in results])
    df['amount'] = pd.to_numeric(df['amount'])
    
    stats = DataAggregator.get_summary_statistics(df)
    
    return jsonify({
        'status': 'success',
        'data': stats
    }), 200


@app.route('/api/statistics/by-department', methods=['GET'])
@error_handler
def get_statistics_by_department():
    """Get statistics grouped by department"""
    db = get_db()
    
    query = """
    SELECT department, 
           COUNT(*) as transaction_count,
           SUM(amount) as total_amount,
           AVG(amount) as avg_amount,
           MIN(amount) as min_amount,
           MAX(amount) as max_amount
    FROM transactions
    GROUP BY department
    ORDER BY total_amount DESC
    """
    
    results = db.fetch_all(query)
    data = [dict(row) for row in results]
    
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    }), 200


@app.route('/api/statistics/by-category', methods=['GET'])
@error_handler
def get_statistics_by_category():
    """Get statistics grouped by category"""
    db = get_db()
    
    query = """
    SELECT category,
           COUNT(*) as transaction_count,
           SUM(amount) as total_amount,
           AVG(amount) as avg_amount
    FROM transactions
    GROUP BY category
    ORDER BY total_amount DESC
    """
    
    results = db.fetch_all(query)
    data = [dict(row) for row in results]
    
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    }), 200


@app.route('/api/statistics/by-status', methods=['GET'])
@error_handler
def get_statistics_by_status():
    """Get statistics grouped by status"""
    db = get_db()
    
    query = """
    SELECT status,
           COUNT(*) as transaction_count,
           SUM(amount) as total_amount,
           AVG(amount) as avg_amount,
           MIN(amount) as min_amount,
           MAX(amount) as max_amount
    FROM transactions
    GROUP BY status
    """
    
    results = db.fetch_all(query)
    data = [dict(row) for row in results]
    
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    }), 200


# Data Quality Endpoints
@app.route('/api/quality/validate', methods=['GET'])
@error_handler
def validate_data_quality():
    """Validate data quality"""
    db = get_db()
    
    results = db.fetch_all("SELECT * FROM transactions")
    if not results:
        return jsonify({'status': 'error', 'message': 'No data'}), 404
    
    df = pd.DataFrame([dict(row) for row in results])
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    
    quality_checker = DataQualityChecker(df)
    report = quality_checker.generate_report()
    
    return jsonify({
        'status': 'success',
        'data': report
    }), 200


@app.route('/api/quality/anomalies', methods=['GET'])
@error_handler
def detect_anomalies():
    """Detect data anomalies"""
    db = get_db()
    
    results = db.fetch_all("SELECT * FROM transactions")
    if not results:
        return jsonify({'status': 'error', 'message': 'No data'}), 404
    
    df = pd.DataFrame([dict(row) for row in results])
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    
    detector = AnomalyDetector(df)
    summary = detector.detect_all()
    
    return jsonify({
        'status': 'success',
        'data': summary
    }), 200


# Top Values Endpoints
@app.route('/api/top-vendors', methods=['GET'])
@error_handler
def get_top_vendors():
    """Get top vendors by transaction count"""
    limit = request.args.get('limit', 10, type=int)
    db = get_db()
    
    query = f"""
    SELECT vendor,
           COUNT(*) as transaction_count,
           SUM(amount) as total_amount
    FROM transactions
    WHERE vendor IS NOT NULL
    GROUP BY vendor
    ORDER BY transaction_count DESC
    LIMIT {limit}
    """
    
    results = db.fetch_all(query)
    data = [dict(row) for row in results]
    
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    }), 200


@app.route('/api/top-accounts', methods=['GET'])
@error_handler
def get_top_accounts():
    """Get top accounts by amount"""
    limit = request.args.get('limit', 10, type=int)
    db = get_db()
    
    query = f"""
    SELECT account_id,
           COUNT(*) as transaction_count,
           SUM(amount) as total_amount,
           AVG(amount) as avg_amount
    FROM transactions
    GROUP BY account_id
    ORDER BY total_amount DESC
    LIMIT {limit}
    """
    
    results = db.fetch_all(query)
    data = [dict(row) for row in results]
    
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


def run_api(host=API_HOST, port=API_PORT, debug=API_DEBUG):
    """Run Flask API server"""
    logger.info(f"Starting Finance Audit API on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    run_api()
