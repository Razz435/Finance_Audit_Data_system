# Installation & Troubleshooting Guide

## 🔧 Installation Steps

### Prerequisites
- Windows 10/11 (or any OS with Python)
- Python 3.8 or higher
- ~2GB free disk space for full 1M record dataset

### Step 1: Verify Python Installation
```bash
python --version
```
Should show: `Python 3.x.x` or higher

If not found, install from: https://www.python.org/downloads/

### Step 2: Navigate to Project Directory
```bash
cd c:\Users\rahul\Documents\finance_audit_system
```

### Step 3: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed Flask-2.3.0 pandas-2.0.0 numpy-1.24.0 scipy-1.10.0
```

### Step 5: Verify Installation
```bash
python -c "import pandas; import flask; print('All dependencies installed!')"
```

---

## ✅ Quick Verification

Run the demo to verify everything works:
```bash
python demo.py
```

This will:
- Generate sample data
- Test transformations
- Validate data
- Check quality
- Detect anomalies
- Test database operations
- Show API examples

---

## 🚀 Running the System

### Option 1: Full Automated Pipeline
```bash
python main.py full
```
Time: ~15-20 minutes with 1M records

### Option 2: Quick Test with Sample
```bash
python main.py full --sample
```
Time: ~2-3 minutes with 10K records

### Option 3: Step-by-Step
```bash
# Step 1: Generate data (2-3 min)
python main.py generate --sample

# Step 2: Initialize database (1 sec)
python main.py init-db

# Step 3: Run ETL (depends on data size)
python main.py etl

# Step 4: Quality checks
python main.py quality

# Step 5: Analytics
python main.py analytics

# Step 6: Start API (stays running)
python main.py api
```

### Option 4: Windows Batch Menu (Easiest!)
Double-click: `run.bat`

---

## 🐛 Troubleshooting

### Problem 1: ModuleNotFoundError
**Error**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or manually install
pip install pandas numpy scipy flask
```

---

### Problem 2: Python Not Found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
- Reinstall Python with "Add Python to PATH" checked
- Use full path: `C:\Python3XX\python.exe main.py full`
- Or use: `python3 main.py full`

---

### Problem 3: Database Locked
**Error**: `sqlite3.OperationalError: database is locked`

**Solution**:
```bash
# Option A: Delete and recreate database
del database\finance_audit.db
python main.py full

# Option B: Kill any existing database connections
# Restart your terminal/Python
```

---

### Problem 4: Permission Denied (Logs)
**Error**: `PermissionError: [Errno 13] Permission denied: 'logs/...'`

**Solution**:
```bash
# Run as Administrator
# Right-click cmd.exe -> "Run as administrator"
python main.py full

# Or manually create logs folder
mkdir logs
python main.py full
```

---

### Problem 5: Out of Disk Space
**Error**: `OSError: [Errno 28] No space left on device`

**Solution**:
- Use sample data: `python main.py full --sample` (10K records, 50MB)
- Clean up old files: `del data\raw\*.csv`
- Use external drive for data

---

### Problem 6: API Port Already in Use
**Error**: `OSError: [Errno 10048] Address already in use`

**Solution**:
```bash
# Use different port
python main.py api --port 5001

# Or kill existing process
taskkill /F /IM python.exe
# Then restart
python main.py api
```

---

### Problem 7: Slow Performance
**Symptom**: Taking too long to process data

**Solution**:
```bash
# Use smaller dataset
python main.py full --sample

# Or generate smaller dataset
python main.py generate --records 10000

# Reduce batch size in config.py
ETL_BATCH_SIZE = 5000
```

---

### Problem 8: Memory Issues
**Error**: `MemoryError` or system becomes very slow

**Solution**:
- Close other applications
- Use sample data: `python main.py full --sample`
- Reduce `CHUNK_SIZE` in config.py (default: 50000)
- Process on machine with more RAM

---

### Problem 9: CSV File Not Found
**Error**: `FileNotFoundError: Source file not found`

**Solution**:
```bash
# Generate data first
python main.py generate --sample

# Then run ETL
python main.py etl
```

---

### Problem 10: Flask API Won't Start
**Error**: `RuntimeError: Working outside of request context`

**Solution**:
```bash
# Restart terminal
# Check port is available
python main.py api --port 5000
```

---

## 📊 Expected Output Examples

