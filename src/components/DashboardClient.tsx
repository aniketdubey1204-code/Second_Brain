'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, ChevronRight, Clock, Sparkles, Brain, Zap, Layers, Activity, ShieldCheck, Search, Plus, X } from 'lucide-react';

interface DashboardClientProps {
  slugs: string[];
}

export default function DashboardClient({ slugs }: DashboardClientProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const dailyLogs = slugs.filter(s => s.startsWith('daily/')).length;
  const bugBounties = slugs.filter(s => s.startsWith('bug-bounty/')).length;

  // Real search logic
  const filteredSlugs = useMemo(() => {
    return slugs.filter(slug => 
      slug.toLowerCase().includes(searchQuery.toLowerCase()) ||
      slug.split('/').pop()?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [slugs, searchQuery]);

  return (
    <div className="relative w-full min-h-full">
      
      {/* Content Layer */}
      <div className="max-w-7xl mx-auto py-8 px-6 lg:px-12 relative z-10 pb-24">
        
        {/* Header Stats Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-12 px-6 py-4 glassPanel !rounded-3xl border-white/10">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Activity size={14} className="text-blue-400" />
              <span className="text-[10px] uppercase tracking-widest font-bold text-white/50 whitespace-nowrap">Core: Nominal</span>
            </div>
            <div className="h-4 w-px bg-white/10 hidden sm:block" />
            <div className="flex items-center gap-2">
              <ShieldCheck size={14} className="text-green-400" />
              <span className="text-[10px] uppercase tracking-widest font-bold text-white/50 whitespace-nowrap">Sync: Encrypted</span>
            </div>
          </div>
          
          <div className="flex items-center gap-8 text-[10px] uppercase tracking-[0.2em] font-black">
             <div className="flex flex-col items-center sm:items-start">
                <span className="text-white/30 whitespace-nowrap">Neural Nodes</span>
                <span className="text-blue-300">{slugs.length} Units</span>
             </div>
             <div className="flex flex-col items-center sm:items-start">
                <span className="text-white/30 whitespace-nowrap">Bug Bounties</span>
                <span className="text-red-400">{bugBounties} Exploits</span>
             </div>
             <div className="flex flex-col items-center sm:items-start">
                <span className="text-white/30 whitespace-nowrap">Daily Logs</span>
                <span className="text-pink-300">{dailyLogs} Cycles</span>
             </div>
          </div>
        </div>

        {/* Hero Section */}
        <div className="mb-16 md:mb-24 text-center relative flex flex-col items-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-[10px] font-black uppercase tracking-[0.3em] mb-8">
             <Sparkles size={12} />
             <span>Neural Interface Active</span>
          </div>

          <h1 className="text-6xl md:text-[8rem] lg:text-[10rem] font-black tracking-tighter mb-6 text-white drop-shadow-2xl leading-[0.9] uppercase break-all sm:break-normal">
            Brain <span className="text-blue-500/80">v2</span>
          </h1>
          
          <div className="flex flex-col items-center gap-8 w-full max-w-2xl">
            <p className="text-white/60 text-base md:text-xl leading-relaxed font-light tracking-wide px-4">
              Secure hyper-repository for <span className="text-white font-bold border-b-2 border-blue-500/50 pb-1">Aniket Dubey</span>. Synchronized neural documentation and daily cognitive logs.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center gap-4 w-full px-4">
               <div className="glassPanel !p-2 !rounded-2xl flex items-center gap-2 pr-6 border-white/5 w-full sm:w-auto flex-1">
                  <div className="p-3 bg-white/5 rounded-xl text-white/40">
                     <Search size={18} />
                  </div>
                  <input 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Query Neural Cache..." 
                    className="bg-transparent outline-none text-sm text-white placeholder-white/20 w-full" 
                  />
                  {searchQuery && (
                    <button onClick={() => setSearchQuery('')} className="text-white/40 hover:text-white mr-2">
                      <X size={14} />
                    </button>
                  )}
               </div>
               <button 
                onClick={() => setIsAddModalOpen(true)}
                className="p-5 rounded-2xl bg-blue-600 hover:bg-white hover:text-black transition-all shadow-2xl active:scale-90 shrink-0 group"
               >
                  <Plus size={20} className="group-hover:rotate-90 transition-transform duration-300" />
               </button>
            </div>
          </div>
        </div>

        {/* Dynamic Grid */}
        <div className="grid gap-6 md:gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {filteredSlugs.length > 0 ? (
            filteredSlugs.map((slug) => (
              <div key={slug} className="h-full group">
                <Link
                  href={`/docs/${slug}`}
                  className="relative flex flex-col h-full p-8 glassPanel !rounded-[2.5rem] transition-all duration-300 border-white/5 hover:border-blue-500/30 overflow-hidden"
                >
                  <div className="relative z-10 flex justify-between items-start mb-12">
                    <div className="p-4 rounded-2xl bg-white/5 border border-white/10 text-white shadow-2xl group-hover:bg-blue-600 group-hover:border-blue-400 transition-all duration-300">
                      {slug.startsWith('daily/') ? <Clock size={24} /> : <Layers size={24} />}
                    </div>
                    
                    <div className="flex flex-col items-end">
                       <span className="text-[9px] font-black px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/40 uppercase tracking-[0.2em]">
                         {slug.includes('/') ? slug.split('/')[0] : 'NODE'}
                       </span>
                    </div>
                  </div>
                  
                  <div className="relative z-10 mt-auto">
                    <h3 className="text-2xl md:text-3xl font-black text-white mb-4 group-hover:text-blue-100 transition-colors tracking-tighter leading-tight break-words">
                      {slug.split('/').pop()?.replace(/-/g, ' ')}
                    </h3>
                    
                    <div className="flex items-center justify-between pt-6 border-t border-white/5 mt-4">
                       <div className="flex items-center gap-2 text-[10px] text-white/30 uppercase tracking-widest font-bold">
                          <Activity size={12} className="text-blue-500/50" />
                          <span>Synced</span>
                       </div>
                       <div className="w-10 h-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-white group-hover:text-black transition-all duration-300">
                          <ChevronRight size={20} />
                       </div>
                    </div>
                  </div>
                </Link>
              </div>
            ))
          ) : (
            <div className="col-span-full py-32 text-center glassPanel !rounded-[3rem]">
              <Brain className="w-32 h-32 text-white/20 mx-auto mb-10" />
              <h3 className="text-4xl font-black text-white mb-4 tracking-tighter uppercase">No Nodes Found</h3>
              <p className="text-white/40 mb-8">Search query "{searchQuery}" returned zero results.</p>
              <button 
                onClick={() => setSearchQuery('')}
                className="liquidButton px-12 py-5 text-xs font-black uppercase tracking-[0.3em]"
              >
                Clear Search
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Add Modal Placeholder */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsAddModalOpen(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-md"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="glassPanel !p-12 w-full max-w-lg relative z-10 !rounded-[3rem] border-white/20"
            >
              <h2 className="text-4xl font-black text-white mb-4 tracking-tighter uppercase">Initiate Node</h2>
              <p className="text-white/50 mb-10 leading-relaxed">System is currently in read-only mode via neural link. Manual ingestion requires local terminal access.</p>
              <div className="p-6 bg-blue-500/10 border border-blue-500/20 rounded-2xl mb-8">
                 <p className="text-xs font-mono text-blue-300"># Command to add new doc:<br/>openclaw brain add --title "My New Doc"</p>
              </div>
              <button 
                onClick={() => setIsAddModalOpen(false)}
                className="w-full py-5 bg-white text-black font-black uppercase tracking-widest rounded-2xl hover:bg-blue-500 hover:text-white transition-all"
              >
                Understood
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
