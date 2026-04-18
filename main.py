"""
Main execution script - Finance Audit System
Run the complete pipeline: Data Generation -> ETL -> Quality Checks -> Analytics
"""
import os
import sys
import logging
import argparse
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from config import RAW_DATA_PATH, LOGS_DIR, DATABASE_PATH
from modules.data_generator import generate_data
from etl.etl_pipeline import ETLPipeline, DataQualityPipeline, AnalyticsPipeline, run_complete_pipeline
from database.db_manager import initialize_database
from api.api_server import run_api

# Configure logging
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'main.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║     Finance Audit Data System - End-to-End Pipeline       ║
    ║                                                           ║
    ║  Complete data engineering solution with:                ║
    ║  • Data Ingestion (1M+ rows)                            ║
    ║  • ETL Pipeline (Extract, Transform, Load)              ║
    ║  • Data Quality Checks & Anomaly Detection              ║
    ║  • Analytics & Reporting                                ║
    ║  • REST API for Data Access                             ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def generate_data_command(args):
    """Generate synthetic data"""
    logger.info(f"Generating {args.records:,} records...")
    
    try:
        if not os.path.exists(RAW_DATA_PATH):
            os.makedirs(RAW_DATA_PATH)
        
        from modules.data_generator import FinanceDataGenerator
        
        generator = FinanceDataGenerator(RAW_DATA_PATH, num_records=args.records)
        
        if args.sample:
            generator.generate_sample_csv(num_records=10000)
            logger.info("Sample data generated")
        else:
            generator.generate_csv()
            logger.info(f"Full dataset ({args.records:,} records) generated")
    
    except Exception as e:
        logger.error(f"Error generating data: {e}")
        return False
    
    return True


def initialize_db_command(args):
    """Initialize database"""
    logger.info("Initializing database...")
    
    try:
        initialize_database()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False


def run_etl_command(args):
    """Run ETL pipeline"""
    logger.info("Running ETL pipeline...")
    
    try:
        etl = ETLPipeline()
        summary = etl.run_etl()
        
        logger.info(f"ETL completed: {summary['successful']} records loaded")
        return True
    except Exception as e:
        logger.error(f"ETL error: {e}")
        return False


def run_quality_command(args):
    """Run quality checks"""
    logger.info("Running data quality checks...")
    
    try:
        quality_pipeline = DataQualityPipeline()
        results = quality_pipeline.run_quality_checks()
        
        if results:
            logger.info(f"Quality Score: {results['quality_report']['quality_score']}")
            return True
        return False
    except Exception as e:
        logger.error(f"Quality check error: {e}")
        return False


def run_analytics_command(args):
    """Run analytics pipeline"""
    logger.info("Running analytics...")
    
    try:
        analytics_pipeline = AnalyticsPipeline()
        analytics = analytics_pipeline.generate_analytics()
        
        if analytics:
            logger.info("Analytics generated successfully")
            return True
        return False
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return False


def run_api_command(args):
    """Run REST API server"""
    logger.info(f"Starting API server on {args.host}:{args.port}...")
    
    try:
        run_api(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        logger.error(f"API error: {e}")
        return False


def full_pipeline_command(args):
    """Run complete pipeline"""
    logger.info("Running complete pipeline...")
    logger.info("Steps: Generate Data -> Initialize DB -> ETL -> Quality -> Analytics")
    
    try:
        # Step 1: Generate Data
        if args.skip_generation:
            logger.info("Skipping data generation")
        else:
            logger.info("Step 1: Generating data...")
            if not generate_data_command(argparse.Namespace(records=args.records, sample=args.sample)):
                return False
        
        # Step 2: Initialize Database
        logger.info("Step 2: Initializing database...")
        if not initialize_db_command(args):
            return False
        
        # Step 3: Run ETL
        logger.info("Step 3: Running ETL pipeline...")
        if not run_etl_command(args):
            return False
        
        # Step 4: Run Quality Checks
        logger.info("Step 4: Running quality checks...")
        if not run_quality_command(args):
            return False
        
        # Step 5: Run Analytics
        logger.info("Step 5: Running analytics...")
        if not run_analytics_command(args):
            return False
        
        logger.info("=" * 60)
        logger.info("Complete pipeline executed successfully!")
        logger.info("=" * 60)
        logger.info(f"Database: {DATABASE_PATH}")
        logger.info(f"Logs: {LOGS_DIR}")
        logger.info(f"Run 'python main.py api' to start the API server")
        
        return True
    
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return False


def main():
    """Main entry point"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='Finance Audit System - Data Engineering Pipeline'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate data command
    gen_parser = subparsers.add_parser('generate', help='Generate synthetic data')
    gen_parser.add_argument('--records', type=int, default=1000000, help='Number of records to generate')
    gen_parser.add_argument('--sample', action='store_true', help='Generate sample data (10k records)')
    gen_parser.set_defaults(func=generate_data_command)
    
    # Initialize DB command
    db_parser = subparsers.add_parser('init-db', help='Initialize database')
    db_parser.set_defaults(func=initialize_db_command)
    
    # ETL command
    etl_parser = subparsers.add_parser('etl', help='Run ETL pipeline')
    etl_parser.set_defaults(func=run_etl_command)
    
    # Quality command
    quality_parser = subparsers.add_parser('quality', help='Run data quality checks')
    quality_parser.set_defaults(func=run_quality_command)
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Run analytics pipeline')
    analytics_parser.set_defaults(func=run_analytics_command)
    
    # API command
    api_parser = subparsers.add_parser('api', help='Run REST API server')
    api_parser.add_argument('--host', default='0.0.0.0', help='API host')
    api_parser.add_argument('--port', type=int, default=5000, help='API port')
    api_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    api_parser.set_defaults(func=run_api_command)
    
    # Full pipeline command
    full_parser = subparsers.add_parser('full', help='Run complete pipeline')
    full_parser.add_argument('--records', type=int, default=1000000, help='Number of records')
    full_parser.add_argument('--sample', action='store_true', help='Use sample data (10k)')
    full_parser.add_argument('--skip-generation', action='store_true', help='Skip data generation')
    full_parser.set_defaults(func=full_pipeline_command)
    
    args = parser.parse_args()
    
    # If no command provided, show help and run full pipeline
    if not args.command:
        print("No command provided. Running full pipeline...\n")
        args.command = 'full'
        args.records = 1000000
        args.sample = False
        args.skip_generation = False
        return full_pipeline_command(args)
    
    # Execute command
    try:
        if hasattr(args, 'func'):
            result = args.func(args)
            return 0 if result else 1
        else:
            parser.print_help()
            return 0
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
