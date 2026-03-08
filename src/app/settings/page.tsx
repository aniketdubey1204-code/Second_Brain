'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Shield, Bell, Monitor, Palette, Check, Zap, Cpu, Activity, Database, X, Info, Lock, Trash2, HardDrive } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useConfig } from '@/components/Providers';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  }
};

const item = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 }
};

interface ToggleProps {
  enabled: boolean;
  onChange: () => void;
}

const Toggle = ({ enabled, onChange }: ToggleProps) => (
  <button 
    onClick={(e) => { e.stopPropagation(); onChange(); }}
    className={cn(
      "w-10 h-5 rounded-full transition-all duration-300 relative border",
      enabled ? "bg-blue-500/40 border-blue-400/50 shadow-[0_0_10px_rgba(59,130,246,0.3)]" : "bg-white/5 border-white/10"
    )}
  >
    <div className={cn(
      "absolute top-1 w-2.5 h-2.5 rounded-full transition-all duration-300 shadow-sm",
      enabled ? "left-6 bg-white" : "left-1 bg-white/30"
    )} />
  </button>
);

export default function SettingsPage() {
  const { theme, setTheme, fontSize, setFontSize, animations, setAnimations } = useConfig();
  
  const [states, setStates] = useState<Record<string, boolean>>({
    "Push Notifications": true,
    "Two-Factor Auth": false,
    "Diagnostics": true,
    "Theme Auto-switch": true,
    "Quantum Encryption": true,
    "Neural Sync": true,
    "Auto-Backup": true
  });

  const [activeInfo, setActiveInfo] = useState<string | null>(null);
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const toggleState = (id: string) => {
    setStates(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const executeSync = () => {
    setIsSyncing(true);
    setTimeout(() => setIsSyncing(false), 2000);
  };

  const descriptions: Record<string, string> = {
    "Theme": "Switch between Cyber-Dark, Liquid-Glass, and Neon-Pulse modes to alter the visual interface.",
    "Font Size": "Adjust the base density of text for better ingestion speed.",
    "Animations": "Toggle motion effects and fluid transitions.",
    "Neural Sync": "Keep local brain data synchronized with cloud-based cognitive nodes.",
    "Quantum Encryption": "End-to-end multi-layer encryption for classified vulnerability research.",
    "Latency Optimization": "Reduce response time between synapses for faster browsing.",
    "Change Password": "Update your master biometric decryption key for secure access.",
    "Two-Factor Auth": "Secure access using a rolling TOTP code (like Google Authenticator) or a physical U2F security key for multi-layer neural protection.",
    "Session History": "Log and track all cognitive sessions across paired devices.",
    "Auto-Backup": "Automatically export brain backups to distributed storage every 4 hours.",
    "Storage": "Manage total neural capacity and cleanup legacy synaptic caches.",
    "Diagnostics": "Run self-checks to ensure all neural nodes are functioning optimally."
  };

  return (
    <div className="w-full py-12 px-6 lg:px-12 pb-32">
       <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-white/5 rounded-3xl border border-white/10 backdrop-blur-md shadow-2xl relative group">
               <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
               <Settings className="w-8 h-8 text-white relative z-10" />
            </div>
            <div>
              <h1 className="text-5xl font-bold tracking-tighter text-white uppercase">Settings</h1>
              <p className="text-slate-400 text-sm tracking-widest uppercase font-medium">Core Configuration • Alpha v3.0</p>
            </div>
          </div>
       </motion.div>

       <motion.div variants={container} initial="hidden" animate="show" className="grid gap-8 md:grid-cols-2">
          
          {/* Appearance Section */}
          <motion.div variants={item} className="p-8 rounded-[2.5rem] bg-white/5 border border-white/10 backdrop-blur-3xl">
             <div className="flex items-center gap-4 mb-10">
                <Palette className="text-pink-400" />
                <h3 className="text-2xl font-bold text-white tracking-tight">Appearance</h3>
             </div>
             <div className="space-y-4">
                <div className="flex flex-col gap-2 p-5 rounded-2xl bg-white/5 border border-white/5">
                   <span className="text-xs uppercase tracking-widest text-white/30 font-bold mb-2">Interface Theme</span>
                   <div className="flex gap-2">
                      {['cyber-dark', 'liquid-glass', 'neon-pulse'].map(t => (
                        <button key={t} onClick={() => setTheme(t as any)} className={cn(
                          "px-4 py-2 rounded-xl text-[10px] uppercase font-bold tracking-widest transition-all",
                          theme === t ? "bg-blue-600 text-white shadow-lg" : "bg-white/5 text-white/40 hover:bg-white/10"
                        )}>
                          {t.replace('-', ' ')}
                        </button>
                      ))}
                   </div>
                </div>
                <div className="flex flex-col gap-2 p-5 rounded-2xl bg-white/5 border border-white/5">
                   <span className="text-xs uppercase tracking-widest text-white/30 font-bold mb-2">Neural Density (Font)</span>
                   <div className="flex gap-2">
                      {['small', 'medium', 'large'].map(s => (
                        <button key={s} onClick={() => setFontSize(s as any)} className={cn(
                          "px-4 py-2 rounded-xl text-[10px] uppercase font-bold tracking-widest transition-all",
                          fontSize === s ? "bg-white text-black" : "bg-white/5 text-white/40 hover:bg-white/10"
                        )}>
                          {s}
                        </button>
                      ))}
                   </div>
                </div>
                <div className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5">
                   <span className="text-sm text-gray-300 font-medium">Fluid Motion</span>
                   <Toggle enabled={animations} onChange={() => setAnimations(!animations)} />
                </div>
             </div>
          </motion.div>

          {/* Privacy & Security Section */}
          <motion.div variants={item} className="p-8 rounded-[2.5rem] bg-white/5 border border-white/10 backdrop-blur-3xl">
             <div className="flex items-center gap-4 mb-10">
                <Shield className="text-green-400" />
                <h3 className="text-2xl font-bold text-white tracking-tight">Security</h3>
             </div>
             <div className="space-y-3">
                <button onClick={() => setActiveAction('Change Password')} className="w-full flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5 hover:border-white/20 transition-all group">
                   <div className="flex items-center gap-3">
                      <Lock size={16} className="text-white/40 group-hover:text-blue-400" />
                      <span className="text-sm text-gray-300">Change Decryption Key</span>
                   </div>
                   <ChevronRight size={14} className="text-white/20" />
                </button>
                <div className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5">
                   <span className="text-sm text-gray-300">Quantum Encryption</span>
                   <Toggle enabled={states["Quantum Encryption"]} onChange={() => toggleState("Quantum Encryption")} />
                </div>
                <div className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5">
                   <span className="text-sm text-gray-300">Two-Factor Auth</span>
                   <Toggle enabled={states["Two-Factor Auth"]} onChange={() => toggleState("Two-Factor Auth")} />
                </div>
             </div>
          </motion.div>

          {/* Data Matrix Section */}
          <motion.div variants={item} className="p-8 rounded-[2.5rem] bg-white/5 border border-white/10 backdrop-blur-3xl">
             <div className="flex items-center gap-4 mb-10">
                <Database className="text-yellow-400" />
                <h3 className="text-2xl font-bold text-white tracking-tight">Data Matrix</h3>
             </div>
             <div className="space-y-4">
                <div className="p-5 rounded-2xl bg-white/5 border border-white/5">
                   <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                         <HardDrive size={16} className="text-white/40" />
                         <span className="text-sm text-gray-300">Neural Capacity</span>
                      </div>
                      <span className="text-xs font-mono text-blue-400">42.8 GB / 100 GB</span>
                   </div>
                   <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div className="w-[42%] h-full bg-gradient-to-r from-blue-600 to-cyan-400" />
                   </div>
                </div>
                <button onClick={() => setActiveAction('Clear Cache')} className="w-full flex items-center justify-between p-5 rounded-2xl bg-red-500/5 border border-red-500/10 hover:bg-red-500/10 transition-all group">
                   <div className="flex items-center gap-3">
                      <Trash2 size={16} className="text-red-400/50 group-hover:text-red-400" />
                      <span className="text-sm text-red-400/80">Purge Synaptic Cache</span>
                   </div>
                   <span className="text-[10px] uppercase font-bold text-red-400/30">Dangerous</span>
                </button>
                <div className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5">
                   <span className="text-sm text-gray-300">Auto-Backup</span>
                   <Toggle enabled={states["Auto-Backup"]} onChange={() => toggleState("Auto-Backup")} />
                </div>
             </div>
          </motion.div>

          {/* Neural Section */}
          <motion.div variants={item} className="p-8 rounded-[2.5rem] bg-white/5 border border-white/10 backdrop-blur-3xl">
             <div className="flex items-center gap-4 mb-10">
                <Cpu className="text-blue-400" />
                <h3 className="text-2xl font-bold text-white tracking-tight">Neural Link</h3>
             </div>
             <div className="space-y-3">
                <div className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5">
                   <span className="text-sm text-gray-300">Neural Sync</span>
                   <Toggle enabled={states["Neural Sync"]} onChange={() => toggleState("Neural Sync")} />
                </div>
                <div className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5">
                   <span className="text-sm text-gray-300">Diagnostics</span>
                   <Toggle enabled={states["Diagnostics"]} onChange={() => toggleState("Diagnostics")} />
                </div>
                <button onClick={() => setActiveInfo('Latency Optimization')} className="w-full flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all">
                   <span className="text-sm text-gray-300">Optimize Synapse</span>
                   <Activity size={14} className="text-white/20" />
                </button>
             </div>
          </motion.div>

       </motion.div>

       {/* Floating Save Button */}
       <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} className="fixed bottom-10 right-10 z-50">
          <button onClick={executeSync} disabled={isSyncing} className={cn(
              "flex items-center gap-4 px-10 py-5 rounded-[2rem] font-black text-sm uppercase tracking-[0.2em] shadow-[0_25px_50px_rgba(37,99,235,0.4)] transition-all active:scale-95",
              isSyncing ? "bg-green-600 text-white" : "bg-gradient-to-r from-blue-600 to-blue-500 hover:from-white hover:to-white hover:text-black text-white"
            )}>
             <Zap size={20} className={cn("fill-current", isSyncing && "animate-ping")} />
             {isSyncing ? "Synchronizing..." : "Execute Synchronization"}
          </button>
       </motion.div>

       {/* Action Modal */}
       <AnimatePresence>
         {activeAction && (
           <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setActiveAction(null)} className="absolute inset-0 bg-black/90 backdrop-blur-xl" />
              <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} className="glassPanel !p-12 w-full max-w-md relative z-10 !rounded-[3rem] border-white/20 text-center">
                 <h2 className="text-3xl font-black text-white mb-6 uppercase tracking-tighter">{activeAction}</h2>
                 <p className="text-white/50 mb-10 leading-relaxed">Neural authorization required. Enter master credential to proceed with this offensive protocol.</p>
                 <input type="password" placeholder="Master Key..." className="w-full bg-white/5 border border-white/10 p-5 rounded-2xl text-white outline-none mb-8 focus:border-blue-500" />
                 <div className="flex gap-4">
                    <button onClick={() => setActiveAction(null)} className="flex-1 py-4 bg-white/5 text-white font-bold rounded-xl hover:bg-white/10 transition-all">Cancel</button>
                    <button onClick={() => setActiveAction(null)} className="flex-1 py-4 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-500 shadow-xl transition-all uppercase text-xs tracking-widest italic">Authorize</button>
                 </div>
              </motion.div>
           </div>
         )}
       </AnimatePresence>

       {/* Info Modal */}
       <AnimatePresence>
         {activeInfo && (
           <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setActiveInfo(null)} className="absolute inset-0 bg-black/80 backdrop-blur-md" />
              <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} className="glassPanel !p-10 w-full max-w-sm relative z-10 !rounded-[2.5rem] border-white/20 text-center">
                 <div className="w-16 h-16 bg-blue-500/20 rounded-2xl flex items-center justify-center text-blue-400 mx-auto mb-6">
                    <Info size={32} />
                 </div>
                 <h2 className="text-2xl font-black text-white mb-3 uppercase tracking-tighter">{activeInfo}</h2>
                 <p className="text-white/50 text-sm leading-relaxed mb-8">{descriptions[activeInfo] || "Neural core protocol definition pending."}</p>
                 <button onClick={() => setActiveInfo(null)} className="w-full py-4 bg-white text-black font-black uppercase tracking-widest rounded-xl hover:bg-blue-500 hover:text-white transition-all text-xs">Close</button>
              </motion.div>
           </div>
         )}
       </AnimatePresence>
    </div>
  );
}

function ChevronRight({ size, className }: { size: number, className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="m9 18 6-6-6-6" />
    </svg>
  );
}
