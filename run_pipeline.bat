@echo off
cd /d C:\Users\kajet\OneDrive\Pulpit\AIAssetSupport

echo Task started at %date% %time% >> logs\scheduler_test.log

C:\Users\kajet\OneDrive\Pulpit\AIAssetSupport\.venv\Scripts\python.exe framework\run_daily_pipeline.py >> logs\scheduler_output.log 2>&1

echo Task finished at %date% %time% with exit code %ERRORLEVEL% >> logs\scheduler_test.log

exit /b %ERRORLEVEL%