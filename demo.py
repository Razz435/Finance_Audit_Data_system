"""
Example/Demo Script - Finance Audit System
Shows how to use each component of the system
"""
import sys
import os
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

import pandas as pd
import logging
from config import RAW_DATA_PATH
from modules.data_generator import FinanceDataGenerator
from modules.data_transformer import DataTransformer, DataAggregator, DataValidator
from modules.data_quality import DataQualityChecker, AnomalyDetector
from database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_data_generation():
    """Demo: Generate sample data"""
    print("\n" + "="*60)
    print("DEMO 1: Data Generation")
    print("="*60)
    
    logger.info("Generating 1000 sample records...")
    
    generator = FinanceDataGenerator(RAW_DATA_PATH, num_records=1000)
    csv_file = generator.generate_sample_csv(num_records=1000, filename='demo_data.csv')
    
    logger.info(f"Sample data generated: {csv_file}")
    
    # Show sample
    df = pd.read_csv(csv_file)
    print(f"\nGenerated {len(df)} records")
    print("\nFirst 5 records:")
    print(df.head())
    print(f"\nColumns: {list(df.columns)}")
    print(f"Data types:\n{df.dtypes}")
    
    return csv_file


def demo_data_transformation(csv_file):
    """Demo: Transform and clean data"""
    print("\n" + "="*60)
    print("DEMO 2: Data Transformation & Cleaning")
    print("="*60)
    
    # Load data
    df = pd.read_csv(csv_file)
    print(f"\nOriginal data shape: {df.shape}")
    print(f"Missing values:\n{df.isnull().sum()}")
    
    # Apply transformations
    logger.info("Applying transformations...")
    transformer = DataTransformer(df)
    
    transformer.normalize_amounts()
    transformer.normalize_dates()
    transformer.standardize_text()
    transformer.handle_missing_values()
    transformer.remove_duplicates()
    transformer.add_derived_columns()
    
    transformed_df = transformer.get_dataframe()
    
    print(f"\nTransformed data shape: {transformed_df.shape}")
    print(f"\nTransformation log:")
    for log in transformer.get_transformation_log():
        print(f"  - {log}")
    
    print(f"\nSample transformed data:")
    print(transformed_df.head())
    
    return transformed_df


def demo_data_validation(df):
    """Demo: Validate data quality"""
    print("\n" + "="*60)
    print("DEMO 3: Data Validation")
    print("="*60)
    
    logger.info("Validating data...")
    validator = DataValidator(df)
    
    print("\nRunning validation checks...")
    results = validator.validate_complete()
    
    print(f"\nValidation Results:")
    for check, result in results.items():
        print(f"\n{check}:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {result}")


def demo_data_quality(df):
    """Demo: Quality checks and scoring"""
    print("\n" + "="*60)
    print("DEMO 4: Data Quality Checks")
    print("="*60)
    
    logger.info("Running quality checks...")
    
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    
    quality_checker = DataQualityChecker(df)
    report = quality_checker.generate_report()
    
    print(f"\nQuality Score: {report['quality_score']}/100")
    print(f"Total Records: {report['total_records']}")
    
    print("\nCompleteness Check:")
    for col, info in report['completeness'].items():
        print(f"  {col}: {info['filled_percentage']:.1f}% complete")
    
    print("\nDuplicate Check:")
    print(f"  {report['duplicates']}")


def demo_anomaly_detection(df):
    """Demo: Detect anomalies"""
    print("\n" + "="*60)
    print("DEMO 5: Anomaly Detection")
    print("="*60)
    
    logger.info("Detecting anomalies...")
    
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    
    detector = AnomalyDetector(df)
    summary = detector.detect_all()
    
    print(f"\nTotal Anomalies Found: {summary['total_anomalies']}")
    
    print("\nAnomalies by Type:")
    for anom_type, count in summary['anomalies_by_type'].items():
        print(f"  {anom_type}: {count}")