### After Running `python main.py full --sample`:
```
2024-01-15 10:30:45 - INFO - ============================================================
2024-01-15 10:30:45 - INFO - Starting ETL Pipeline
2024-01-15 10:30:45 - INFO - ============================================================
2024-01-15 10:30:46 - INFO - Connected to database: c:\...\finance_audit.db
2024-01-15 10:30:46 - INFO - Creating database schema...
2024-01-15 10:30:46 - INFO - Database schema created successfully
2024-01-15 10:30:46 - INFO - Extracting data from: c:\...\raw_audit_data.csv
2024-01-15 10:30:46 - INFO - Data extraction completed
2024-01-15 10:30:46 - INFO - Processing chunk 1: 10000 records
2024-01-15 10:30:47 - INFO - Transforming 10000 records...
2024-01-15 10:30:48 - INFO - Transformation completed: 9850 records after cleaning
2024-01-15 10:30:48 - INFO - Loading 9850 records into database...
2024-01-15 10:30:48 - INFO - Loaded 9850 records
============================================================
ETL Pipeline Summary
============================================================
status: completed
total_processed: 9850
failed: 0
successful: 9850
duration_seconds: 2.34
records_per_second: 4209.40
timestamp: 2024-01-15T10:30:49.123456
```

### After Running `python main.py api`:
```
2024-01-15 10:35:20 - INFO - Starting Finance Audit API on 0.0.0.0:5000
WARNING: This is a development server. Do not use it in production.
Press CTRL+C to quit
```

Then visit: `http://localhost:5000/api/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:35:25.123456",
  "service": "Finance Audit System API"
}
```

---

## 🔍 Verifying Installation

### Check 1: Dependency Installation
```bash
python -c "import pandas, numpy, scipy, flask; print('✓ All dependencies installed')"
```

### Check 2: Project Structure
```bash
# Should see these directories
dir database modules etl api logs data
```

### Check 3: Database Creation
```bash
python main.py init-db
# Should see: "Database initialized successfully"
```

### Check 4: Data Generation
```bash
python main.py generate --sample
# Should see: "Sample data generated"
```

### Check 5: API Availability
```bash
python main.py api &
# In another terminal:
curl http://localhost:5000/api/health
```

---

## 📋 System Requirements Checklist

- [ ] Python 3.8+ installed
- [ ] pip available (`pip --version`)
- [ ] 2GB free disk space
- [ ] Administrator access for logs
- [ ] Ports 5000+ available for API

---

## 🔄 Starting Fresh

To completely reset and start over:

```bash
# 1. Delete database
del database\finance_audit.db

# 2. Delete generated data
del data\raw\*.csv

# 3. Delete logs
del logs\*.log

# 4. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 5. Run full pipeline
python main.py full --sample
```

---

## 🎯 Next Steps After Installation

1. **Verify Installation**
   ```bash
   python demo.py
   ```

2. **Generate and Process Data**
   ```bash
   python main.py full --sample
   ```

3. **Start API Server**
   ```bash
   python main.py api
   ```

4. **Test API**
   ```bash
   curl http://localhost:5000/api/statistics/summary
   ```

5. **Review Logs**
   ```bash
   type logs\main.log
   ```

---

## 📞 Getting Help

If you encounter issues:

1. **Check Logs**:
   ```bash
   type logs\main.log
   type logs\database.log
   type logs\api.log
   ```

2. **Review Documentation**:
   - `README.md` - User guide
   - `QUICKSTART.md` - Quick start
   - `ARCHITECTURE.md` - Technical design

3. **Run Demo**:
   ```bash
   python demo.py
   ```

4. **Check Configuration**:
   - Edit `config.py` for settings
   - Verify paths are correct
   - Check database location

---

## 🎓 Learning Resources

### Inside This Project:
- Well-commented code
- Example in `demo.py`
- Comprehensive README
- Architecture documentation

### External Resources:
- Pandas: https://pandas.pydata.org/
- Flask: https://flask.palletsprojects.com/
- SQLite: https://www.sqlite.org/
- NumPy: https://numpy.org/

---

## ✨ Success Indicators

After successful installation, you should see:

✅ No error messages during installation
✅ `python demo.py` completes successfully
✅ API starts without errors
✅ API responds to health check
✅ Database file created
✅ Log files generated

---

**Installation Complete! Ready to process data. 🚀**
