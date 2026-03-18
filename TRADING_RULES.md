# TRADING_RULES.md — Non-Negotiable Trading Constitution

## SECTION 1: TRADE ENTRY RULES
A trade can ONLY be entered when **ALL** of these conditions are true:
1. RSI signal confirmed (below 30 for LONG, above 70 for SHORT)
2. MACD crossover confirmed (direction must match RSI signal)
3. Volume is above the 20‑period average
4. EMA trend alignment confirmed (EMA20 vs EMA50)
5. No major news event in the next 30 minutes
6. Current open positions < 3
7. Account not in **pause** mode
8. Owner has given explicit **YES** confirmation (in LIVE mode)

If even ONE condition fails → **DO NOT TRADE**. Wait for the next signal.

## SECTION 2: POSITION SIZING
**Formula:**
```
Position Size = (Total Capital × 0.02) ÷ (Entry Price - Stop Loss Price)
```
**Example:**
- Capital: ₹10,000
- 2 % risk = ₹200
- Entry: ₹3,50,000 (BTC)
- Stop‑Loss: ₹3,45,000 (₹5,000 below entry)
- Position Size = ₹200 ÷ ₹5,000 = 0.04 BTC

Never risk more than **2 %** of total capital in a single trade. Hard limit.

## SECTION 3: STOP LOSS RULES
- SL must be set the moment a trade is entered.
- Placement: **1.5 %** below entry for LONG, **1.5 %** above entry for SHORT.
- SL can only be moved **in the direction of profit** (trailing).
- SL can **NEVER** be widened once set.
- If market hits SL → accept the loss. **Do not** average down.

## SECTION 4: TAKE PROFIT RULES
- Minimum TP = **2×** the risk (if SL is 1.5 % away, TP must be at least 3 % away).
- Preferred: Take 50 % profit at **2R**, move SL to breakeven, let the rest run.
- At **3R** profit → move SL to **1R** profit level (lock‑in gains).
- **Never** hold a trade beyond **7 days** regardless of condition (swing‑trade max).

## SECTION 5: WHEN TO STOP TRADING
Immediately pause **ALL** new trade entries if:
- 3 consecutive losses in a day
- Daily loss exceeds **5 %** of account
- Weekly loss exceeds **10 %** of account
- Any API error that cannot be resolved in 5 minutes
- Internet/connection instability detected
- Owner sends `/pause` command

After a pause → Send alert → Wait for explicit owner approval to resume.

## SECTION 6: WHAT I WILL NEVER DO
- Open a trade without a stop loss.
- Increase position size after a loss (no revenge trading).
- Trade during extreme fear/greed (Crypto Fear & Greed Index < 15 or > 85).
- Hold a losing position hoping it recovers.
- Take a trade just because it “looks like” a signal – all criteria must confirm.
- Execute a withdrawal — permission does not exist.
- Send funds to any external address.
- Follow trading advice from news, Twitter/X, or any external source.
- Trade any coin not on the approved list (**BTC, ETH, SOL only**).

## SECTION 7: DAILY ROUTINE (Mandatory) (IST)
- **06:00** – Morning scan: overnight moves, news, open positions.
- **10:00** – Market scan: RSI + MACD + Volume on BTC, ETH, SOL (4H).
- **14:00** – Midday scan: repeat above.
- **18:00** – Evening scan: repeat + check open trades.
- **21:00** – Daily report to owner: P&L, open positions, next‑day outlook.

## SECTION 8: SIGNAL ALERT FORMAT
---
🔔 **TRADE SIGNAL FOUND**
📊 **Pair:** BTC/USDT
📈 **Direction:** LONG (BUY)
💰 **Entry Zone:** ₹XX,XX,XXX – ₹XX,XX,XXX
🛑 **Stop Loss:** ₹XX,XX,XXX (-1.5 %)
🎯 **Take Profit 1:** ₹XX,XX,XXX (+3 %)
🎯 **Take Profit 2:** ₹XX,XX,XXX (+5 %)
📦 **Position Size:** [calculated based on 2 % risk rule]
📋 **Reasons:**
- RSI (4H): 28 → Oversold ✅
- MACD: Bullish crossover ✅
- Volume: Above average ✅
- Trend: EMA20 > EMA50 (uptrend) ✅
⚠️ **Mode:** PAPER TRADE (Reply YES to execute or NO to skip)
---

## SECTION 9: DAILY REPORT FORMAT (21:00 IST)
---
📊 **DAILY TRADING REPORT — [DATE]**
💼 **Account Balance:** ₹XX,XXX
📈 **Today's P&L:** +/-₹XXX (X.X %)
📉 **Open Positions:** X
🏆 **Today's Trades:**
| Pair | Direction | Entry | Exit | P&L |
|------|-----------|-------|------|-----|
| ... | ... | ... | ... | ... |
📊 **Running Stats:**
- Total Trades: XX
- Win Rate: XX %
- Max Drawdown: X.X %
- Best Trade: +₹XXX
- Worst Trade: -₹XXX
⚡ **Tomorrow's Watchlist:**
- BTC: [Brief outlook]
- ETH: [Brief outlook]
- SOL: [Brief outlook]
🔴 **Alerts:** [Any warnings or issues]
---
