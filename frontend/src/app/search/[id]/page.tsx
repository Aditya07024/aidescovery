"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getSearchJobStatus, getSearchResults, getExportUrl } from "@/lib/api";
import { SearchJobResponse, SearchResultItem } from "@/types";
import { EntityCard } from "@/components/entity-card";
import { Loader2, Download, Filter, CheckCircle2, AlertCircle, Sparkles, Layers, Cpu, Search } from "lucide-react";

export default function SearchResultsPage() {
  const params = useParams();
  const searchId = params.id as string;

  const [job, setJob] = useState<SearchJobResponse | null>(null);
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [qualifiedOnly, setQualifiedOnly] = useState(false);
  const [filterQuery, setFilterQuery] = useState("");

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const fetchJobAndResults = async () => {
      try {
        const jobData = await getSearchJobStatus(searchId);
        setJob(jobData);

        if (jobData.status === "completed" || jobData.status === "failed") {
          const resultsData = await getSearchResults(searchId, qualifiedOnly);
          setResults(resultsData);
          setLoading(false);
        } else {
          // Poll every 1.2s if still running
          intervalId = setTimeout(fetchJobAndResults, 1200);
        }
      } catch (err) {
        console.error("Error fetching job status:", err);
        setLoading(false);
      }
    };

    fetchJobAndResults();

    return () => {
      if (intervalId) clearTimeout(intervalId);
    };
  }, [searchId, qualifiedOnly]);

  const filteredResults = results.filter((item) => {
    if (!filterQuery.trim()) return true;
    const q = filterQuery.toLowerCase();
    return (
      item.name.toLowerCase().includes(q) ||
      (item.description && item.description.toLowerCase().includes(q)) ||
      (item.location_summary && item.location_summary.toLowerCase().includes(q))
    );
  });

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-6 px-2 sm:px-4">
      
      {/* Search Header & Pipeline Execution Glass Panel */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-xl relative overflow-hidden bg-white/95 border border-slate-200">
        
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-extrabold uppercase tracking-wider text-emerald-800 shadow-2xs">
              <Sparkles className="w-4 h-4 text-emerald-700" />
              <span>Job ID: {searchId.slice(0, 8)}...</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
              Entity Discovery & Intelligence Pipeline
            </h1>
          </div>

          {/* Export Buttons */}
          {job && job.status === "completed" && (
            <div className="flex items-center gap-3">
              <a
                href={getExportUrl(searchId, "csv")}
                download
                className="px-4.5 py-2.5 bg-slate-900 hover:bg-emerald-800 text-white border border-slate-800 rounded-2xl text-xs font-bold flex items-center gap-2 transition-all shadow-md active:scale-95"
              >
                <Download className="w-4 h-4 text-emerald-400" /> Export CSV
              </a>
              <a
                href={getExportUrl(searchId, "json")}
                download
                className="px-4.5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-900 border border-slate-300 rounded-2xl text-xs font-bold flex items-center gap-2 transition-all shadow-sm active:scale-95"
              >
                <Download className="w-4 h-4 text-emerald-700" /> Export JSON
              </a>
            </div>
          )}
        </div>

        {/* Real-time Stage Progress Tracker */}
        {job && (
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <div className="flex items-center justify-between text-xs font-bold text-slate-700">
              <span className="capitalize flex items-center gap-2 text-sm font-extrabold">
                {job.status !== "completed" && job.status !== "failed" && (
                  <Loader2 className="w-4 h-4 text-emerald-700 animate-spin" />
                )}
                Pipeline Status: <strong className="text-emerald-700 uppercase tracking-wider">{job.status}</strong>
              </span>
              <span className="text-slate-500 font-mono text-xs font-semibold">{job.progress}% Executed</span>
            </div>

            {/* Glowing Gradient Progress Bar */}
            <div className="w-full h-3.5 bg-slate-100 rounded-full overflow-hidden border border-slate-200 p-0.5 shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-emerald-600 via-teal-600 to-slate-800 transition-all duration-700 rounded-full shadow-md shadow-emerald-500/20"
                style={{ width: `${job.progress}%` }}
              />
            </div>

            {/* Discovered vs Qualified Summary Bar */}
            <div className="flex items-center gap-6 text-xs text-slate-600 font-semibold pt-1">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-700" />
                <span>Total Discovered: <strong className="text-slate-900 font-extrabold text-sm">{job.discovered}</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                <span>Qualified Matches: <strong className="text-emerald-800 font-extrabold text-sm">{job.qualified}</strong></span>
              </div>
            </div>
          </div>
        )}

      </div>

      {/* AI Search Plan Specification Card */}
      {job?.structured_plan && (
        <div className="glass-panel p-5 sm:p-6 rounded-3xl text-xs space-y-3 bg-white border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 text-slate-500 font-bold uppercase tracking-widest text-[10px]">
            <Cpu className="w-4 h-4 text-emerald-700" />
            <span>AI Executed Structured Search Plan</span>
          </div>
          <div className="flex items-center gap-6 flex-wrap text-slate-800 font-semibold text-xs pt-1">
            <div>Target Entity: <span className="font-extrabold text-emerald-800 uppercase px-3 py-1 rounded-lg bg-emerald-50 border border-emerald-200 shadow-2xs ml-1">{job.structured_plan.entity_type}</span></div>
            <div>Roles / Specialty: <span className="font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200 ml-1">{job.structured_plan.profession?.join(", ") || "Any"}</span></div>
            <div>Location Scope: <span className="font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200 ml-1">{job.structured_plan.location?.city || job.structured_plan.location?.country || "Global"}</span></div>
          </div>
        </div>
      )}

      {/* Results Header Controls */}
      <div className="flex items-center justify-between flex-wrap gap-4 pt-3 pb-1">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter leads by name, keyword..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              className="pl-9 pr-4 py-2.5 glass-input rounded-2xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none w-60 sm:w-80 font-medium border-slate-300"
            />
          </div>

          <button
            onClick={() => setQualifiedOnly(!qualifiedOnly)}
            className={`px-4 py-2.5 rounded-2xl text-xs font-bold flex items-center gap-2 border transition-all ${
              qualifiedOnly
                ? "bg-emerald-50 text-emerald-800 border-emerald-300 shadow-sm"
                : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
            }`}
          >
            <Filter className="w-4 h-4" />
            <span>Qualified Only</span>
          </button>
        </div>

        <span className="text-xs text-slate-600 font-semibold">
          Showing <strong className="text-slate-900 font-extrabold">{filteredResults.length}</strong> of <strong className="text-slate-700">{results.length}</strong> entities
        </span>
      </div>

      {/* Entity Cards Grid */}
      {loading ? (
        <div className="py-24 text-center space-y-4 glass-panel rounded-3xl bg-white border border-slate-200 shadow-sm">
          <Loader2 className="w-10 h-10 text-emerald-700 animate-spin mx-auto" />
          <p className="text-slate-700 text-sm font-semibold">Executing multi-source discovery, web crawling & AI qualification...</p>
        </div>
      ) : filteredResults.length === 0 ? (
        <div className="py-20 glass-panel rounded-3xl text-center text-slate-600 text-sm space-y-2 bg-white border border-slate-200 shadow-sm">
          <AlertCircle className="w-8 h-8 text-slate-400 mx-auto" />
          <p className="font-semibold text-slate-700">No matching entities found for this filter criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredResults.map((item) => (
            <EntityCard key={item.entity_id} item={item} />
          ))}
        </div>
      )}

    </div>
  );
}
