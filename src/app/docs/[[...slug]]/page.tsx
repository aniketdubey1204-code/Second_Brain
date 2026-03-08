import React from 'react';
import { getDocBySlug } from '@/lib/docs';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';
import { ChevronLeft, Calendar, FileText, Share2, Printer, Clock } from 'lucide-react';

type Params = Promise<{ slug: string[] }>;

export default async function DocPage(props: { params: Params }) {
  const { slug: slugArray = [] } = await props.params;
  const slug = slugArray.join('/');
  
  if (!slug) {
    return (
      <div className="w-full py-12 px-6 lg:px-12">
        <h1 className="text-2xl font-bold">No document selected</h1>
        <Link href="/" className="text-blue-400 hover:underline">Back to docs</Link>
      </div>
    );
  }

  try {
    const doc = getDocBySlug(slug);
    const category = slug.includes('/') ? slug.split('/')[0] : 'General';
    const fileName = slug.split('/').pop();

    return (
      <div className="w-full py-8 lg:py-16 px-6 lg:px-12 relative">
        
        {/* Navigation & Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
          <div>
            <Link href="/" className="inline-flex items-center gap-2 text-sm text-white/50 hover:text-white mb-6 transition-all group px-3 py-1.5 rounded-full bg-white/5 border border-white/5 hover:border-white/20">
              <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
              Back to System
            </Link>
            
            <div className="flex items-center gap-3 mb-2">
               <span className="px-2.5 py-0.5 rounded-md bg-blue-500/20 border border-blue-500/30 text-[10px] font-bold text-blue-300 uppercase tracking-tighter">
                  {category}
               </span>
               <div className="flex items-center gap-1.5 text-white/40 text-[10px] uppercase tracking-widest font-medium">
                  <Clock size={10} />
                  <span>5 min read</span>
               </div>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold tracking-tighter text-white drop-shadow-2xl">
               {fileName?.replace(/-/g, ' ')}
            </h1>
          </div>

          <div className="flex items-center gap-2 self-end md:self-center">
             <button className="p-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 text-white/70 hover:text-white transition-all shadow-lg active:scale-95">
                <Share2 size={18} />
             </button>
             <button className="p-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 text-white/70 hover:text-white transition-all shadow-lg active:scale-95">
                <Printer size={18} />
             </button>
          </div>
        </div>

        {/* Liquid Glass Article Container */}
        <div className="glassPanel p-6 md:p-12 lg:p-16 mb-12 relative">
           {/* Decorative elements */}
           <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 blur-[80px] rounded-full pointer-events-none" />
           <div className="absolute bottom-0 left-0 w-48 h-48 bg-pink-500/5 blur-[100px] rounded-full pointer-events-none" />
           
           <article className="prose prose-invert prose-blue max-w-none prose-headings:tracking-tighter prose-headings:font-bold prose-p:text-white/80 prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-2xl">
             <ReactMarkdown>{doc.content}</ReactMarkdown>
           </article>
        </div>

        {/* Footer Meta */}
        <div className="pt-10 border-t border-white/10 flex flex-col sm:flex-row justify-between items-center gap-6 text-white/30 text-xs">
          <div className="flex items-center gap-6">
            <div className="flex flex-col gap-1">
              <span className="uppercase tracking-[0.2em] text-[9px] font-bold text-white/20">Source Path</span>
              <span className="font-mono">{slug}.md</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="uppercase tracking-[0.2em] text-[9px] font-bold text-white/20">Access Token</span>
              <span className="font-mono text-green-500/50">VALIDATED</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/5 shadow-inner">
             <Calendar size={14} className="text-blue-400" />
             <span>Synchronized: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
          </div>
        </div>
        
        {/* Subtle Bottom Glow */}
        <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-px bg-gradient-to-r from-transparent via-blue-500/20 to-transparent -z-10" />
      </div>
    );
  } catch (error: any) {
    return (
      <div className="max-w-3xl mx-auto py-24 px-6 text-center">
        <div className="inline-flex p-6 rounded-[2rem] bg-red-500/10 border border-red-500/20 text-red-400 mb-8 shadow-[0_0_50px_rgba(239,68,68,0.1)]">
           <div className="relative">
              <div className="absolute inset-0 blur-xl bg-red-500/40 animate-pulse" />
              <span className="text-5xl relative z-10">⚠️</span>
           </div>
        </div>
        <h1 className="text-3xl font-bold mb-4 tracking-tighter text-white">Neural Link Severed</h1>
        <p className="text-white/40 mb-10 max-w-md mx-auto leading-relaxed">{error.message}</p>
        <Link href="/" className="liquidButton px-8 py-4 text-sm font-bold uppercase tracking-widest">
          Reconnect to Core
        </Link>
      </div>
    );
  }
}
