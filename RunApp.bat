@echo off
cd /d "%~dp0"

echo Checking for Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Opening download page...
    start https://www.python.org/downloads/
    echo Please install Python, tick "Add Python to PATH", then run this file again.
    pause
    exit
)

echo Checking dependencies...
py -m pip show streamlit yfinance pandas plotly requests >nul 2>&1
if errorlevel 1 (
    echo Some dependencies are missing.
    echo.
    set /p answer="Would you like to install them now? (y/n): "
    if /i "%answer%"=="y" (
        echo Installing, this will take a minute...
        py -m pip install -r requirements.txt --quiet
        echo Done!
    ) else (
        echo Dependencies are required to run the app. Exiting.
        pause
        exit
    )
) else (
    echo All dependencies already installed!
)

echo Launching app...
py -m streamlit run app.py
pause