# Quick Start Guide - Finance Audit System

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd c:\Users\rahul\Documents\finance_audit_system
pip install -r requirements.txt
```

### Step 2: Run Full Pipeline (Takes ~15 minutes with 1M records)
```bash
python main.py full
```

**OR** Use sample data for quick testing (5 seconds):
```bash
python main.py full --sample --skip-generation
```

### Step 3: Start API Server
```bash
python main.py api
```

### Step 4: Test API
Open in browser or terminal:
```bash
curl http://localhost:5000/api/health
```

---

## What Each Command Does

| Command | Description | Time |
|---------|-------------|------|
| `python main.py full` | Complete pipeline with 1M records | ~15 min |
| `python main.py full --sample` | Complete pipeline with 10K records | ~2 min |
| `python main.py generate --records 1000000` | Generate 1M records only | ~2 min |
| `python main.py generate --sample` | Generate 10K records | ~5 sec |
| `python main.py init-db` | Create database schema | ~1 sec |
| `python main.py etl` | ETL pipeline (uses existing data) | ~5 min |
| `python main.py quality` | Run quality checks | ~1 min |
| `python main.py analytics` | Generate analytics | ~30 sec |
| `python main.py api` | Start REST API server | continuous |

---

## Output Files

After running:

```
finance_audit_system/
├── database/finance_audit.db      # SQLite database (1GB+ for 1M rows)
├── data/raw/raw_audit_data.csv    # Generated CSV data
├── logs/
│   ├── main.log                   # Main execution log
│   ├── database.log               # Database operations log
│   └── api.log                    # API server log
└── data/processed/                # Processed data (if any)
```

---

## API Quick Reference

### Get All Transactions
```bash
curl http://localhost:5000/api/transactions?limit=10
```

### Get Transactions from Sales Dept
```bash
curl "http://localhost:5000/api/transactions?department=SALES&limit=10"
```

### Get Stats by Department
```bash
curl http://localhost:5000/api/statistics/by-department
```

### Run Quality Check
```bash
curl http://localhost:5000/api/quality/validate
```

### Detect Anomalies
```bash
curl http://localhost:5000/api/quality/anomalies
```

### Get Top Vendors
```bash
curl http://localhost:5000/api/top-vendors?limit=5
```

---

## Project Structure

```
finance_audit_system/          Main project directory
├── config.py                  Configuration settings
├── main.py                    Entry point - run this!
├── requirements.txt           Dependencies
└── database/
    ├── db_manager.py         Database operations
    └── finance_audit.db      SQLite database (created after running)
└── modules/
    ├── data_generator.py     Create synthetic data
    ├── data_transformer.py   Clean & transform data
    └── data_quality.py       Quality checks & anomaly detection
└── etl/
    └── etl_pipeline.py       Complete ETL pipeline
└── api/
    └── api_server.py         Flask REST API
└── logs/                      All logs written here
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError"
**Solution**: 
```bash
pip install -r requirements.txt
```

### Problem: Database locked
**Solution**: Delete `database/finance_audit.db` and restart:
```bash
del database\finance_audit.db
python main.py full
```

### Problem: Slow performance on 1M rows
**Solution**: Use sample data first:
```bash
python main.py full --sample
```

### Problem: Port 5000 already in use
**Solution**: Use different port:
```bash
python main.py api --port 5001
```

---

## Key Metrics

With **1M transactions**:
- Database size: ~800MB-1GB
- Generation time: ~2-3 minutes  
- ETL time: ~5-7 minutes
- Quality checks: ~1-2 minutes
- API response: <500ms average

---

## Next Steps

1. **Explore the data**:
   ```bash
   python main.py api
   # Open http://localhost:5000/api/statistics/summary
   ```

2. **Check logs**:
   ```bash
   type logs\main.log
   ```

3. **Modify configuration** (config.py):
   - Change `TOTAL_RECORDS` for different data sizes
   - Adjust `ETL_BATCH_SIZE` for memory/speed tradeoff
   - Enable/disable caching with `USE_CACHE`

4. **Extend with custom analysis**:
   - Edit `modules/data_transformer.py` for custom transformations
   - Add new API endpoints in `api/api_server.py`
   - Create custom reports using the database

---

## Data Generated

Sample transaction record:
```json
{
  "transaction_id": "TXN_2024_00000001",
  "date": "2023-06-15",
  "amount": 4250.50,
  "account_id": "ACC_5432",
  "department": "SALES",
  "category": "TRAVEL",
  "vendor": "Global Solutions",
  "description": "Travel expense report",
  "status": "approved"
}
```

---

## Database Queries (via API)

Can retrieve:
- ✅ All transactions with filters
- ✅ Specific transaction by ID
- ✅ Total count
- ✅ Statistics by any dimension
- ✅ Top vendors/accounts
- ✅ Quality metrics
- ✅ Anomalies

---

**Happy Data Engineering! 🚀**
