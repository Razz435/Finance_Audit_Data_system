"""
Data transformation and cleaning module
"""
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transform and clean financial data"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.transformation_log = []
    
    def normalize_amounts(self):
        """Normalize amount values and handle outliers"""
        logger.info("Normalizing amount values...")
        
        # Convert to numeric
        self.df['amount'] = pd.to_numeric(self.df['amount'], errors='coerce')
        
        # Remove negative amounts (invalid in most audit contexts)
        invalid_count = (self.df['amount'] < 0).sum()
        self.df = self.df[self.df['amount'] >= 0]
        self.transformation_log.append(f"Removed {invalid_count} negative amounts")
        
        # Cap extreme outliers (> 99.9th percentile)
        percentile_999 = self.df['amount'].quantile(0.999)
        capped_count = (self.df['amount'] > percentile_999).sum()
        self.df.loc[self.df['amount'] > percentile_999, 'amount'] = percentile_999
        self.transformation_log.append(f"Capped {capped_count} amounts to 99.9th percentile")
        
        return self
    
    def normalize_dates(self):
        """Normalize and validate date values"""
        logger.info("Normalizing dates...")
        
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        
        # Remove future dates
        future_count = (self.df['date'] > datetime.now()).sum()
        self.df = self.df[self.df['date'] <= datetime.now()]
        self.transformation_log.append(f"Removed {future_count} future dates")
        
        # Remove dates before audit period start (e.g., before 2015)
        old_count = (self.df['date'] < pd.Timestamp('2015-01-01')).sum()
        self.df = self.df[self.df['date'] >= pd.Timestamp('2015-01-01')]
        self.transformation_log.append(f"Removed {old_count} dates before 2015")
        
        return self
    
    def standardize_text(self):
        """Standardize text fields"""
        logger.info("Standardizing text fields...")
        
        text_columns = ['department', 'category', 'vendor', 'status']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].str.strip().str.upper()
        
        self.transformation_log.append("Text fields standardized to uppercase")
        return self
    
    def handle_missing_values(self, strategy='drop'):
        """Handle missing values"""
        logger.info(f"Handling missing values with strategy: {strategy}")
        
        missing_before = self.df.isnull().sum().sum()
        
        if strategy == 'drop':
            self.df = self.df.dropna()
        elif strategy == 'fill_numeric':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
            self.df = self.df.dropna(subset=['transaction_id', 'date', 'amount'])
        
        missing_after = self.df.isnull().sum().sum()
        self.transformation_log.append(f"Handled missing values: {missing_before} -> {missing_after}")
        
        return self
    
    def remove_duplicates(self, subset=None):
        """Remove duplicate transactions"""
        logger.info("Removing duplicates...")
        
        duplicates_before = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset or ['transaction_id'], keep='first')
        duplicates_after = len(self.df)
        
        removed = duplicates_before - duplicates_after
        self.transformation_log.append(f"Removed {removed} duplicates")
        
        return self
    
    def add_derived_columns(self):
        """Add calculated/derived columns for analytics"""
        logger.info("Adding derived columns...")
        
        # Quarter from date
        self.df['quarter'] = self.df['date'].dt.quarter
        self.df['year'] = self.df['date'].dt.year
        self.df['month'] = self.df['date'].dt.month
        
        # Amount brackets for categorization
        self.df['amount_bracket'] = pd.cut(
            self.df['amount'],
            bins=[0, 1000, 5000, 50000, float('inf')],
            labels=['Small', 'Medium', 'Large', 'Very Large']
        )
        
        # Amount category based on status
        self.df['is_approved'] = (self.df['status'] == 'APPROVED').astype(int)
        self.df['is_pending'] = (self.df['status'] == 'PENDING').astype(int)
        
        self.transformation_log.append("Added derived columns: quarter, year, month, amount_bracket, is_approved, is_pending")
        
        return self
    
    def aggregate_by_dimension(self, group_by, agg_dict):
        """Aggregate data by specified dimensions"""
        logger.info(f"Aggregating data by: {group_by}")
        
        aggregated = self.df.groupby(group_by).agg(agg_dict).reset_index()
        return aggregated
    
    def get_transformation_log(self):
        """Get log of transformations applied"""
        return self.transformation_log
    
    def get_dataframe(self):
        """Return transformed dataframe"""
        return self.df


