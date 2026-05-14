# Quick Start Guide

Get your morning stock alerts running in 5 minutes.

## Step 1: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

## Step 2: Get Gmail App Password (2 minutes)

1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication (if not done)
3. Click "App passwords"
4. Select **Mail** and your device
5. Copy the 16-character password Google generates

## Step 3: Configure (1 minute)

```bash
cp config.json.template config.json
```

Edit `config.json` and replace:
- `your-email@gmail.com` → Your Gmail address
- `your-app-password` → The 16-character password from Step 2

```json
{
  "email": {
    "sender": "your-email@gmail.com",          # ← Update this
    "password": "your-16-char-app-password",   # ← Update this
    "recipient": "your-email@gmail.com"        # ← Update this
  }
}
```

## Step 4: Test (30 seconds)

```bash
python test.py
```

This tests imports, config, and runs analyzer on 5 stocks. Should take ~30 seconds.

## Step 5: Run (Start now)

```bash
python scheduler.py
```

That's it! The scheduler will:
- Run at 9:00 AM IST daily
- Email you the top 3 stocks
- Keep running in background

## To Run in Background

### On Linux/Mac:
```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

Check status anytime:
```bash
tail -f scheduler.log
```

### On Windows:
Use Task Scheduler to run `scheduler.py` at startup.

---

## What You'll Get Each Morning

Email with:
- 📊 Stock symbol & price
- 🎯 Technical score (0-7)
- 📈 Why to buy (RSI, MACD, Volume, etc.)
- ⚠️ Risk disclaimer

## Need Help?

1. **Email not working?** Check password is 16 characters (not your Gmail password)
2. **No stocks found?** Check internet connection, run `python stock_analyzer.py`
3. **Scheduler issues?** Check `stock_analyzer.log` for errors

## Important

⚠️ **This is NOT financial advice**
- Do your own research
- Use stop losses
- Never risk more than you can afford
- Intraday trading is risky

---

Enjoy your daily stock alerts! 📈
