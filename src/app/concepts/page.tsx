import React from 'react';
import Link from 'next/link';
import { getDocSlugs } from '@/lib/docs';
import { Lightbulb, ChevronRight } from 'lucide-react';

export default function ConceptsPage() {
  const slugs = getDocSlugs().filter(s => s.startsWith('concepts/'));

  return (
    <div className="max-w-4xl mx-auto py-12 px-6">
      <div className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-2 text-white drop-shadow-lg">Concepts</h1>
        <p className="text-blue-200/70 text-lg font-light tracking-wide">Exploring the deeper architecture of our ideas.</p>
      </div>

      <div className="grid gap-4">
        {slugs.length > 0 ? (
          slugs.map((slug) => (
            <Link
              key={slug}
              href={`/docs/${slug}`}
              className="group flex items-center justify-between p-6 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 hover:border-blue-400/30 hover:bg-white/10 transition-all duration-300 shadow-lg hover:shadow-blue-900/20"
            >
              <div className="flex items-center gap-5">
                <div className="p-3 rounded-xl bg-white/5 border border-white/5 text-gray-300 group-hover:text-blue-300 group-hover:bg-blue-500/20 group-hover:border-blue-400/20 transition-all shadow-inner">
                  <Lightbulb size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-white text-lg group-hover:text-blue-100 transition-colors">
                    {slug.replace('concepts/', '')}
                  </h3>
                </div>
              </div>
              <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-blue-500 group-hover:text-white transition-all duration-300">
                 <ChevronRight size={18} />
              </div>
            </Link>
          ))
        ) : (
          <div className="py-20 text-center border border-dashed border-white/10 rounded-3xl bg-white/5 backdrop-blur-sm">
            <p className="text-white/40">No concepts explored yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
