'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Brain, Book, Calendar, Lightbulb, Search, Settings, Menu, X, RefreshCw, Shield, LogOut, User } from 'lucide-react';
import { signOut, useSession } from 'next-auth/react';
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
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-white/10 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-4 z-40">
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-white/20 p-1 rounded-md text-blue-300">
            <Brain size={18} />
          </div>
          <span className="font-semibold text-white text-sm">Aniket's Brain v2</span>
        </Link>
        <button 
          onClick={() => setIsOpen(true)}
          className="text-white/70 hover:text-white p-2"
          aria-label="Open menu"
        >
          <Menu size={24} />
        </button>
      </div>

      {/* Sidebar Overlay */}
      {isOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-[60]"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside className={cn(
        "glassPanel fixed lg:relative top-4 lg:top-0 left-0 w-72 lg:w-64 z-[70] transition-transform duration-300 ease-in-out flex flex-col m-4 lg:m-6 h-[calc(100vh-2rem)] lg:h-fit rounded-[2rem] shrink-0 shadow-[0_20px_50px_rgba(0,0,0,0.5)]",
        isOpen ? "translate-x-0" : "-translate-x-[110%] lg:translate-x-0"
      )}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-6 mb-2">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-1.5 rounded-xl text-blue-300 backdrop-blur-md shadow-[0_0_15px_rgba(59,130,246,0.3)]">
              <Brain size={22} />
            </div>
            <span className="font-bold tracking-tight text-white text-lg leading-none drop-shadow-md">Aniket's Brain</span>
          </div>
          <button 
            onClick={() => setIsOpen(false)}
            className="lg:hidden text-white/70 hover:text-white p-1"
          >
            <X size={24} />
          </button>
        </div>

        {/* Navigation */}
        <div className="flex flex-col gap-1 flex-1 px-4">
          <div className="relative mb-6 group">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/50 group-focus-within:text-blue-300 transition-colors">
              <Search size={14} />
            </div>
            <input 
              placeholder="Quick search..." 
              className="w-full bg-white/5 rounded-xl py-2.5 pl-9 pr-3 text-sm text-white placeholder-white/30 outline-none border border-white/10 focus:border-blue-400/50 transition-all focus:bg-white/10 focus:shadow-[0_0_15px_rgba(59,130,246,0.2)]"
            />
          </div>

          <div className="space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 relative overflow-hidden group",
                  pathname === item.href 
                    ? "bg-white/10 text-white shadow-[0_0_20px_rgba(255,255,255,0.1)] border border-white/10" 
                    : "text-white/60 hover:text-white hover:bg-white/5"
                )}
              >
                {/* Liquid hover effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out" />
                
                <span className={cn("relative z-10 transition-transform duration-300", pathname === item.href && "scale-110")}>
                  {item.icon}
                </span>
                <span className="relative z-10">{item.label}</span>
              </Link>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-auto border-t border-white/10 p-4 flex flex-col gap-2">
          {session && (
            <div className="flex items-center gap-3 px-4 py-3 bg-white/5 rounded-2xl border border-white/5 mb-2 group/user overflow-hidden relative">
              <div className="absolute inset-0 bg-blue-500/5 translate-y-full group-hover/user:translate-y-0 transition-transform duration-500" />
              {session.user?.image ? (
                <img src={session.user.image} alt="Avatar" className="w-8 h-8 rounded-full border border-white/20 relative z-10" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 relative z-10">
                  <User size={16} />
                </div>
              )}
              <div className="flex flex-col min-w-0 relative z-10">
                <span className="text-xs font-bold text-white truncate">{session.user?.name || 'Neural User'}</span>
                <span className="text-[10px] text-white/30 truncate">Authenticated</span>
              </div>
            </div>
          )}

          <Link href="/settings" className="flex items-center gap-3 px-4 py-2.5 text-white/60 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300 text-sm w-full group">
            <Settings size={18} className="group-hover:rotate-90 transition-transform duration-500" />
            Settings
          </Link>
          
          <button 
            onClick={() => signOut()}
            className="flex items-center gap-3 px-4 py-2.5 text-red-400/60 hover:text-red-400 hover:bg-red-500/5 rounded-xl transition-all duration-300 text-sm w-full group"
          >
            <LogOut size={18} className="group-hover:-translate-x-1 transition-transform" />
            Disconnect
          </button>

          <div className="text-[10px] text-white/30 px-4 flex items-center gap-1 mt-1 font-mono uppercase tracking-widest">
             <RefreshCw size={10} className="animate-spin-slow" />
             Link: Stable
          </div>
        </div>
      </aside>
    </>
  );
}
