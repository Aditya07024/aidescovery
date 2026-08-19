"use client";

import Link from "next/link";
import { Sparkles, Key, Search } from "lucide-react";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-200/80 bg-white/90">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Title */}
        <Link href="/" className="flex items-center gap-3.5 group">
          <div className="relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-emerald-600 to-teal-500 rounded-xl blur opacity-25 group-hover:opacity-75 transition duration-300"></div>
            <div className="relative w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5 text-emerald-400 group-hover:text-teal-300 transition-colors" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base sm:text-lg tracking-tight text-slate-900 flex items-center gap-1.5">
                Universal <span className="gradient-text">AI Discovery</span>
              </span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 uppercase tracking-widest hidden sm:inline-block">
                v1.0 Enterprise
              </span>
            </div>
            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold block -mt-0.5">
              Entity Intelligence Platform
            </span>
          </div>
        </Link>

        {/* Status Badge & Navigation Links */}
        <div className="flex items-center gap-5">
          {/* Live System Indicator */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Serper AI Search Live</span>
          </div>

          <nav className="flex items-center gap-2 sm:gap-3">
            <Link
              href="/"
              className="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 flex items-center gap-2 transition-all border border-transparent hover:border-slate-200"
            >
              <Search className="w-4 h-4 text-emerald-600" />
              <span>Discovery</span>
            </Link>

            <Link
              href="/api-keys"
              className="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 flex items-center gap-2 transition-all border border-transparent hover:border-slate-200"
            >
              <Key className="w-4 h-4 text-teal-600" />
              <span>API Keys</span>
            </Link>
          </nav>
        </div>

      </div>
    </header>
  );
}
