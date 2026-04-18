"""
Database schema and initialization
"""
import sqlite3
import os
from config import DATABASE_PATH, LOGS_DIR
import logging

# Configure logging
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'database.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage database operations including schema creation and queries"""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Create database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, timeout=30.0)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
            return self.connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a single query"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            logger.debug(f"Query executed: {query[:100]}...")
            return cursor
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            self.connection.rollback()
            raise
    
    def fetch_all(self, query, params=None):
        """Fetch all results from a query"""
        cursor = self.execute_query(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """Fetch single result from a query"""
        cursor = self.execute_query(query, params)
        return cursor.fetchone()
    
    def create_schema(self):
        """Create database schema"""
        logger.info("Creating database schema...")
        
        # Create transactions table
        create_transactions = """
        CREATE TABLE IF NOT EXISTS transactions (
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
        """
        
        # Create audit_logs table
        create_audit_logs = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            details TEXT,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
        """
        
        # Create data_quality table
        create_quality = """
        CREATE TABLE IF NOT EXISTS data_quality_checks (
            check_id INTEGER PRIMARY KEY AUTOINCREMENT,
            check_name TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_records INTEGER,
            passed_records INTEGER,
            failed_records INTEGER,
            status TEXT,
            details TEXT
        )
        """
        
        # Create anomaly_detection table
        create_anomalies = """
        CREATE TABLE IF NOT EXISTS anomalies (
            anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            anomaly_type TEXT NOT NULL,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
        """
        
        # Create indices for performance
        create_indices = [
            "CREATE INDEX IF NOT EXISTS idx_date ON transactions(date)",
            "CREATE INDEX IF NOT EXISTS idx_account ON transactions(account_id)",
            "CREATE INDEX IF NOT EXISTS idx_department ON transactions(department)",
            "CREATE INDEX IF NOT EXISTS idx_category ON transactions(category)",
            "CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)",
            "CREATE INDEX IF NOT EXISTS idx_amount ON transactions(amount)"
        ]
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_transactions)
            cursor.execute(create_audit_logs)
            cursor.execute(create_quality)
            cursor.execute(create_anomalies)
            
            for index in create_indices:
                cursor.execute(index)
            
            self.connection.commit()
            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Schema creation error: {e}")
            self.connection.rollback()
            raise
    
    def get_transaction_count(self):
        """Get total transaction count"""
        result = self.fetch_one("SELECT COUNT(*) as count FROM transactions")
        return result['count'] if result else 0
    
    def insert_transactions_batch(self, transactions):
        """Insert batch of transactions"""
        try:
            cursor = self.connection.cursor()
            cursor.executemany(
                """INSERT INTO transactions 
                (transaction_id, date, amount, account_id, department, 
                 category, vendor, description, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                transactions
            )
            self.connection.commit()
            logger.debug(f"Inserted {len(transactions)} transactions")
            return len(transactions)
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            self.connection.rollback()
            raise
    
    def drop_all_tables(self):
        """Drop all tables (for testing/reset)"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS anomalies")
            cursor.execute("DROP TABLE IF EXISTS data_quality_checks")
            cursor.execute("DROP TABLE IF EXISTS audit_logs")
            cursor.execute("DROP TABLE IF EXISTS transactions")
            self.connection.commit()
            logger.info("All tables dropped")
        except Exception as e:
            logger.error(f"Drop tables error: {e}")
            self.connection.rollback()
            raise


def initialize_database():
    """Initialize database with schema"""
    db = DatabaseManager()
    db.connect()
    db.create_schema()
    db.close()
    logger.info("Database initialized successfully")


if __name__ == "__main__":
    initialize_database()
