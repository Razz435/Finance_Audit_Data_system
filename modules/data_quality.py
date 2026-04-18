"""
Data quality checks and anomaly detection
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from scipy import stats

logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Check data quality metrics"""
    
    def __init__(self, df):
        self.df = df
        self.checks_results = {}
    
    def check_completeness(self):
        """Check percentage of missing values per column"""
        logger.info("Checking data completeness...")
        
        completeness = {}
        for col in self.df.columns:
            null_count = self.df[col].isnull().sum()
            completeness[col] = {
                'null_count': int(null_count),
                'null_percentage': round((null_count / len(self.df)) * 100, 2) if len(self.df) > 0 else 0,
                'filled_percentage': round(100 - (null_count / len(self.df)) * 100, 2) if len(self.df) > 0 else 100
            }
        
        self.checks_results['completeness'] = completeness
        return completeness
    
    def check_accuracy(self):
        """Check data accuracy (valid formats, ranges)"""
        logger.info("Checking data accuracy...")
        
        accuracy = {}
        
        # Check amount is numeric and positive
        if 'amount' in self.df.columns:
            try:
                amounts = pd.to_numeric(self.df['amount'], errors='coerce')
                invalid_amounts = amounts.isnull().sum() + (amounts < 0).sum()
                accuracy['amount'] = {
                    'invalid_count': int(invalid_amounts),
                    'percentage': round((invalid_amounts / len(self.df)) * 100, 2)
                }
            except:
                accuracy['amount'] = {'error': 'Could not process amount column'}
        
        # Check date format
        if 'date' in self.df.columns:
            try:
                dates = pd.to_datetime(self.df['date'], errors='coerce')
                invalid_dates = dates.isnull().sum()
                accuracy['date'] = {
                    'invalid_count': int(invalid_dates),
                    'percentage': round((invalid_dates / len(self.df)) * 100, 2)
                }
            except:
                accuracy['date'] = {'error': 'Could not process date column'}
        
        self.checks_results['accuracy'] = accuracy
        return accuracy
    
    def check_consistency(self):
        """Check data consistency (valid categories, formats)"""
        logger.info("Checking data consistency...")
        
        consistency = {}
        
        # Check status values
        if 'status' in self.df.columns:
            valid_statuses = ['pending', 'approved', 'rejected', 'completed', 'on_hold']
            invalid_status = ~self.df['status'].isin(valid_statuses)
            consistency['status'] = {
                'invalid_count': int(invalid_status.sum()),
                'percentage': round((invalid_status.sum() / len(self.df)) * 100, 2),
                'valid_values': valid_statuses
            }
        
        # Check department consistency
        if 'department' in self.df.columns:
            consistency['departments'] = {
                'unique_count': int(self.df['department'].nunique()),
                'top_5': self.df['department'].value_counts().head(5).to_dict()
            }
        
        self.checks_results['consistency'] = consistency
        return consistency
    
    def check_duplicates(self, subset=None):
        """Check for duplicate records"""
        logger.info("Checking for duplicates...")
        
        if subset is None:
            subset = ['transaction_id']
        
        duplicates = self.df.duplicated(subset=subset).sum()
        
        duplicate_info = {
            'duplicate_count': int(duplicates),
            'percentage': round((duplicates / len(self.df)) * 100, 2) if len(self.df) > 0 else 0,
            'checked_columns': subset
        }
        
        self.checks_results['duplicates'] = duplicate_info
        return duplicate_info
    
    def get_quality_score(self):
        """Calculate overall data quality score (0-100)"""
        logger.info("Calculating data quality score...")
        
        # Run all checks
        completeness = self.check_completeness()
        accuracy = self.check_accuracy()
        consistency = self.check_consistency()
        duplicates = self.check_duplicates()
        
        # Calculate components
        complete_score = 100 - np.mean([v['null_percentage'] for v in completeness.values()])
        
        accuracy_errors = sum([v.get('invalid_count', 0) for v in accuracy.values()])
        accuracy_score = 100 - (accuracy_errors / len(self.df) * 100) if len(self.df) > 0 else 100
        
        duplicate_score = 100 - duplicates['percentage']
        
        # Weighted average
        quality_score = (complete_score * 0.4 + accuracy_score * 0.4 + duplicate_score * 0.2)
        
        return round(quality_score, 2)
    
    def generate_report(self):
        """Generate comprehensive quality report"""
        logger.info("Generating quality report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(self.df),
            'quality_score': self.get_quality_score(),
            'completeness': self.check_completeness(),
            'accuracy': self.check_accuracy(),
            'consistency': self.check_consistency(),
            'duplicates': self.check_duplicates()
        }
        
        return report


