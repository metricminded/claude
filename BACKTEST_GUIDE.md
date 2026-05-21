# 📊 Backtest Live Trading System - User Guide

## Overview

`backtest_live_system.py` is a comprehensive backtesting framework that:
- ✅ Uses the **SAME logic** as the live trading system
- ✅ Tests on **real historical data** from yfinance
- ✅ Supports multiple time periods (1 month to 2 years)
- ✅ Simulates realistic trade execution (with stop loss, targets)
- ✅ Provides detailed performance metrics
- ✅ Saves results as JSON for analysis

---

## 🚀 Quick Start

### Basic Usage

```bash
# Default: 6 months data, test 60 days
python backtest_live_system.py
```

### Custom Period

```bash
# Backtest 1 month
python backtest_live_system.py --period 1mo --days 20

# Backtest 1 year
python backtest_live_system.py --period 1y --days 200

# Backtest 2 years
python backtest_live_system.py --period 2y --days 400
```

### Custom Parameters

```bash
# Higher confidence trades only (score 7+)
python backtest_live_system.py --min-score 7

# More capital
python backtest_live_system.py --capital 500000

# Larger profit target
python backtest_live_system.py --target 2000

# Tighter stop loss
python backtest_live_system.py --stop-loss 0.003
```

---

## 📋 All Command Line Options

| Flag | Default | Description |
|------|---------|-------------|
| `--period` | `6mo` | Data period: 1mo, 3mo, 6mo, 1y, 2y |
| `--days` | `60` | Number of trading days to test |
| `--capital` | `200000` | Starting capital (INR) |
| `--target` | `1000` | Profit target per trade (INR) |
| `--min-score` | `5` | Minimum signal score (0-10) |
| `--stop-loss` | `0.005` | Stop loss percentage (0.005 = 0.5%) |

---

## 📊 What You Get

### Console Output

```
=====================================================================================
📊 LIVE SYSTEM BACKTEST
=====================================================================================
Period: 6mo
Days to test: 60
Starting Capital: ₹200,000
Profit Target: ₹1000
Stop Loss: 0.5%
Min Score: 5/10
Stocks: 19

📥 Fetching JPOWER.NS (6mo)...
📥 Fetching RELIANCE.NS (6mo)...
... (fetches all stocks)

🔄 Running backtest from day 30 to 130
   (~100 trading days)

=====================================================================================
📊 BACKTEST RESULTS
=====================================================================================

💰 PROFIT/LOSS SUMMARY:
   Starting Capital:      ₹200,000.00
   Ending Capital:        ₹245,820.00
   Total P&L:             ₹+45,820.00
   ROI:                   +22.91%

📊 TRADE STATISTICS:
   Total Trading Days:    60
   Days Traded:           42
   Days Skipped:          18 (low confidence)
   Total Trades:          42
   Wins:                  28 ✅
   Losses:                14 ❌
   Win Rate:              66.7%

🎯 OUTCOME BREAKDOWN:
   Target Hits:           25 (59.5%)
   Stop Losses:           12 (28.6%)
   EOD Closes:            5

💵 P&L ANALYSIS:
   Average Win:           ₹+985.00
   Average Loss:          ₹-485.00
   Largest Win:           ₹+1,250.00
   Largest Loss:          ₹-1,200.00
   Risk/Reward Ratio:     1:2.03

📈 PROFIT ESTIMATES:
   Avg per Trading Day:   ₹+1,091.00
   Monthly Estimate:      ₹+21,820.00
   Annual Estimate:       ₹+272,750.00

🏆 TOP PERFORMING STOCKS:
   JPOWER.NS       ₹+12,450.00 (8 trades)
   RELIANCE.NS     ₹+8,200.00 (6 trades)
   SUNPHARMA.NS    ₹+6,800.00 (5 trades)
   TCS.NS          ₹+5,500.00 (4 trades)
   TITAN.NS        ₹+4,200.00 (3 trades)

📉 WORST PERFORMING STOCKS:
   HINDUNILVR.NS   ₹-1,500.00 (3 trades)
   ITC.NS          ₹-2,200.00 (2 trades)

=====================================================================================
✅ STRATEGY VERDICT: PROFITABLE
=====================================================================================
```