class DataValidator:
    """Validate data quality"""
    
    def __init__(self, df):
        self.df = df
        self.validation_results = {}
    
    def validate_required_fields(self):
        """Check for required fields"""
        required_fields = ['transaction_id', 'date', 'amount', 'account_id']
        missing = {}
        
        for field in required_fields:
            if field not in self.df.columns:
                missing[field] = 'Column missing'
            else:
                null_count = self.df[field].isnull().sum()
                if null_count > 0:
                    missing[field] = f"{null_count} null values"
        
        self.validation_results['required_fields'] = missing
        return len(missing) == 0
    
    def validate_amount_range(self, min_val=0, max_val=1000000):
        """Validate amounts are within acceptable range"""
        if 'amount' not in self.df.columns:
            self.validation_results['amount_range'] = 'amount column missing'
            return False
        
        out_of_range = ((self.df['amount'] < min_val) | (self.df['amount'] > max_val)).sum()
        self.validation_results['amount_range'] = {
            'out_of_range_count': out_of_range,
            'percentage': (out_of_range / len(self.df)) * 100 if len(self.df) > 0 else 0
        }
        
        return out_of_range == 0
    
    def validate_date_range(self, start_date='2015-01-01', end_date=None):
        """Validate dates within expected range"""
        if 'date' not in self.df.columns:
            self.validation_results['date_range'] = 'date column missing'
            return False
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        out_of_range = (
            (self.df['date'] < pd.Timestamp(start_date)) |
            (self.df['date'] > pd.Timestamp(end_date))
        ).sum()
        
        self.validation_results['date_range'] = {
            'out_of_range_count': out_of_range,
            'percentage': (out_of_range / len(self.df)) * 100 if len(self.df) > 0 else 0
        }
        
        return out_of_range == 0
    
    def validate_unique_ids(self):
        """Check for duplicate transaction IDs"""
        if 'transaction_id' not in self.df.columns:
            self.validation_results['unique_ids'] = 'transaction_id column missing'
            return False
        
        duplicates = self.df['transaction_id'].duplicated().sum()
        self.validation_results['unique_ids'] = {
            'duplicate_count': duplicates,
            'percentage': (duplicates / len(self.df)) * 100 if len(self.df) > 0 else 0
        }
        
        return duplicates == 0
    
    def validate_complete(self):
        """Run all validations"""
        logger.info("Running complete data validation...")
        
        self.validate_required_fields()
        self.validate_amount_range()
        self.validate_date_range()
        self.validate_unique_ids()
        
        logger.info(f"Validation results: {self.validation_results}")
        return self.validation_results
    
    def get_summary(self):
        """Get validation summary"""
        return {
            'total_records': len(self.df),
            'validation_results': self.validation_results,
            'timestamp': datetime.now().isoformat()
        }


class DataAggregator:
    """Aggregate data for analytics"""
    
    @staticmethod
    def aggregate_by_department(df):
        """Aggregate transactions by department"""
        return df.groupby('department').agg({
            'amount': ['sum', 'mean', 'count'],
            'transaction_id': 'count'
        }).round(2)
    
    @staticmethod
    def aggregate_by_category(df):
        """Aggregate transactions by category"""
        return df.groupby('category').agg({
            'amount': ['sum', 'mean', 'count'],
            'transaction_id': 'count'
        }).round(2)
    
    @staticmethod
    def aggregate_by_status(df):
        """Aggregate transactions by status"""
        return df.groupby('status').agg({
            'amount': ['sum', 'mean', 'count'],
            'transaction_id': 'count'
        }).round(2)
    
    @staticmethod
    def aggregate_by_date(df, freq='D'):
        """Aggregate transactions by date"""
        df_sorted = df.sort_values('date')
        return df_sorted.groupby(pd.Grouper(key='date', freq=freq)).agg({
            'amount': ['sum', 'count'],
            'transaction_id': 'count'
        }).round(2)
    
    @staticmethod
    def get_summary_statistics(df):
        """Get summary statistics"""
        return {
            'total_amount': df['amount'].sum(),
            'mean_amount': df['amount'].mean(),
            'median_amount': df['amount'].median(),
            'std_amount': df['amount'].std(),
            'total_transactions': len(df),
            'unique_departments': df['department'].nunique() if 'department' in df.columns else 0,
            'unique_vendors': df['vendor'].nunique() if 'vendor' in df.columns else 0,
            'unique_accounts': df['account_id'].nunique() if 'account_id' in df.columns else 0,
        }


if __name__ == "__main__":
    # Example usage
    logger.info("Data transformation module loaded")
