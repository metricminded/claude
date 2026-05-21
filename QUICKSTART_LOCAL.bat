@echo off
REM Quick Start Script - Run Locally (Windows)
REM Copy and paste this entire script and save as quickstart.bat, then run it

echo ================================================
echo NSE Stock Analyzer - Local Setup (Windows)
echo ================================================
echo.

REM Step 1: Clone Repository
echo 📥 Step 1: Cloning repository...
if exist "claude" (
    echo    ℹ️ 'claude' directory already exists, skipping clone
    cd claude
) else (
    git clone https://github.com/metricminded/claude.git
    cd claude
)

REM Step 2: Checkout Branch
echo.
echo 🔀 Step 2: Checking out branch...
git checkout claude/setup-yfinance-api-2Eksa

REM Step 3: Create Virtual Environment
echo.
echo 🐍 Step 3: Creating virtual environment...
python -m venv venv

REM Step 4: Activate Virtual Environment
echo.
echo ✨ Step 4: Activating virtual environment...
call venv\Scripts\activate.bat

REM Step 5: Install Dependencies
echo.
echo 📦 Step 5: Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Step 6: Create Config File
echo.
echo ⚙️ Step 6: Setting up configuration...
if not exist "config.json" (
    copy config.json.template config.json
    echo    ✓ Created config.json
    echo    ⚠️ Please edit config.json and add your email
) else (
    echo    ✓ config.json already exists
)

REM Step 7: Run Tests
echo.
echo 🧪 Step 7: Running tests...
python test.py

REM Step 8: Get Live Prices
echo.
echo 💹 Step 8: Fetching live NSE prices...
python market_prices.py

echo.
echo ================================================
echo ✅ Setup Complete!
echo ================================================
echo.
echo Next commands to use:
echo.
echo   📊 Get current prices:
echo      python market_prices.py
echo.
echo   📈 Analyze top 3 stocks:
echo      python stock_analyzer.py
echo.
echo   📅 Run daily scheduler:
echo      python scheduler.py
echo.
echo   💌 Send email alerts:
echo      python send_email.py
echo.
echo ================================================
pause
