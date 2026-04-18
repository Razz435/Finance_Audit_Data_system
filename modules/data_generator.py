"""
Data generation module - Generate realistic finance audit data
"""
import csv
import random
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinanceDataGenerator:
    """Generate synthetic finance audit data"""
    
    def __init__(self, output_dir, num_records=1000000):
        self.output_dir = output_dir
        self.num_records = num_records
        self.start_date = datetime(2020, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        
        # Create output directory if not exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Define data pools
        self.departments = [
            'HR', 'Finance', 'Operations', 'Sales', 'Marketing',
            'IT', 'Legal', 'Compliance', 'Audit', 'Treasury'
        ]
        
        self.categories = [
            'Travel', 'Office Supplies', 'Utilities', 'Rent',
            'Software', 'Consulting', 'Equipment', 'Training',
            'Maintenance', 'Insurance', 'Marketing', 'Vendor Services'
        ]
        
        self.vendors = [
            'Acme Corp', 'Global Solutions', 'Tech Systems', 'Professional Services',
            'Office Pro', 'Cloud Providers', 'Local Supplier', 'Enterprise Software',
            'Consulting Group', 'Facilities Management', 'Data Services', 'Analytics Inc'
        ]
        
        self.statuses = ['pending', 'approved', 'rejected', 'completed', 'on_hold']
    
    def random_date(self):
        """Generate random date between start and end dates"""
        days_diff = (self.end_date - self.start_date).days
        random_days = random.randint(0, days_diff)
        return (self.start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
    
    def random_amount(self):
        """Generate random transaction amount with realistic distribution"""
        # 70% small transactions (< 5000), 25% medium (5000-50000), 5% large (50000+)
        rand = random.random()
        if rand < 0.70:
            return round(random.uniform(10, 5000), 2)
        elif rand < 0.95:
            return round(random.uniform(5000, 50000), 2)
        else:
            return round(random.uniform(50000, 500000), 2)
    
    def generate_csv(self, filename='raw_audit_data.csv'):
        """Generate CSV file with audit data"""
        filepath = os.path.join(self.output_dir, filename)
        logger.info(f"Generating {self.num_records:,} records to {filepath}")
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'transaction_id', 'date', 'amount', 'account_id',
                    'department', 'category', 'vendor', 'description', 'status'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for i in range(self.num_records):
                    # Generate transaction ID
                    transaction_id = f"TXN_{datetime.now().year:04d}_{i:08d}"
                    
                    # Generate random account ID
                    account_id = f"ACC_{random.randint(1000, 9999)}"
                    
                    # Generate description with variety
                    descriptions = [
                        'Office expense reimbursement',
                        'Travel expense report',
                        'Software license payment',
                        'Service invoice',
                        'Equipment purchase',
                        'Vendor payment',
                        'Contractor fee',
                        'Utility bill',
                        'Insurance premium',
                        'Maintenance service'
                    ]
                    
                    record = {
                        'transaction_id': transaction_id,
                        'date': self.random_date(),
                        'amount': self.random_amount(),
                        'account_id': account_id,
                        'department': random.choice(self.departments),
                        'category': random.choice(self.categories),
                        'vendor': random.choice(self.vendors),
                        'description': random.choice(descriptions),
                        'status': random.choice(self.statuses)
                    }
                    
                    writer.writerow(record)
                    
                    # Log progress every 100k records
                    if (i + 1) % 100000 == 0:
                        logger.info(f"Generated {i + 1:,} records")
            
            logger.info(f"CSV file created successfully: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error generating CSV: {e}")
            raise
    
    def generate_sample_csv(self, num_records=10000, filename='sample_audit_data.csv'):
        """Generate smaller sample CSV for testing"""
        filepath = os.path.join(self.output_dir, filename)
        logger.info(f"Generating {num_records:,} sample records to {filepath}")
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'transaction_id', 'date', 'amount', 'account_id',
                    'department', 'category', 'vendor', 'description', 'status'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for i in range(num_records):
                    transaction_id = f"SAMPLE_{i:08d}"
                    account_id = f"ACC_{random.randint(1000, 9999)}"
                    
                    record = {
                        'transaction_id': transaction_id,
                        'date': self.random_date(),
                        'amount': self.random_amount(),
                        'account_id': account_id,
                        'department': random.choice(self.departments),
                        'category': random.choice(self.categories),
                        'vendor': random.choice(self.vendors),
                        'description': 'Sample transaction',
                        'status': random.choice(self.statuses)
                    }
                    
                    writer.writerow(record)
            
            logger.info(f"Sample CSV created: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error generating sample CSV: {e}")
            raise


def generate_data(num_records=1000000, sample_only=False):
    """Main function to generate data"""
    from config import RAW_DATA_PATH
    
    generator = FinanceDataGenerator(RAW_DATA_PATH, num_records)
    
    if sample_only:
        generator.generate_sample_csv(num_records=10000)
    else:
        generator.generate_csv()


if __name__ == "__main__":
    generate_data(num_records=1000000, sample_only=False)
