import React from 'react';
import { getDocBySlug } from '@/lib/docs';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';
import { ChevronLeft, Calendar, Share2, Printer, Clock } from 'lucide-react';

type Params = Promise<{ slug: string[] }>;

export default async function DocPage(props: { params: Params }) {
  const { slug: slugArray = [] } = await props.params;
  const slug = slugArray.join('/');
  
  if (!slug) {
    return (
      <div className="w-full py-12 px-6 lg:px-12">
        <h1 className="text-2xl font-bold text-text">No document selected</h1>
        <Link href="/" className="text-accent hover:underline">Back to docs</Link>
      </div>
    );
  }

  try {
    const doc = getDocBySlug(slug);
    const category = slug.includes('/') ? slug.split('/')[0] : 'General';
    const fileName = slug.split('/').pop();

    return (
      <div className="w-full py-8 lg:py-16 px-4 sm:px-6 lg:px-12 relative">
        
        {/* Navigation & Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 lg:mb-12">
          <div>
            <Link href="/" className="inline-flex items-center gap-2 text-sm text-text/50 hover:text-text mb-4 lg:mb-6 transition-all group px-3 py-1.5 rounded-full bg-text/5 border border-text/10 hover:border-text/20">
              <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
              Back to System
            </Link>
            
            <div className="flex items-center gap-3 mb-2">
               <span className="px-2.5 py-0.5 rounded-md bg-accent/20 border border-accent/30 text-[10px] font-bold text-accent uppercase tracking-tighter">
                  {category}
               </span>
               <div className="flex items-center gap-1.5 text-text/40 text-[10px] uppercase tracking-widest font-medium">
                  <Clock size={10} />
                  <span>5 min read</span>
               </div>
            </div>
            
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tighter text-text drop-shadow-2xl break-words">
               {fileName?.replace(/-/g, ' ')}
            </h1>
          </div>

          <div className="flex items-center gap-2 self-end md:self-center shrink-0">
             <button className="p-3 rounded-2xl bg-text/5 border border-text/10 hover:bg-text/10 text-text/70 hover:text-text transition-all shadow-lg active:scale-95">
                <Share2 size={18} />
             </button>
             <button className="p-3 rounded-2xl bg-text/5 border border-text/10 hover:bg-text/10 text-text/70 hover:text-text transition-all shadow-lg active:scale-95">
                <Printer size={18} />
             </button>
          </div>
        </div>

        {/* Article Container */}
        <div className="glassPanel p-6 md:p-10 lg:p-16 mb-8 relative">
           <div className="absolute top-0 right-0 w-32 h-32 bg-accent/10 blur-[80px] rounded-full pointer-events-none" />
           <div className="absolute bottom-0 left-0 w-48 h-48 bg-secondary/5 blur-[100px] rounded-full pointer-events-none" />
           
           <article className="prose prose-invert max-w-none prose-headings:tracking-tighter prose-headings:font-bold prose-headings:text-text prose-p:text-text/80 prose-p:leading-relaxed prose-pre:bg-bg prose-pre:border prose-pre:border-text/10 prose-pre:rounded-2xl prose-a:text-accent prose-code:text-accent prose-code:bg-bg/80 prose-strong:text-text">
             <ReactMarkdown>{doc.content}</ReactMarkdown>
           </article>
        </div>

        {/* Footer Meta */}
        <div className="pt-8 border-t border-text/10 flex flex-col sm:flex-row justify-between items-center gap-6 text-text/30 text-xs">
          <div className="flex items-center gap-6">
            <div className="flex flex-col gap-1">
              <span className="uppercase tracking-[0.2em] text-[9px] font-bold text-text/20">Source Path</span>
              <span className="font-mono">{slug}.md</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="uppercase tracking-[0.2em] text-[9px] font-bold text-text/20">Access Token</span>
              <span className="font-mono text-stable/50">VALIDATED</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-text/5 border border-text/5 shadow-inner">
             <Calendar size={14} className="text-accent" />
             <span>Synchronized: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
          </div>
        </div>
      </div>
    );
  } catch (error: any) {
    return (
      <div className="max-w-3xl mx-auto py-24 px-6 text-center">
        <div className="inline-flex p-6 rounded-[2rem] bg-red-500/10 border border-red-500/20 text-red-400 mb-8">
           <div className="relative">
              <div className="absolute inset-0 blur-xl bg-red-500/40 animate-pulse" />
              <span className="text-5xl relative z-10">⚠️</span>
           </div>
        </div>
        <h1 className="text-3xl font-bold mb-4 tracking-tighter text-text">Neural Link Severed</h1>
        <p className="text-text/40 mb-10 max-w-md mx-auto leading-relaxed">{error.message}</p>
        <Link href="/" className="px-8 py-4 text-sm font-bold uppercase tracking-widest bg-accent text-black rounded-xl hover:opacity-90 transition-all">
          Reconnect to Core
        </Link>
      </div>
    );
  }
}