class AnomalyDetector:
    """Detect anomalies in financial data"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.anomalies = []
    
    def detect_outliers_zscore(self, column='amount', threshold=3.0):
        """Detect outliers using Z-score method"""
        logger.info(f"Detecting outliers in {column} using Z-score (threshold={threshold})...")
        
        if column not in self.df.columns:
            logger.warning(f"Column {column} not found")
            return []
        
        z_scores = np.abs(stats.zscore(self.df[column].dropna()))
        outlier_indices = np.where(z_scores > threshold)[0]
        
        outliers = []
        for idx in outlier_indices:
            outliers.append({
                'type': 'zscore_outlier',
                'column': column,
                'index': int(idx),
                'value': float(self.df[column].iloc[idx]),
                'z_score': float(z_scores[idx]),
                'threshold': threshold
            })
        
        logger.info(f"Found {len(outliers)} outliers using Z-score")
        self.anomalies.extend(outliers)
        return outliers
    
    def detect_outliers_iqr(self, column='amount'):
        """Detect outliers using IQR method"""
        logger.info(f"Detecting outliers in {column} using IQR method...")
        
        if column not in self.df.columns:
            logger.warning(f"Column {column} not found")
            return []
        
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (self.df[column] < lower_bound) | (self.df[column] > upper_bound)
        outlier_indices = np.where(outlier_mask)[0]
        
        outliers = []
        for idx in outlier_indices:
            outliers.append({
                'type': 'iqr_outlier',
                'column': column,
                'index': int(idx),
                'value': float(self.df[column].iloc[idx]),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            })
        
        logger.info(f"Found {len(outliers)} outliers using IQR")
        self.anomalies.extend(outliers)
        return outliers
    
    def detect_unusual_patterns(self):
        """Detect unusual transaction patterns"""
        logger.info("Detecting unusual transaction patterns...")
        
        patterns = []
        
        # Check for unusual status transitions
        if 'status' in self.df.columns:
            rejected_high_value = (
                (self.df['status'] == 'rejected') & 
                (self.df['amount'] > self.df['amount'].quantile(0.9))
            )
            
            count = rejected_high_value.sum()
            if count > 0:
                patterns.append({
                    'type': 'rejected_high_value',
                    'description': 'High-value transactions being rejected',
                    'count': int(count),
                    'percentage': round((count / len(self.df)) * 100, 2)
                })
        
        # Check for unusual same-day transactions from same account
        if 'date' in self.df.columns and 'account_id' in self.df.columns:
            same_day_txns = self.df.groupby(['date', 'account_id']).size()
            excessive = same_day_txns[same_day_txns > 10]
            
            if len(excessive) > 0:
                patterns.append({
                    'type': 'excessive_daily_transactions',
                    'description': 'Accounts with >10 transactions per day',
                    'count': int(len(excessive)),
                    'max_transactions': int(excessive.max())
                })
        
        self.anomalies.extend(patterns)
        return patterns
    
    def detect_fraud_indicators(self):
        """Detect potential fraud indicators"""
        logger.info("Detecting fraud indicators...")
        
        fraud_indicators = []
        
        # Unusually large amounts
        if 'amount' in self.df.columns:
            threshold = self.df['amount'].quantile(0.99)
            large_txns = (self.df['amount'] > threshold).sum()
            
            if large_txns > 0:
                fraud_indicators.append({
                    'indicator': 'unusually_large_amounts',
                    'count': int(large_txns),
                    'threshold': float(threshold),
                    'percentage': round((large_txns / len(self.df)) * 100, 4)
                })
        
        # Pending transactions older than 30 days
        if 'status' in self.df.columns and 'date' in self.df.columns:
            thirty_days_ago = pd.Timestamp.now() - pd.Timedelta(days=30)
            old_pending = (
                (self.df['status'] == 'pending') & 
                (self.df['date'] < thirty_days_ago)
            ).sum()
            
            if old_pending > 0:
                fraud_indicators.append({
                    'indicator': 'old_pending_transactions',
                    'count': int(old_pending),
                    'threshold_days': 30,
                    'percentage': round((old_pending / len(self.df)) * 100, 2)
                })
        
        self.anomalies.extend(fraud_indicators)
        return fraud_indicators
    
    def get_anomaly_summary(self):
        """Get summary of all detected anomalies"""
        return {
            'total_anomalies': len(self.anomalies),
            'anomalies_by_type': self._group_by_type(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _group_by_type(self):
        """Group anomalies by type"""
        grouped = {}
        for anomaly in self.anomalies:
            anom_type = anomaly.get('type') or anomaly.get('indicator', 'unknown')
            if anom_type not in grouped:
                grouped[anom_type] = 0
            grouped[anom_type] += 1
        return grouped
    
    def detect_all(self):
        """Run all anomaly detection methods"""
        logger.info("Running comprehensive anomaly detection...")
        
        self.detect_outliers_zscore()
        self.detect_outliers_iqr()
        self.detect_unusual_patterns()
        self.detect_fraud_indicators()
        
        return self.get_anomaly_summary()


if __name__ == "__main__":
    logger.info("Data quality and anomaly detection module loaded")
