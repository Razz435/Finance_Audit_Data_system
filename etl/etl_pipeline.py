"""
ETL Pipeline - Extract, Transform, Load
"""
import pandas as pd
import logging
import time
import os
from pathlib import Path
from datetime import datetime
from config import ETL_BATCH_SIZE, RAW_DATA_PATH, PROCESSED_DATA_PATH
from database.db_manager import DatabaseManager
from modules.data_transformer import DataTransformer, DataValidator, DataAggregator
from modules.data_quality import DataQualityChecker, AnomalyDetector

logger = logging.getLogger(__name__)


class ETLPipeline:
    """Complete ETL pipeline for finance audit data"""
    
    def __init__(self, source_file=None, batch_size=ETL_BATCH_SIZE):
        self.source_file = source_file or os.path.join(RAW_DATA_PATH, 'raw_audit_data.csv')
        self.batch_size = batch_size
        self.db = DatabaseManager()
        self.processed_count = 0
        self.failed_count = 0
        self.start_time = None
        self.end_time = None
    
    def extract(self):
        """Extract data from CSV file"""
        logger.info(f"Extracting data from: {self.source_file}")
        
        if not os.path.exists(self.source_file):
            logger.error(f"Source file not found: {self.source_file}")
            raise FileNotFoundError(f"Source file not found: {self.source_file}")
        
        try:
            # Check file size
            file_size = os.path.getsize(self.source_file)
            logger.info(f"File size: {file_size / (1024*1024):.2f} MB")
            
            if file_size == 0:
                logger.error("Source file is empty")
                raise ValueError("Source file is empty")
            
            # Read CSV in chunks for memory efficiency
            # Convert iterator to list to ensure it doesn't hang
            chunks = list(pd.read_csv(self.source_file, chunksize=self.batch_size))
            logger.info(f"Data extraction completed: {len(chunks)} chunks")
            return iter(chunks)  # Return iterator from list
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            raise
    
    def transform(self, df):
        """Transform data - clean, normalize, validate"""
        logger.info(f"Transforming {len(df)} records...")
        
        try:
            # Apply transformations
            transformer = DataTransformer(df)
            transformer.normalize_amounts()
            transformer.normalize_dates()
            transformer.standardize_text()
            transformer.handle_missing_values(strategy='drop')
            transformer.remove_duplicates()
            transformer.add_derived_columns()
            
            transformed_df = transformer.get_dataframe()
            
            # Validate
            validator = DataValidator(transformed_df)
            validator.validate_complete()
            
            logger.info(f"Transformation completed: {len(transformed_df)} records after cleaning")
            return transformed_df
        
        except Exception as e:
            logger.error(f"Transformation error: {e}")
            raise
    
    def load(self, df):
        """Load data into database"""
        logger.info(f"Loading {len(df)} records into database...")
        
        try:
            # Prepare data for database insertion
            records = []
            for _, row in df.iterrows():
                record = (
                    str(row['transaction_id']),
                    str(row['date']),
                    float(row['amount']),
                    str(row['account_id']),
                    str(row['department']),
                    str(row['category']),
                    str(row['vendor']) if pd.notna(row['vendor']) else None,
                    str(row['description']) if pd.notna(row['description']) else None,
                    str(row['status']).lower()
                )
                records.append(record)
            
            # Insert batch
            loaded = self.db.insert_transactions_batch(records)
            self.processed_count += loaded
            
            logger.info(f"Loaded {loaded} records")
            return loaded
        
        except Exception as e:
            logger.error(f"Load error: {e}")
            self.failed_count += len(df)
            raise
    
    def run_etl(self):
        """Execute complete ETL pipeline"""
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 60)
        
        self.start_time = time.time()
        chunk_count = 0
        
        try:
            # Connect to database
            self.db.connect()
            self.db.create_schema()
            
            # Extract data in chunks
            chunks = self.extract()
            
            # Transform and Load for each chunk
            for i, chunk in enumerate(chunks, 1):
                try:
                    chunk_records = len(chunk)
                    logger.info(f"Processing chunk {i}: {chunk_records} records")
                    
                    if chunk_records == 0:
                        logger.warning(f"Chunk {i} is empty, skipping")
                        continue
                    
                    # Transform
                    transformed = self.transform(chunk)
                    
                    # Load
                    if len(transformed) > 0:
                        self.load(transformed)
                    
                    chunk_count = i
                
                except Exception as e:
                    logger.error(f"Error processing chunk {i}: {e}")
                    self.failed_count += len(chunk) if 'chunk' in locals() else 0
            
            logger.info(f"Processed {chunk_count} chunks total")
            
            # Finalize
            self.end_time = time.time()
            
            return self.get_summary()
        
        finally:
            self.db.close()
    
    def get_summary(self):
        """Get ETL execution summary"""
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        summary = {
            'status': 'completed',
            'total_processed': self.processed_count,
            'failed': self.failed_count,
            'successful': self.processed_count - self.failed_count,
            'duration_seconds': round(duration, 2),
            'records_per_second': round(self.processed_count / duration, 2) if duration > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("=" * 60)
        logger.info("ETL Pipeline Summary")
        logger.info("=" * 60)
        for key, value in summary.items():
            logger.info(f"{key}: {value}")
        
        return summary


class DataQualityPipeline:
    """Pipeline for data quality checks and anomaly detection"""
    
    def __init__(self, db=None):
        self.db = db or DatabaseManager()
    
    def run_quality_checks(self):
        """Run comprehensive quality checks"""
        logger.info("Running data quality checks...")
        
        try:
            self.db.connect()
            
            # Fetch all data
            query = "SELECT * FROM transactions"
            results = self.db.fetch_all(query)
            
            if not results:
                logger.warning("No data found in database")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame([dict(row) for row in results])
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
            
            # Run quality checks
            quality_checker = DataQualityChecker(df)
            quality_report = quality_checker.generate_report()
            
            # Run anomaly detection
            anomaly_detector = AnomalyDetector(df)
            anomaly_summary = anomaly_detector.detect_all()
            
            return {
                'quality_report': quality_report,
                'anomaly_summary': anomaly_summary,
                'timestamp': datetime.now().isoformat()
            }
        
        finally:
            self.db.close()


class AnalyticsPipeline:
    """Pipeline for generating analytics and reports"""
    
    def __init__(self, db=None):
        self.db = db or DatabaseManager()
    
    def generate_analytics(self):
        """Generate comprehensive analytics"""
        logger.info("Generating analytics...")
        
        try:
            self.db.connect()
            
            # Fetch all data
            query = "SELECT * FROM transactions"
            results = self.db.fetch_all(query)
            
            if not results:
                logger.warning("No data found")
                return None
            
            df = pd.DataFrame([dict(row) for row in results])
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
            
            # Generate aggregations
            aggregator = DataAggregator()
            
            analytics = {
                'summary_statistics': aggregator.get_summary_statistics(df),
                'by_department': aggregator.aggregate_by_department(df).to_dict(),
                'by_category': aggregator.aggregate_by_category(df).to_dict(),
                'by_status': aggregator.aggregate_by_status(df).to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("Analytics generation completed")
            return analytics
        
        finally:
            self.db.close()


def run_complete_pipeline(data_file=None):
    """Run complete ETL + Quality + Analytics pipeline"""
    logger.info("Starting complete data pipeline...")
    
    # ETL Pipeline
    etl = ETLPipeline(source_file=data_file)
    etl_summary = etl.run_etl()
    
    # Quality Checks Pipeline
    quality_pipeline = DataQualityPipeline()
    quality_results = quality_pipeline.run_quality_checks()
    
    # Analytics Pipeline
    analytics_pipeline = AnalyticsPipeline()
    analytics = analytics_pipeline.generate_analytics()
    
    return {
        'etl_summary': etl_summary,
        'quality_results': quality_results,
        'analytics': analytics
    }


if __name__ == "__main__":
    logger.info("ETL Pipeline module loaded")