def demo_aggregation(df):
    """Demo: Data aggregation"""
    print("\n" + "="*60)
    print("DEMO 6: Data Aggregation & Analytics")
    print("="*60)
    
    logger.info("Aggregating data...")
    
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    
    aggregator = DataAggregator()
    
    # Summary statistics
    print("\nSummary Statistics:")
    stats = aggregator.get_summary_statistics(df)
    for key, value in stats.items():
        print(f"  {key}: {value:,.2f}" if isinstance(value, (int, float)) else f"  {key}: {value}")
    
    # By department
    print("\nAggregation by Department:")
    dept_agg = aggregator.aggregate_by_department(df)
    print(dept_agg)
    
    # By category
    print("\nTop 5 Categories by Amount:")
    cat_agg = aggregator.aggregate_by_category(df)
    top_categories = cat_agg.nlargest(5, ('amount', 'sum'))
    print(top_categories)
    
    # By status
    print("\nAggregation by Status:")
    status_agg = aggregator.aggregate_by_status(df)
    print(status_agg)


def demo_database_operations():
    """Demo: Database operations"""
    print("\n" + "="*60)
    print("DEMO 7: Database Operations")
    print("="*60)
    
    logger.info("Testing database operations...")
    
    db = DatabaseManager()
    db.connect()
    db.create_schema()
    
    print("\nDatabase schema created successfully")
    
    # Sample transaction data
    sample_transactions = [
        ('TXN_DEMO_001', '2024-01-15', 1500.50, 'ACC_1001', 'HR', 'TRAINING', 'Training Corp', 'Training session', 'approved'),
        ('TXN_DEMO_002', '2024-01-16', 250.00, 'ACC_1002', 'IT', 'SOFTWARE', 'Tech Software', 'License renewal', 'pending'),
        ('TXN_DEMO_003', '2024-01-17', 5000.00, 'ACC_1003', 'FINANCE', 'CONSULTING', 'Global Solutions', 'Consulting services', 'completed'),
    ]
    
    # Insert sample data
    inserted = db.insert_transactions_batch(sample_transactions)
    print(f"Inserted {inserted} sample transactions")
    
    # Query data
    print("\nRetrieved transactions from database:")
    results = db.fetch_all("SELECT * FROM transactions LIMIT 5")
    for row in results:
        print(f"  {dict(row)}")
    
    # Get count
    count = db.get_transaction_count()
    print(f"\nTotal transactions in database: {count}")
    
    db.close()
    logger.info("Database operations completed")


def demo_api_usage():
    """Demo: Show API usage examples"""
    print("\n" + "="*60)
    print("DEMO 8: REST API Usage Examples")
    print("="*60)
    
    print("""
To use the REST API, first start the server:
    
    python main.py api

Then you can use these endpoints:

1. Health Check:
   curl http://localhost:5000/api/health

2. Get Transactions:
   curl http://localhost:5000/api/transactions?limit=10
   curl http://localhost:5000/api/transactions?department=SALES
   curl "http://localhost:5000/api/transactions?min_amount=1000&max_amount=10000"

3. Get Transaction by ID:
   curl http://localhost:5000/api/transactions/TXN_2020_00000001

4. Statistics:
   curl http://localhost:5000/api/statistics/summary
   curl http://localhost:5000/api/statistics/by-department
   curl http://localhost:5000/api/statistics/by-category
   curl http://localhost:5000/api/statistics/by-status

5. Top Values:
   curl http://localhost:5000/api/top-vendors?limit=5
   curl http://localhost:5000/api/top-accounts?limit=10

6. Quality Checks:
   curl http://localhost:5000/api/quality/validate
   curl http://localhost:5000/api/quality/anomalies

All endpoints return JSON responses with status and data fields.
    """)


def main():
    """Run all demos"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Finance Audit System - Complete Demo".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Create output directory
        os.makedirs(RAW_DATA_PATH, exist_ok=True)
        
        # Run demos
        csv_file = demo_data_generation()
        transformed_df = demo_data_transformation(csv_file)
        demo_data_validation(transformed_df)
        demo_data_quality(transformed_df)
        demo_anomaly_detection(transformed_df)
        demo_aggregation(transformed_df)
        demo_database_operations()
        demo_api_usage()
        
        print("\n" + "="*60)
        print("✓ All demos completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run full pipeline: python main.py full")
        print("2. Start API server: python main.py api")
        print("3. Check logs: cat logs/main.log")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"\n✗ Error during demo: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