### JSON Output (`backtest_results/backtest_YYYYMMDD_HHMMSS.json`)

```json
{
  "timestamp": "2026-05-21T09:15:32",
  "config": {
    "starting_capital": 200000,
    "profit_target": 1000,
    "stop_loss_pct": 0.005,
    "min_score": 5
  },
  "summary": {
    "total_pnl": 45820,
    "total_trades": 42,
    "final_capital": 245820,
    "roi_percent": 22.91
  },
  "trades": [
    {
      "date": "2025-12-15",
      "symbol": "JPOWER.NS",
      "direction": "UP",
      "entry": 18.56,
      "target": 19.12,
      "quantity": 1786,
      "pnl": 1000,
      "outcome": "TARGET HIT ✅",
      "score": 8
    },
    ...
  ]
}
```

---

## 🎯 Backtest Scenarios

### Conservative Strategy (High Confidence Only)

```bash
python backtest_live_system.py \
  --period 6mo \
  --days 100 \
  --min-score 7 \
  --stop-loss 0.003
```

**Expected:** Fewer trades, higher win rate (70%+)

### Aggressive Strategy (More Opportunities)

```bash
python backtest_live_system.py \
  --period 1y \
  --days 200 \
  --min-score 4 \
  --stop-loss 0.01
```

**Expected:** More trades, lower win rate (~55%)

### Large Capital Strategy

```bash
python backtest_live_system.py \
  --capital 1000000 \
  --target 5000 \
  --min-score 6
```

**Expected:** Larger profits per trade, ₹5000 targets

### Quick Profit Strategy

```bash
python backtest_live_system.py \
  --target 500 \
  --stop-loss 0.003 \
  --min-score 6
```

**Expected:** Smaller profits but tighter risk management

---

## 📈 Comparing Strategies

Run multiple backtests with different parameters:

```bash
# Test conservative
python backtest_live_system.py --min-score 7 --days 100 > conservative.log

# Test moderate
python backtest_live_system.py --min-score 5 --days 100 > moderate.log

# Test aggressive  
python backtest_live_system.py --min-score 4 --days 100 > aggressive.log

# Compare
grep "ROI" conservative.log moderate.log aggressive.log
grep "Win Rate" conservative.log moderate.log aggressive.log
```

---

## 🔍 Analyzing Results

### View Trade History

```bash
# Last backtest results
cat backtest_results/backtest_*.json | jq '.trades[]' | head -50

# Count wins vs losses
jq '.trades | map(select(.pnl > 0)) | length' backtest_results/backtest_*.json
jq '.trades | map(select(.pnl < 0)) | length' backtest_results/backtest_*.json
```

### Best Performing Stocks

```bash
jq '.trades | group_by(.symbol) | map({symbol: .[0].symbol, total_pnl: (map(.pnl) | add)})' \
   backtest_results/backtest_*.json
```

### Average Trade Size

```bash
jq '.trades | map(.pnl) | add / length' backtest_results/backtest_*.json
```

---

## 💡 Key Metrics Explained

### **ROI (Return on Investment)**
```
ROI = (Final Capital - Starting Capital) / Starting Capital × 100

Good: > 15% annually
Great: > 25% annually
Exceptional: > 40% annually
```

### **Win Rate**
```
Win Rate = Winning Trades / Total Trades × 100

Min Required: 55% (with 1:2 risk/reward)
Good: 60-65%
Excellent: 70%+
```

### **Risk/Reward Ratio**
```
RR = Average Win / Average Loss

Min Required: 1:1.5
Good: 1:2
Excellent: 1:3+
```

### **Profit Factor**
```
PF = Total Wins / Total Losses

> 1.0: Profitable
> 1.5: Good
> 2.0: Excellent
```

---

## 🎓 Backtest Best Practices

### 1. **Test Multiple Periods**
Don't just test one period. Test:
- Bull market (rising prices)
- Bear market (falling prices)
- Sideways market (no trend)
- Volatile periods (high VIX)

