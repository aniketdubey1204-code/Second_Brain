import React from 'react';
import Link from 'next/link';
import { getDocSlugs } from '@/lib/docs';
import { Calendar, ChevronRight } from 'lucide-react';

export default function JournalPage() {
  const slugs = getDocSlugs().filter(s => s.startsWith('daily/'));

  return (
    <div className="w-full py-12 px-6 lg:px-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-2 text-white drop-shadow-lg">Journal</h1>
        <p className="text-pink-200/70 text-lg font-light tracking-wide">A daily record of our discussions and progress.</p>
      </div>

      <div className="grid gap-4">
        {slugs.length > 0 ? (
          slugs.map((slug) => (
            <Link
              key={slug}
              href={`/docs/${slug}`}
              className="group flex items-center justify-between p-6 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 hover:border-pink-400/30 hover:bg-white/10 transition-all duration-300 shadow-lg hover:shadow-pink-900/20"
            >
              <div className="flex items-center gap-5">
                <div className="p-3 rounded-xl bg-white/5 border border-white/5 text-gray-300 group-hover:text-pink-300 group-hover:bg-pink-500/20 group-hover:border-pink-400/20 transition-all shadow-inner">
                  <Calendar size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-white text-lg group-hover:text-pink-100 transition-colors">
                    {slug.replace('daily/', '')}
                  </h3>
                </div>
              </div>
              <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-pink-500 group-hover:text-white transition-all duration-300">
                 <ChevronRight size={18} />
              </div>
            </Link>
          ))
        ) : (
          <div className="py-20 text-center border border-dashed border-white/10 rounded-3xl bg-white/5 backdrop-blur-sm">
            <p className="text-white/40">No journal entries yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
