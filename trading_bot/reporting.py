"""Reporting module.
Generates daily performance reports in JSON and markdown format.
"""
import json
import os
from datetime import datetime
from typing import Dict

REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

def generate_daily_report(portfolio_summary: Dict, trades: list, date: str = None):
    if date is None:
        date = datetime.utcnow().strftime('%Y-%m-%d')
    report = {
        'date': date,
        'account_balance': portfolio_summary.get('account_balance'),
        'realized_pnl': portfolio_summary.get('realized_pnl'),
        'unrealized_pnl': portfolio_summary.get('unrealized_pnl'),
        'max_drawdown': portfolio_summary.get('max_drawdown'),
        'trade_count': portfolio_summary.get('trade_count'),
        'win_rate': portfolio_summary.get('win_rate'),
        'open_positions': portfolio_summary.get('open_positions'),
        'trades': trades,
    }
    json_path = os.path.join(REPORT_DIR, f"daily_report_{date}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    # Markdown version
    md_path = os.path.join(REPORT_DIR, f"DAILY_REPORT_{date}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Daily Trading Report – {date}\n\n")
        f.write(f"**Account Balance:** ${report['account_balance']:.2f}\n\n")
        f.write(f"**Realized P&L:** ${report['realized_pnl']:.2f}\n\n")
        f.write(f"**Unrealized P&L:** ${report['unrealized_pnl']:.2f}\n\n")
        f.write(f"**Max Drawdown:** {report['max_drawdown']*100:.2f}%\n\n")
        f.write(f"**Trade Count:** {report['trade_count']}\n\n")
        f.write(f"**Win Rate:** {report['win_rate']:.2f}%\n\n")
        f.write("## Trades Summary\n\n")
        for t in trades[-10:]:  # last 10 trades
            f.write(f"- {t.get('timestamp','')} {t.get('side','').upper()} {t.get('size','')} {t.get('symbol','')} @ ${t.get('entry_price',''):.2f} – P&L ${t.get('pnl',0):.2f}\n")
    return json_path, md_path
