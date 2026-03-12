'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Brain, Book, Calendar, Lightbulb, Search, Settings, Menu, X, RefreshCw, Shield, LogOut, User, Activity } from 'lucide-react';
import { signOut, useSession } from 'next-auth/react';
import { motion } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function Sidebar() {
  const pathname = usePathname();
  const { data: session } = useSession();
  const [isOpen, setIsOpen] = useState(false);

  // Close sidebar on navigation
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  const navItems = [
    { icon: <Calendar size={18} />, label: 'Journal', href: '/journal' },
    { icon: <Lightbulb size={18} />, label: 'Concepts', href: '/concepts' },
    { icon: <Shield size={18} />, label: 'Bug Bounty', href: '/bug-bounty' },
    { icon: <Book size={18} />, label: 'All Docs', href: '/' },
  ];

  return (
    <>
      {/* Mobile Header - Always visible on small screens */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-bg/40 backdrop-blur-xl border-b border-accent/20 flex items-center justify-between px-4 z-40">
        <Link href="/" className="flex items-center gap-2">
          <div className="p-1 rounded-md text-accent shadow-[0_0_10px_var(--theme-accent)] shadow-accent/30">
            <Brain size={18} />
          </div>
          <span className="font-bold text-text text-xs uppercase tracking-widest">Neural Brain</span>
        </Link>
        <button 
          onClick={() => setIsOpen(true)}
          className="text-accent p-2"
          aria-label="Open menu"
        >
          <Menu size={24} />
        </button>
      </div>

      {/* Sidebar Overlay */}
      {isOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-bg/80 backdrop-blur-md z-[60]"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside className={cn(
        "glassPanel fixed lg:relative top-4 lg:top-0 left-0 w-72 lg:w-64 z-[70] transition-transform duration-500 ease-out flex flex-col m-4 lg:m-6 h-[calc(100vh-2rem)] lg:h-[calc(100vh-3rem)] shrink-0 border border-accent/20",
        isOpen ? "translate-x-0" : "-translate-x-[110%] lg:translate-x-0"
      )}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-6 mb-2">
          <div className="flex items-center gap-3 group">
            <div className="bg-accent/10 p-2 rounded-lg text-accent border border-accent/30 shadow-[0_0_15px_var(--theme-accent)] shadow-accent/20 group-hover:shadow-[0_0_25px_var(--theme-accent)] shadow-accent/40 transition-all">
              <Brain size={22} />
            </div>
            <div className="flex flex-col">
              <span className="font-bold tracking-tighter text-text text-lg leading-none uppercase glitch-text group-hover:glitch-active">Brain v2</span>
              <span className="text-[8px] text-accent/50 tracking-[0.3em] font-bold uppercase mt-1">Interface</span>
            </div>
          </div>
          <button 
            onClick={() => setIsOpen(false)}
            className="lg:hidden text-accent/70 hover:text-accent p-1"
          >
            <X size={24} />
          </button>
        </div>

        {/* Navigation */}
        <div className="flex flex-col gap-1 flex-1 px-4">
          <div className="relative mb-6 group">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-accent/30 group-focus-within:text-accent transition-colors">
              <Search size={14} />
            </div>
            <input 
              placeholder="System search..." 
              className="w-full bg-bg/40 rounded-full py-2.5 pl-9 pr-3 text-xs text-text placeholder-text/20 outline-none border border-accent/10 focus:border-accent/50 transition-all focus:shadow-[0_0_15px_var(--theme-accent)] shadow-accent/10 font-mono"
            />
          </div>

          <div className="space-y-1.5">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-full text-xs font-bold uppercase tracking-widest transition-all duration-300 relative group border border-transparent",
                  pathname === item.href 
                    ? "bg-accent/10 text-accent border-accent/30 shadow-[0_0_15px_var(--theme-accent)] shadow-accent/10" 
                    : "text-text/40 hover:text-text hover:bg-accent/5 hover:border-accent/20"
                )}
              >
                <span className={cn("transition-transform duration-300 group-hover:scale-110 group-hover:text-accent", pathname === item.href && "text-accent")}>
                  {item.icon}
                </span>
                <span className="relative z-10">{item.label}</span>
                {pathname === item.href && (
                  <motion.div 
                    layoutId="active-indicator"
                    className="absolute left-0 w-1 h-2/3 bg-accent rounded-r-full shadow-[0_0_10px_var(--theme-accent)]"
                  />
                )}
              </Link>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-auto border-t border-accent/10 p-4 flex flex-col gap-2">
          {session && (
            <div className="flex items-center gap-3 px-3 py-3 bg-accent/5 rounded-full border border-accent/10 mb-2 group/user">
              {session.user?.image ? (
                <img src={session.user.image} alt="Avatar" className="w-8 h-8 rounded-full border border-accent/30 relative z-10 grayscale group-hover/user:grayscale-0 transition-all" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center text-accent relative z-10 border border-accent/20">
                  <User size={16} />
                </div>
              )}
              <div className="flex flex-col min-w-0 relative z-10">
                <span className="text-[10px] font-bold text-text truncate uppercase tracking-wider">{session.user?.name || 'Neural User'}</span>
                <span className="text-[8px] text-accent/50 truncate uppercase font-bold tracking-tighter">Auth: Verified</span>
              </div>
            </div>
          )}

          <Link href="/settings" className="flex items-center gap-3 px-4 py-2 text-text/40 hover:text-text hover:bg-accent/5 rounded-lg transition-all text-[10px] uppercase font-bold tracking-widest w-full group">
            <Settings size={16} className="group-hover:rotate-90 transition-transform duration-700" />
            Control Panel
          </Link>
          
          <button 
            onClick={() => signOut()}
            className="flex items-center gap-3 px-4 py-2 text-red-500/40 hover:text-red-500 hover:bg-red-500/5 rounded-lg transition-all text-[10px] uppercase font-bold tracking-widest w-full group"
          >
            <LogOut size={16} className="group-hover:-translate-x-1 transition-transform" />
            Terminate
          </button>

          <div className="px-4 py-2 flex items-center justify-between mt-1">
             <div className="text-[9px] flex items-center gap-2 font-bold uppercase tracking-[0.2em] pulse-stable">
                <Activity size={10} />
                Link: Stable
             </div>
             <div className="text-[8px] text-text/20 font-mono">v2.0.4</div>
          </div>
        </div>
      </aside>
    </>
  );
}
