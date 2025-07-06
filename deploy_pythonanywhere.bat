@echo off
echo 🐍 PythonAnywhere Deployment Instructions
echo.
echo This script provides step-by-step instructions for PythonAnywhere deployment.
echo You'll need to run these commands in your PythonAnywhere bash console.
echo.
echo 1. Go to https://www.pythonanywhere.com and create a free account
echo 2. Open a Bash console in PythonAnywhere
echo 3. Run the following commands:
echo.
echo    git clone https://github.com/faizanshoukat5/AI-Movie-Recommender.git
echo    cd AI-Movie-Recommender
echo    pip3.10 install --user -r requirements.txt
echo.
echo 4. Go to Web tab and create a new web app
echo 5. Choose "Manual configuration" and "Python 3.10"
echo 6. Update the WSGI configuration file (see PYTHONANYWHERE_DEPLOYMENT.md)
echo 7. Replace 'yourusername' with your actual PythonAnywhere username
echo 8. Reload your web app
echo.
echo Your backend will be live at: https://yourusername.pythonanywhere.com
echo.
echo For detailed instructions, see PYTHONANYWHERE_DEPLOYMENT.md
echo.
pause
