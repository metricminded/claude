# Quick Start Guide

Get your morning stock alerts running in 5 minutes.

## Step 1: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

## Step 2: Configure (1 minute)

```bash
cp config.json.template config.json
```

Edit `config.json`:
```json
{
  "email": {
    "recipient": "your-email@gmail.com"   # ← Update this only
  }
}
```

That's it! Uses Gmail MCP connector (no passwords needed).

## Step 3: Test (30 seconds)

```bash
python test.py
```

This tests imports, config, and runs analyzer on 5 stocks.

## Step 4: Run (Start now)

```bash
python scheduler.py
```

The scheduler will run at 9:00 AM IST daily and prepare emails.

## Step 5: Send Email Alert

After scheduler runs, send the prepared email:

```bash
python send_email.py
```

This gives you the email data to send via Gmail MCP `create_draft` tool.

## To Run in Background

### On Linux/Mac:
```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

Check status:
```bash
tail -f scheduler.log
```

### On Windows:
Use Task Scheduler to run `scheduler.py` at startup.

---

## What You'll Get Each Day

Email with:
- 📊 Stock symbol & price
- 🎯 Technical score (0-7)
- 📈 Why to buy (RSI, MACD, Volume signals)
- ⚠️ Risk disclaimer

## Need Help?

1. **Email not prepared?** Run `python stock_analyzer.py` to test
2. **No stocks found?** Check internet connection, Yahoo Finance might be down
3. **Scheduler issues?** Check `stock_analyzer.log` for errors
4. **Send email?** Run `python send_email.py` to see the prepared email

## Important

⚠️ **This is NOT financial advice**
- Do your own research
- Use stop losses
- Never risk more than you can afford
- Intraday trading is risky

---

Enjoy your daily stock alerts! 📈
