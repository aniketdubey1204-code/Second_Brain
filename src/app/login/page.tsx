"use client";

import { signIn, useSession } from "next-auth/react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { LogIn, Brain } from "lucide-react";

export default function LoginPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") {
      router.push("/");
    }
  }, [status, router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-6 text-center">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="p-12 rounded-[3rem] bg-white/5 border border-white/10 backdrop-blur-3xl shadow-2xl max-w-md w-full"
      >
        <div className="w-20 h-20 bg-blue-500/20 rounded-[2rem] flex items-center justify-center mx-auto mb-8 border border-blue-400/30">
          <Brain size={40} className="text-blue-400" />
        </div>
        
        <h1 className="text-4xl font-bold mb-4 tracking-tight">Access Locked</h1>
        <p className="text-slate-400 mb-10 font-light">This neural interface is restricted. Please authenticate to continue.</p>

        <button 
          onClick={() => signIn("google")}
          className="w-full flex items-center justify-center gap-3 py-4 bg-white text-black rounded-2xl font-bold hover:bg-gray-100 transition-all active:scale-95 shadow-xl"
        >
          <img src="https://www.google.com/favicon.ico" className="w-5 h-5" alt="Google" />
          Login with Google
        </button>
        
        <p className="mt-8 text-[10px] text-white/20 uppercase tracking-[0.2em]">Authorized Personnel Only</p>
      </motion.div>
    </div>
  );
}
