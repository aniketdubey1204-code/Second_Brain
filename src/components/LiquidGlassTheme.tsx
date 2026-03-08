"use client";

import styles from '../app/LiquidGlass.module.css';

export default function LiquidGlassTheme({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.liquidGlassContainer}>
      <div className="absolute inset-0 z-0 pointer-events-none">
        {/* Animated Background Blobs */}
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
        <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-yellow-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-[-20%] left-[20%] w-[500px] h-[500px] bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
      </div>
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
