"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Sparkles, Globe, MapPin, Share2, Youtube, ArrowRight, Zap, Layers } from "lucide-react";
import { createSearchJob } from "@/lib/api";

const PRESET_CATEGORIES = [
  {
    category: "Healthcare",
    query: "Find therapists in Delhi with at least 5 years of experience.",
    badge: "Person",
  },
  {
    category: "B2B SaaS",
    query: "Find SaaS CTOs in India working at companies with 20–200 employees.",
    badge: "Executive",
  },
  {
    category: "Medical Specialists",
    query: "Find dermatologists in India who have an Instagram presence and own a clinic.",
    badge: "Clinician",
  },
  {
    category: "Local Commerce",
    query: "Find high rated cafes in Delhi with active online booking options.",
    badge: "Business",
  },
];

export function SearchBar() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedSources, setSelectedSources] = useState<string[]>(["auto"]);

  const handleSourceToggle = (source: string) => {
    if (source === "auto") {
      setSelectedSources(["auto"]);
      return;
    }
    const current = selectedSources.filter((s) => s !== "auto");
    if (current.includes(source)) {
      const updated = current.filter((s) => s !== source);
      setSelectedSources(updated.length === 0 ? ["auto"] : updated);
    } else {
      setSelectedSources([...current, source]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    try {
      const job = await createSearchJob(query, selectedSources);
      router.push(`/search/${job.search_id}`);
    } catch (err: any) {
      alert(err.message || "Failed to start discovery job");
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-7">
      
      {/* Search Form Container */}
      <form onSubmit={handleSubmit} className="relative group">
        
        {/* Glow backdrop */}
        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-sky-400 rounded-3xl blur-xl opacity-20 group-hover:opacity-40 transition duration-700"></div>

        <div className="relative glass-panel rounded-3xl p-3.5 sm:p-4 space-y-3.5 shadow-xl border border-slate-200 bg-white/90">
          
          {/* Main Input Area */}
          <div className="flex items-center gap-3 px-3 py-1">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shrink-0">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything (e.g. 'Find therapists in Delhi with at least 5 years experience')..."
              className="w-full bg-transparent text-slate-900 placeholder-slate-400 text-base sm:text-lg focus:outline-none py-1.5 font-medium"
              required
            />

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-6 py-3.5 bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-700 hover:to-sky-700 text-white text-sm font-bold rounded-2xl flex items-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-40 transition-all shrink-0 active:scale-95"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>Run Discovery</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>

          {/* Sources Connector Selector Bar */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-between px-2 text-xs text-slate-600 flex-wrap gap-2">
            <div className="flex items-center gap-1.5 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
              <Layers className="w-3.5 h-3.5 text-indigo-600" />
              <span>Connectors:</span>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              {[
                { id: "auto", label: "Auto Smart AI", icon: Sparkles },
                { id: "web", label: "Serper Google", icon: Globe },
                { id: "google_maps", label: "Google Maps", icon: MapPin },
                { id: "reddit", label: "Reddit", icon: Share2 },
                { id: "youtube", label: "YouTube", icon: Youtube },
              ].map((src) => {
                const Icon = src.icon;
                const active = selectedSources.includes(src.id);
                return (
                  <button
                    key={src.id}
                    type="button"
                    onClick={() => handleSourceToggle(src.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                      active
                        ? "bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-sm"
                        : "bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5 text-indigo-600" />
                    <span>{src.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

        </div>
      </form>

      {/* Recommended Prompt Presets Grid */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between text-xs text-slate-500 px-1">
          <span className="uppercase font-bold tracking-widest text-[11px] text-slate-600 flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-500" />
            Curated Discovery Templates
          </span>
          <span className="hidden sm:inline-block text-[11px] text-slate-400">Click any card to populate query</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {PRESET_CATEGORIES.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setQuery(preset.query)}
              className="text-left p-4 glass-panel rounded-2xl text-slate-700 hover:text-slate-900 border border-slate-200 hover:border-indigo-300 transition-all flex items-start justify-between gap-3 group glass-panel-hover bg-white/80"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-indigo-700 px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-100">
                    {preset.category}
                  </span>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">
                    {preset.badge}
                  </span>
                </div>
                <p className="text-xs text-slate-800 group-hover:text-indigo-900 transition-colors leading-relaxed font-medium">
                  "{preset.query}"
                </p>
              </div>

              <div className="w-7 h-7 rounded-xl bg-slate-100 group-hover:bg-indigo-50 border border-slate-200 group-hover:border-indigo-200 flex items-center justify-center shrink-0 text-slate-400 group-hover:text-indigo-600 transition-all mt-0.5">
                <Search className="w-3.5 h-3.5" />
              </div>
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}
