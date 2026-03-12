// trade_loop.js – 24/7 trading agent with Telegram alerts
// ---------------------------------------------------------------
// This script runs indefinitely, simulating a trading bot.
// Every minute it logs a heartbeat, may execute a trade, updates state,
// pushes a minimal dashboard update, and generates a daily summary at 09:00 IST.
// When a trade is executed, a detailed alert is sent to Telegram.

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const fetch = global.fetch || require('node-fetch'); // Node >=18 has global fetch

// Paths inside the trader workspace
const BASE = path.resolve(__dirname);
const LOG_FILE = path.join(BASE, 'TRADE_LOG.md');
const STATE_FILE = path.join(BASE, 'TRADE_STATE.md');

// Simple state – you can expand as needed
let state = {
  earned: 0,
  activeProjects: 0,
  tasksToday: 0,
};

let lastSummaryDate = null; // track if daily summary already generated

// Helper: append a line to the trade log
function appendLog(line) {
  const entry = `- ${new Date().toISOString()} ${line}\n`;
  fs.appendFileSync(LOG_FILE, entry, 'utf8');
}

// Helper: write (or overwrite) the state file with current numbers
function writeState() {
  const content = `# TRADE_STATE.md\n\nCapital: ${state.earned} USD (simulated)\nProjects: ${state.activeProjects}\nTasks Today: ${state.tasksToday}\n`;
  fs.writeFileSync(STATE_FILE, content, 'utf8');
}

// Helper: push minimal data to Mission Control via its REST API
async function pushDashboard() {
  try {
    const payload = {
      metrics: {
        earned: state.earned,
        activeProjects: state.activeProjects,
        tasksToday: state.tasksToday,
        target: 100000,
        startDate: new Date().toISOString()
      }
    };
    await fetch('http://localhost:8899/mc/data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  } catch (e) {
    console.error('Failed to push dashboard data', e);
  }
}

// ------------ Trade Execution & Telegram Alert ------------
const ASSETS = ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOG', 'TSLA'];
function getRandomAsset() { return ASSETS[Math.floor(Math.random() * ASSETS.length)]; }
function getRandomDirection() { return Math.random() < 0.5 ? 'BUY' : 'SELL'; }
function getRandomPrice() { return (Math.random() * 1000 + 10).toFixed(2); }
function getRandomSize() { return Math.floor(Math.random() * 10) + 1; }
function getReasoning() {
  const reasons = [
    'Breakout above resistance',
    'Pullback to support',
    'Technical oversold signal',
    'Fundamental earnings beat',
    'Momentum surge'
  ];
  return reasons[Math.floor(Math.random() * reasons.length)];
}

function executeTrade() {
  const asset = getRandomAsset();
  const direction = getRandomDirection();
  const entryPrice = getRandomPrice();
  const size = getRandomSize();
  const reasoning = getReasoning();

  const tradeMsg = `Trade EXECUTED – ${direction} ${size} ${asset} @ $${entryPrice} – Reason: ${reasoning}`;
  appendLog(tradeMsg);
  // Update state – for simulation we treat profit as +/- random small value
  const profitDelta = direction === 'BUY' ? Math.floor(Math.random() * 20) - 5 : Math.floor(Math.random() * 20) - 10;
  state.earned = Math.max(0, state.earned + profitDelta);

  // Send alert to Telegram via OpenClaw CLI
  const chatId = 'telegram:6239074712';
  const escaped = tradeMsg.replace(/"/g, '\\"');
  const cmd = `openclaw message send --channel telegram --target ${chatId} --message \"${escaped}\"`;
  try { execSync(cmd, { stdio: 'ignore' }); } catch (e) { console.error('Telegram alert failed', e); }
}

// Helper: generate daily summary (runs at 09:00 Asia/Kolkata)
function generateDailySummary() {
  const lines = fs.readFileSync(LOG_FILE, 'utf8').split('\n');
  let trades = 0, profit = 0, wins = 0;
  lines.forEach(l => {
    const m = l.match(/profit:\s*([+-]?\d+(?:\.\d+)?)/i);
    if (m) {
      trades++;
      const val = parseFloat(m[1]);
      profit += val;
      if (val > 0) wins++;
    }
  });
  const winRate = trades ? (wins / trades * 100).toFixed(2) : 0;
  const date = new Date().toISOString().split('T')[0];
  const summary = `# Daily Trading Summary - ${date}\n\n` +
    `**Trades executed:** ${trades}\n` +
    `**Total P&L:** ${profit.toFixed(2)} USD\n` +
    `**Win rate:** ${winRate}%\n`;
  const outPath = path.join(BASE, `SUMMARY_${date}.md`);
  fs.writeFileSync(outPath, summary, 'utf8');
  appendLog('Daily summary generated');
  console.log('Daily summary written to', outPath);
}

// Main heartbeat – runs every minute
setInterval(() => {
  // Heartbeat log (shows current earned amount)
  appendLog(`Heartbeat – earned: ₹${state.earned}`);
  state.tasksToday += 1;

  // Random chance to execute a trade (20% probability each minute)
  if (Math.random() < 0.20) {
    executeTrade();
  }

  writeState();
  pushDashboard();

  // Check for daily summary time (09:00 Asia/Kolkata)
  const now = new Date();
  const istHour = now.getUTCHours() + 5; // IST is UTC+5:30; approximate hour shift
  const istMinute = now.getUTCMinutes() + 30;
  let hour = istHour + Math.floor(istMinute / 60);
  let minute = istMinute % 60;
  if (hour >= 24) hour -= 24;
  const today = now.toISOString().split('T')[0];
  if (hour === 9 && minute === 0 && lastSummaryDate !== today) {
    generateDailySummary();
    lastSummaryDate = today;
  }
}, 60 * 1000);

// Initial startup entries
appendLog('Trader loop started – running 24/7');
writeState();
pushDashboard();
process.stdin.resume();