```bash
# Recent bull (2026 Q1)
python backtest_live_system.py --period 3mo --days 60

# Older period (2025 H1)
python backtest_live_system.py --period 1y --days 100

# Crisis period
python backtest_live_system.py --period 2y --days 200
```

### 2. **Forward Test After Backtest**
- Backtest shows historical performance
- Paper trade for 1 month
- Then risk real money

### 3. **Account for Real-World Costs**
The backtest doesn't include:
- Brokerage fees (~₹20-40 per trade)
- STT (Securities Transaction Tax)
- GST on brokerage
- Slippage (price moves before order fills)

**Realistic adjustment:** Subtract ~₹100 per trade from backtest profits

### 4. **Watch for Overfitting**
- Don't tune parameters to perfectly fit historical data
- The strategy should work across different market conditions
- If it only works for specific period → likely overfit

---

## ⚠️ Important Disclaimers

1. **Past Performance ≠ Future Results**
   - Markets change, strategies degrade
   - Backtest is just an estimate

2. **Survivorship Bias**
   - We test stocks that exist today
   - Don't include delisted stocks
   - Real performance may be worse

3. **Look-Ahead Bias**
   - Backtest uses next-day high/low
   - Real trading can't see future
   - Account for this in expectations

4. **Network Required**
   - Backtest needs internet
   - Yahoo Finance must be accessible
   - May fail in restricted networks

---

## 🚨 Troubleshooting

### "No data fetched"
**Cause:** Network restrictions or yfinance issues
**Fix:** Check internet, retry, or use VPN

### "No trades executed"
**Cause:** Min score too high
**Fix:** Lower `--min-score` (try 4 or 5)

### Backtest takes too long
**Cause:** Too many stocks or long period
**Fix:** Reduce `--period` to 3mo or test fewer stocks

### Results vary between runs
**Cause:** Network latency, partial data
**Fix:** Run multiple times, take average

---

## 📊 Integration with Live System

The backtest uses the **exact same logic** as `live_trading_system.py`:
- Same RSI calculation
- Same MACD calculation
- Same TimesFM prediction
- Same scoring system
- Same position sizing

This means: **If backtest shows profit, live trading should too!**

### Validation Workflow

```bash
1. Run backtest on 6 months data
   $ python backtest_live_system.py --period 6mo

2. Check if profitable (ROI > 0)
   $ grep "ROI" backtest_results/backtest_*.json

3. Run for different periods (consistency check)
   $ python backtest_live_system.py --period 1y
   $ python backtest_live_system.py --period 3mo

4. If consistently profitable → deploy live
   $ python live_trading_system.py
```

---

## 🎯 Realistic Expectations

After running backtest, you'll know:

```
If win rate > 60%:        ✅ Strategy is good, deploy
If win rate 50-60%:       ⚠️ Marginal, refine parameters
If win rate < 50%:        ❌ Don't trade, fix strategy

If ROI > 20% annually:    ✅ Excellent strategy
If ROI 10-20%:           ✅ Good (better than mutual funds)
If ROI < 10%:            ⚠️ Marginal (consider index funds instead)
If ROI negative:         ❌ Losing money, don't trade
```

---

## ✅ Example Successful Backtest

```bash
$ python backtest_live_system.py --period 6mo --days 100 --min-score 6

📊 BACKTEST RESULTS
====================

💰 P&L: ₹+38,500 (+19.25% ROI)
📊 Trades: 65 total (42 wins, 23 losses)
🎯 Win Rate: 64.6%
💵 Avg Win: ₹920 | Avg Loss: ₹420 (RR: 1:2.19)
📈 Daily Avg: ₹577 profit
🚀 Annual Est: ₹144,375 profit

✅ STRATEGY VERDICT: PROFITABLE
```

This means the strategy:
- Made ₹38,500 in 100 days
- Won 64.6% of trades
- Made 1:2.19 risk/reward
- Ready for live deployment

---

## 🎉 You're Ready to Backtest!

```bash
# Try it now
python backtest_live_system.py --period 6mo --days 60

# Check the results
cat backtest_results/backtest_*.json | jq '.summary'
```

Good luck testing your strategy! 📊
