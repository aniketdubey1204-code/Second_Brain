import React from 'react';

export default function LiquidBackground() {
  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none z-0 bg-[#050505]">
      {/* Static Blobs for performance */}
      <div className="static-blob top-[-10%] left-[-10%] w-[60vw] h-[60vw] bg-blue-600/10" />
      <div className="static-blob top-[20%] right-[-10%] w-[50vw] h-[50vw] bg-purple-600/10" />
      <div className="static-blob bottom-[-10%] left-[10%] w-[60vw] h-[60vw] bg-pink-600/10" />
      
      {/* Noise Overlay */}
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.02] mix-blend-overlay"></div>
      
      {/* Vignette */}
      <div className="absolute inset-0 bg-radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.8) 100%)" />
    </div>
  );
}
