'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { SessionProvider } from 'next-auth/react';

type Theme = 'cyber-dark' | 'liquid-glass' | 'neon-pulse';
type FontSize = 'small' | 'medium' | 'large';

interface ConfigContextType {
  theme: Theme;
  setTheme: (t: Theme) => void;
  fontSize: FontSize;
  setFontSize: (s: FontSize) => void;
  animations: boolean;
  setAnimations: (b: boolean) => void;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export function Providers({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('cyber-dark');
  const [fontSize, setFontSize] = useState<FontSize>('medium');
  const [animations, setAnimations] = useState(true);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('brain-theme') as Theme;
    const savedSize = localStorage.getItem('brain-fontSize') as FontSize;
    const savedAnims = localStorage.getItem('brain-animations');

    if (savedTheme) setTheme(savedTheme);
    if (savedSize) setFontSize(savedSize);
    if (savedAnims !== null) setAnimations(savedAnims === 'true');
    
    setIsLoaded(true);
  }, []);

  // Save settings and apply to document
  useEffect(() => {
    if (!isLoaded) return;

    const root = window.document.documentElement;
    root.setAttribute('data-theme', theme);
    root.setAttribute('data-size', fontSize);
    root.style.setProperty('--enable-animations', animations ? '1' : '0');

    localStorage.setItem('brain-theme', theme);
    localStorage.setItem('brain-fontSize', fontSize);
    localStorage.setItem('brain-animations', String(animations));
  }, [theme, fontSize, animations, isLoaded]);

  return (
    <SessionProvider>
      <ConfigContext.Provider value={{ theme, setTheme, fontSize, setFontSize, animations, setAnimations }}>
        {children}
      </ConfigContext.Provider>
    </SessionProvider>
  );
}

export const useConfig = () => {
  const context = useContext(ConfigContext);
  if (!context) throw new Error('useConfig must be used within Providers');
  return context;
};
