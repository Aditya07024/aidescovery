"use client";

import { SearchBar } from "@/components/search-bar";
import { Sparkles, ShieldCheck, Cpu, Database, Network, CheckCircle2 } from "lucide-react";

export default function HomePage() {
  return (
    <div className="space-y-12 sm:space-y-16 py-6 sm:py-10">
      
      {/* Hero Section */}
      <div className="text-center space-y-5 max-w-4xl mx-auto px-4 relative">
        
        {/* Soft Ambient Radial Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[32rem] h-[32rem] bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -z-10 animate-glow"></div>

        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-panel text-xs font-bold text-indigo-700 border border-indigo-200 bg-white/80 shadow-md">
          <Sparkles className="w-4 h-4 text-indigo-600 animate-pulse" />
          <span>Universal AI Entity Intelligence & Discovery Platform</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black text-slate-900 tracking-tight leading-[1.08]">
          Discover Verified Entities via <span className="gradient-text">Natural Language</span>
        </h1>

        <p className="text-slate-600 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed font-medium">
          An enterprise-grade AI engine that translates complex natural language queries into structured plans, crawls multi-platform data, resolves entities, and qualifies verified leads.
        </p>

        {/* Feature Badges */}
        <div className="flex items-center justify-center gap-6 text-xs text-slate-600 font-semibold pt-2 flex-wrap">
          <span className="flex items-center gap-1.5 text-slate-700">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Live Serper Google Search
          </span>
          <span className="flex items-center gap-1.5 text-slate-700">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Zero Data Hallucination
          </span>
          <span className="flex items-center gap-1.5 text-slate-700">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Multi-Signal Deduplication
          </span>
        </div>
      </div>

      {/* Main Search Bar Component */}
      <SearchBar />

      {/* Platform Architecture Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4.5 pt-8">
        {[
          {
            icon: Cpu,
            title: "AI Structured Planner",
            desc: "Translates natural language intent into validated entity schemas, role specs, and location targets.",
            color: "text-indigo-600 bg-indigo-50 border-indigo-200",
          },
          {
            icon: Network,
            title: "Multi-Source Connectors",
            desc: "Orchestrates live Google Search, Google Maps, Reddit, YouTube, and deep Web Crawlers.",
            color: "text-sky-600 bg-sky-50 border-sky-200",
          },
          {
            icon: ShieldCheck,
            title: "Multi-Signal Resolution",
            desc: "Deduplicates profiles by linking email hashes, domain authority, phone numbers, and social URLs.",
            color: "text-emerald-600 bg-emerald-50 border-emerald-200",
          },
          {
            icon: Database,
            title: "Fact Provenance Matrix",
            desc: "Separates observed facts from AI inferences with explicit audit lineage for every extracted claim.",
            color: "text-purple-600 bg-purple-50 border-purple-200",
          },
        ].map((feat, idx) => {
          const Icon = feat.icon;
          return (
            <div
              key={idx}
              className="glass-panel glass-panel-hover p-6 rounded-3xl border border-slate-200 bg-white/80 space-y-3 relative group shadow-sm"
            >
              <div className={`w-11 h-11 rounded-2xl flex items-center justify-center border shadow-sm ${feat.color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                {feat.title}
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed font-normal">
                {feat.desc}
              </p>
            </div>
          );
        })}
      </div>

    </div>
  );
}
