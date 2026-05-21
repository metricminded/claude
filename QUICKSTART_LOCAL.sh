#!/bin/bash
# Quick Start Script - Run Locally
# Copy and paste this entire script to your terminal

echo "================================================"
echo "NSE Stock Analyzer - Local Setup"
echo "================================================"
echo ""

# Step 1: Clone Repository
echo "📥 Step 1: Cloning repository..."
if [ -d "claude" ]; then
    echo "   ℹ️  'claude' directory already exists, skipping clone"
    cd claude
else
    git clone https://github.com/metricminded/claude.git
    cd claude
fi

# Step 2: Checkout Branch
echo ""
echo "🔀 Step 2: Checking out branch..."
git checkout claude/setup-yfinance-api-2Eksa

# Step 3: Create Virtual Environment
echo ""
echo "🐍 Step 3: Creating virtual environment..."
if command -v python3 &> /dev/null; then
    python3 -m venv venv
else
    python -m venv venv
fi

# Step 4: Activate Virtual Environment
echo ""
echo "✨ Step 4: Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Mac/Linux
    source venv/bin/activate
fi

# Step 5: Install Dependencies
echo ""
echo "📦 Step 5: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Create Config File
echo ""
echo "⚙️  Step 6: Setting up configuration..."
if [ ! -f "config.json" ]; then
    cp config.json.template config.json
    echo "   ✓ Created config.json"
    echo "   ⚠️  Please edit config.json and add your email"
else
    echo "   ✓ config.json already exists"
fi

# Step 7: Run Tests
echo ""
echo "🧪 Step 7: Running tests..."
python test.py

# Step 8: Get Live Prices
echo ""
echo "💹 Step 8: Fetching live NSE prices..."
python market_prices.py

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next commands to use:"
echo ""
echo "  📊 Get current prices:"
echo "     python market_prices.py"
echo ""
echo "  📈 Analyze top 3 stocks:"
echo "     python stock_analyzer.py"
echo ""
echo "  📅 Run daily scheduler:"
echo "     python scheduler.py"
echo ""
echo "  💌 Send email alerts:"
echo "     python send_email.py"
echo ""
echo "================================================"
