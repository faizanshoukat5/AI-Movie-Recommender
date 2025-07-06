@echo off
echo Switching to original version...

:: Backup current files
echo Backing up current files...
copy app.py app_current_backup.py > nul 2>&1
copy recommendation-frontend\src\App.js recommendation-frontend\src\App_current_backup.js > nul 2>&1
copy recommendation-frontend\src\App.css recommendation-frontend\src\App_current_backup.css > nul 2>&1
copy recommendation-frontend\src\index.js recommendation-frontend\src\index_current_backup.js > nul 2>&1
copy requirements.txt requirements_current_backup.txt > nul 2>&1

:: Switch to original files
echo Switching to original files...
copy app_original.py app.py > nul 2>&1
copy recommendation-frontend\src\App_original.js recommendation-frontend\src\App.js > nul 2>&1
copy recommendation-frontend\src\App_original.css recommendation-frontend\src\App.css > nul 2>&1
copy recommendation-frontend\src\index_original.js recommendation-frontend\src\index.js > nul 2>&1
copy requirements_original.txt requirements.txt > nul 2>&1

echo Original version activated!
echo.
echo To start the application:
echo 1. Install Python dependencies: pip install -r requirements.txt
echo 2. Start the backend: python app.py
echo 3. In another terminal, go to recommendation-frontend and run: npm start
echo.
echo Your current files have been backed up with '_current_backup' suffix.
pause
