import React from 'react';
import Link from 'next/link';
import { getDocSlugs } from '@/lib/docs';
import { Shield, ChevronRight, Target, Zap, DollarSign } from 'lucide-react';

export default function BugBountyPage() {
  const slugs = getDocSlugs().filter(s => s.startsWith('bug-bounty/'));

  return (
    <div className="w-full py-12 px-6 lg:px-12">
      <div className="mb-12 relative">
        <div className="flex items-center gap-4 mb-4">
           <div className="p-3 bg-red-500/10 rounded-2xl border border-red-500/20 text-red-400 shadow-[0_0_30px_rgba(239,68,68,0.1)]">
              <Shield size={32} />
           </div>
           <h1 className="text-5xl font-black tracking-tighter text-white uppercase italic">Bug Bounty <span className="text-red-500">HQ</span></h1>
        </div>
        <p className="text-gray-400 text-lg font-light tracking-wide max-w-2xl">
          Offensive security protocols and vulnerability research database. Tracking exploits from discovery to bounty.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
         <div className="glassPanel !p-6 flex items-center gap-5 border-white/5">
            <div className="w-12 h-12 rounded-xl bg-orange-500/20 flex items-center justify-center text-orange-400">
               <Target size={24} />
            </div>
            <div>
               <div className="text-[10px] uppercase tracking-widest text-white/30 font-bold">Active Targets</div>
               <div className="text-2xl font-black text-white">12 Systems</div>
            </div>
         </div>
         <div className="glassPanel !p-6 flex items-center gap-5 border-white/5">
            <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center text-green-400">
               <DollarSign size={24} />
            </div>
            <div>
               <div className="text-[10px] uppercase tracking-widest text-white/30 font-bold">Total Bounty</div>
               <div className="text-2xl font-black text-white">$4,250.00</div>
            </div>
         </div>
         <div className="glassPanel !p-6 flex items-center gap-5 border-white/5">
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400">
               <Zap size={24} />
            </div>
            <div>
               <div className="text-[10px] uppercase tracking-widest text-white/30 font-bold">Vulns Found</div>
               <div className="text-2xl font-black text-white">28 Critical</div>
            </div>
         </div>
      </div>

      <div className="grid gap-4">
        {slugs.length > 0 ? (
          slugs.map((slug) => (
            <Link
              key={slug}
              href={`/docs/${slug}`}
              className="group flex items-center justify-between p-6 rounded-[1.5rem] bg-white/5 border border-white/10 hover:border-red-500/30 hover:bg-red-500/5 transition-all duration-500"
            >
              <div className="flex items-center gap-5">
                <div className="p-3 rounded-xl bg-black/40 border border-white/10 text-gray-400 group-hover:text-red-400 group-hover:scale-110 transition-all">
                  <Shield size={20} />
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg group-hover:text-red-100 transition-colors tracking-tight">
                    {slug.replace('bug-bounty/', '').replace(/-/g, ' ')}
                  </h3>
                  <span className="text-[10px] uppercase tracking-widest text-white/20 font-mono">Status: CLASSIFIED</span>
                </div>
              </div>
              <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-red-600 group-hover:text-white transition-all duration-300">
                 <ChevronRight size={20} />
              </div>
            </Link>
          ))
        ) : (
          <div className="py-20 text-center glassPanel border-dashed border-white/10 rounded-[2rem]">
            <p className="text-white/20 uppercase tracking-[0.3em] font-black">No Offensive Data Found</p>
          </div>
        )}
      </div>
    </div>
  );
}
