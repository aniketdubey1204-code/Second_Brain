'use client';
import React, { useEffect } from 'react';

export default function LiquidBackground() {
  // Load tsparticles script and initialize a simple digital‑rain effect
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/tsparticles@2.12.0/tsparticles.bundle.min.js';
    script.async = true;
    script.onload = () => {
      // @ts-ignore
// The bundle attaches tsParticles to window
      // @ts-ignore
      if (window.tsParticles) {
        window.tsParticles.load('tsparticles', {
          fpsLimit: 60,
          background: { color: { value: '#000000' } },
          particles: {
            number: { value: 60 },
            color: { value: ['#00ff99', '#00ccff'] },
            shape: { type: 'circle' },
            opacity: { value: 0.4 },
            size: { value: { min: 1, max: 3 } },
            move: { direction: 'bottom', speed: 1.5, outModes: { default: 'out' } },
            interactivity: { detectsOn: 'canvas', events: { resize: true } },
          },
          detectRetina: true,
        });
      }
    };
    document.body.appendChild(script);
    return () => {
      // Cleanup on unmount
      if (window.tsParticles) {
        window.tsParticles?.dom?.forEach(p => p?.destroy());
      }
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none z-0 bg-[#050505]">
      {/* Neon gradient overlay */}
      <div className="absolute inset-0 animate-neon-pulse bg-gradient-to-br from-[#ff00ff] via-[#00ffff] to-[#00ff00] opacity-20 mix-blend-screen" />

      {/* Static Blobs for performance */}
      <div className="static-blob top-[-10%] left-[-10%] w-[60vw] h-[60vw] bg-blue-600/10" />
      <div className="static-blob top-[20%] right-[-10%] w-[50vw] h-[50vw] bg-purple-600/10" />
      <div className="static-blob bottom-[-10%] left-[10%] w-[60vw] h-[60vw] bg-pink-600/10" />
      
      {/* Particle canvas */}
      <div id="tsparticles" className="absolute inset-0" />

      {/* Noise Overlay */}
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.02] mix-blend-overlay"></div>
      
      {/* Vignette */}
      <div className="absolute inset-0 bg-radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.8) 100%)" />
    </div>
  );
}
