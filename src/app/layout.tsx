import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import LiquidBackground from "@/components/LiquidBackground";
import LiquidGlassTheme from "@/components/LiquidGlassTheme"; // Import the new theme
import { Providers } from "@/components/Providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Aniket's Brain",
  description: "Personal knowledge repository",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#050505] text-white flex flex-col lg:flex-row h-screen overflow-hidden`}>
        <Providers>
          <LiquidGlassTheme>
            <LiquidBackground />
            <div className="flex flex-col lg:flex-row w-full h-full relative z-10 overflow-x-hidden overflow-y-auto custom-scrollbar">
              <Sidebar />
              <main className="flex-1 relative">
                {children}
              </main>
            </div>
          </LiquidGlassTheme>
        </Providers>
      </body>
    </html>
  );
}
