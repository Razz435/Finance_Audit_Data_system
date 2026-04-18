@echo off
REM Finance Audit System - Windows Batch Helper Scripts
REM Use these shortcuts to run commands easily

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Finance Audit System - Quick Commands                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 1. Run Full Pipeline (1M records)
echo 2. Run Full Pipeline with Sample Data (10K records)
echo 3. Generate Data Only
echo 4. Initialize Database
echo 5. Run ETL Pipeline
echo 6. Run Quality Checks
echo 7. Run Analytics
echo 8. Start API Server
echo 9. Run Demo
echo 10. Install Dependencies
echo 11. View Logs
echo 0. Exit
echo.
set /p choice="Enter your choice (0-11): "

if "%choice%"=="1" goto full_pipeline
if "%choice%"=="2" goto full_sample
if "%choice%"=="3" goto generate
if "%choice%"=="4" goto init_db
if "%choice%"=="5" goto etl
if "%choice%"=="6" goto quality
if "%choice%"=="7" goto analytics
if "%choice%"=="8" goto api
if "%choice%"=="9" goto demo
if "%choice%"=="10" goto install
if "%choice%"=="11" goto logs
if "%choice%"=="0" goto end

echo Invalid choice!
timeout /t 3
goto menu

:full_pipeline
echo.
echo Running full pipeline with 1M records...
echo This will take approximately 15-20 minutes
echo.
python main.py full
pause
goto menu

:full_sample
echo.
echo Running full pipeline with sample data (10K records)...
echo This will take approximately 2 minutes
echo.
python main.py full --sample --skip-generation
pause
goto menu

:generate
echo.
echo Generating data...
python main.py generate --records 1000000
pause
goto menu

:init_db
echo.
echo Initializing database...
python main.py init-db
pause
goto menu

:etl
echo.
echo Running ETL pipeline...
python main.py etl
pause
goto menu

:quality
echo.
echo Running quality checks...
python main.py quality
pause
goto menu

:analytics
echo.
echo Generating analytics...
python main.py analytics
pause
goto menu

:api
echo.
echo Starting API server...
echo.
echo API will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python main.py api
pause
goto menu

:demo
echo.
echo Running demo...
python demo.py
pause
goto menu

:install
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Installation complete!
pause
goto menu

:logs
echo.
echo Recent logs:
echo.
echo === Main Log ===
type logs\main.log | tail -20
echo.
echo === Database Log ===
type logs\database.log | tail -10
echo.
pause
goto menu

:end
echo.
echo Goodbye!
exit /b 0
