const fs = require('fs');
const path = require('path');

// File paths
const workspaceFile = path.resolve(__dirname, 'team_c_workspace.md');
const masterFile = path.resolve(__dirname, '..', '..', 'master_trading_battle.json');

let cumulativePnL = 0;
let virtualBalance = 500;
let active = false;
let trade = null;

function writeWorkspace(line) {
  fs.appendFileSync(workspaceFile, line + '\n');
}

function readMaster() {
  try { return JSON.parse(fs.readFileSync(masterFile, 'utf8')); } catch(e) { return []; }
}

function getTimestamp(){
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth()+1).padStart(2,'0');
  const dd = String(d.getDate()).padStart(2,'0');
  const hh = String(d.getHours()).padStart(2,'0');
  const min = String(d.getMinutes()).padStart(2,'0');
  const ss = String(d.getSeconds()).padStart(2,'0');
  return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`;
}
function writeMaster(entry) {
  // Append entry as JSONL line with standardized fields
  entry.timestamp = getTimestamp();
  entry.team = 'Team_C';
  entry.strategy = 'MeanReversion';
  const line = JSON.stringify(entry);
  fs.appendFileSync(masterFile, line + '\n', 'utf8');
}

// --- SCOUT: simulate deviation signal ---
function scout() {
  // 30% chance to get a deviation
  if (Math.random() < 0.3) {
    const type = Math.random() < 0.5 ? 'OVEREXTENDED_UP' : 'OVEREXTENDED_DOWN';
    const price = (Math.random() * 990 + 10).toFixed(2);
    writeWorkspace(`DEVIATION_SIGNAL: ${type} @ $${price}`);
    return {type, price: parseFloat(price)};
  }
  return null;
}

// --- SNIPER: decide execution ---
function sniper(signal) {
  if (!signal) return null;
  const exec = signal.type === 'OVEREXTENDED_UP' ? 'SELL' : 'BUY';
  writeWorkspace(`EXECUTE_REVERSION: ${exec}`);
  return {exec, price: signal.price};
}

// --- SCRIBE: execute and monitor ---
function scribe(exec) {
  if (!exec) return;
  active = true;
  trade = {direction: exec.exec, entry: exec.price, entryTime: new Date().toISOString()};
  // Log start in master
  writeMaster({
    timestamp: new Date().toISOString(),
    team: 'Team_C',
    strategy: 'MeanReversion',
    cumulative_pnl: cumulativePnL,
    status: 'REVERTING'
  });
}

function evaluateTrade() {
  if (!active) return;
  // Simulate profit/loss: mean reversion gives between -0.7% and +3% of virtual balance
  const changePct = (Math.random() * 3.7 - 0.7) / 100; // -0.7%..+3%
  const pnl = parseFloat((virtualBalance * changePct).toFixed(2));
  cumulativePnL += pnl;
  virtualBalance += pnl;
  active = false;
  // Log closure
  writeMaster({
    timestamp: new Date().toISOString(),
    team: 'Team_C',
    strategy: 'MeanReversion',
    cumulative_pnl: parseFloat(cumulativePnL.toFixed(2)),
    status: 'IDLE'
  });
  writeWorkspace(`TRADE_DONE: ${trade.direction} entry=$${trade.entry.toFixed(2)} pnl=$${pnl.toFixed(2)}`);
  trade = null;
}

function strategist() {
  // Simple volatility check placeholder – if cumulative pnl negative suggest higher SL
  if (!active && cumulativePnL < 0) {
    writeWorkspace('STRATEGIST: Consider widening stop loss due to volatility');
  }
}

function runCycle() {
  if (!active) {
    const signal = scout();
    const exec = sniper(signal);
    scribe(exec);
  } else {
    evaluateTrade();
  }
  strategist();
  const status = active ? 'REVERTING' : 'WAITING';
  const pnlStr = cumulativePnL.toFixed(2);
  writeWorkspace(`TEAM_C_STATUS: ${status} | REVERSION_PNL: $${pnlStr} | DEVIATION_LEVEL: ${active ? 'High' : 'Low'}`);
}

// Run every 35 seconds
setInterval(runCycle, 35 * 1000);
// API key for NVIDIA-NIM dedicated model
const apiKey = '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';
const modelInfo = 'NVIDIA-NIM-Dedicated';

function testNvidiaNim() {
  try {
    const resp = require('child_process').execSync(`curl -s -H "Authorization: Bearer ${apiKey}" https://integrate.api.nvidia.com/v1/models`);
  } catch (e) {
    writeWorkspace('NVIDIA-NIM connectivity test failed for Team C');
  }
}
// Run connectivity test once at startup
testNvidiaNim();

// Periodic master entry every 30 seconds
setInterval(() => {
  const entry = {
    timestamp: new Date().toISOString().split('T')[1].split('Z')[0].slice(0,8),
    team: 'Team_C',
    strategy: 'MeanReversion',
    model: modelInfo,
    cumulative_pnl: parseFloat(cumulativePnL.toFixed(2)),
    status: active ? 'REVERTING' : 'IDLE'
  };
  writeMaster(entry);
}, 30 * 1000);

console.log('Reversion Master (Team C) started');
// Heartbeat: write status every minute even if no trade
setInterval(() => {
  writeMaster({cumulative_pnl: cumulativePnL, status: 'ACTIVE'});
}, 60 * 1000);
setInterval(()=>{}, 1e9);
