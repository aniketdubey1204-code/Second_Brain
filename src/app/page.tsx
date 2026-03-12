import React from 'react';
import { getDocSlugs } from '@/lib/docs';
import DashboardClient from '@/components/DashboardClient';

export default function Home() {
  const slugs = getDocSlugs();

  return (
    <main className="min-h-screen bg-transparent text-text">
       <DashboardClient slugs={slugs} />
    </main>
  );
}
