"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getEntityDetail } from "@/lib/api";
import { EntityDetail } from "@/types";
import { ArrowLeft, Globe, Mail, Phone, MapPin, ShieldCheck, CheckCircle2, ExternalLink, Database, Layers } from "lucide-react";

export default function EntityDetailsPage() {
  const params = useParams();
  const entityId = params.id as string;

  const [entity, setEntity] = useState<EntityDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"provenance" | "raw">("provenance");

  useEffect(() => {
    async function loadEntity() {
      try {
        const data = await getEntityDetail(entityId);
        setEntity(data);
      } catch (err) {
        console.error("Failed to load entity details:", err);
      } finally {
        setLoading(false);
      }
    }
    loadEntity();
  }, [entityId]);

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-slate-600 text-sm font-semibold">Loading Entity Intelligence & Data Provenance Lineage...</p>
      </div>
    );
  }

  if (!entity) {
    return (
      <div className="py-20 text-center space-y-4 glass-panel rounded-3xl">
        <p className="text-slate-700 font-semibold">Entity profile not found.</p>
        <Link href="/" className="inline-flex items-center gap-2 text-indigo-600 text-xs font-bold hover:underline">
          <ArrowLeft className="w-4 h-4" /> Back to Discovery Search
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-4">
      
      {/* Back Button */}
      <Link href="/" className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-900 text-xs font-bold transition-colors">
        <ArrowLeft className="w-4 h-4 text-indigo-600" /> Back to Discovery Dashboard
      </Link>

      {/* Hero Entity Header */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-xl relative overflow-hidden bg-white/90">
        
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-indigo-700 px-3 py-1 rounded-xl bg-indigo-50 border border-indigo-200">
                {entity.entity_type} Profile
              </span>
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 px-3 py-1 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                Verified In DB
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              {entity.name}
            </h1>

            {entity.location_summary && (
              <p className="text-xs sm:text-sm text-slate-600 flex items-center gap-1.5 font-medium">
                <MapPin className="w-4 h-4 text-indigo-600 shrink-0" />
                <span>{entity.location_summary}</span>
              </p>
            )}
          </div>
        </div>

        {/* Contact Strip */}
        <div className="pt-4 border-t border-slate-200 flex items-center gap-4 flex-wrap text-xs text-slate-700 font-semibold">
          {entity.website && (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200">
              <Globe className="w-4 h-4 text-indigo-600" />
              <span>{entity.website}</span>
            </div>
          )}
          {entity.email && (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200">
              <Mail className="w-4 h-4 text-sky-600" />
              <span>{entity.email}</span>
            </div>
          )}
          {entity.phone && (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200">
              <Phone className="w-4 h-4 text-emerald-600" />
              <span>{entity.phone}</span>
            </div>
          )}
        </div>

      </div>

      {/* Tabs Switcher */}
      <div className="flex items-center gap-3 border-b border-slate-200 pb-3">
        <button
          onClick={() => setActiveTab("provenance")}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
            activeTab === "provenance"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/20"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Data Provenance & Fact Lineage ({entity.sources?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab("raw")}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
            activeTab === "raw"
              ? "bg-sky-600 text-white shadow-md shadow-sky-500/20"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
          }`}
        >
          <Database className="w-4 h-4" />
          <span>Raw Structured JSON Payload</span>
        </button>
      </div>

      {/* Tab Content: Provenance Table */}
      {activeTab === "provenance" ? (
        <div className="glass-panel rounded-3xl overflow-hidden shadow-xl bg-white">
          <div className="p-4 sm:p-5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <span className="text-xs font-extrabold uppercase tracking-widest text-slate-700 flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-600" />
              Observed vs Inferred Attribute Lineage Matrix
            </span>
            <span className="text-[11px] text-slate-500 font-medium">Strict Anti-Hallucination Lineage</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-100 text-[10px] uppercase font-bold text-slate-500 tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">Attribute Key</th>
                  <th className="px-5 py-3.5">Extracted Value</th>
                  <th className="px-5 py-3.5">Fact Classification</th>
                  <th className="px-5 py-3.5">Source Web Origin</th>
                  <th className="px-5 py-3.5">Collected Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {entity.sources && entity.sources.length > 0 ? (
                  entity.sources.map((prov, idx) => (
                    <tr key={idx} className="hover:bg-slate-50 transition-colors">
                      <td className="px-5 py-4 font-mono font-bold text-indigo-600">{prov.field_name}</td>
                      <td className="px-5 py-4 text-slate-900 font-semibold">{prov.value_raw || "—"}</td>
                      <td className="px-5 py-4">
                        {prov.verification_status === "inferred" ? (
                          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-700 border border-purple-200">
                            INFERRED FACT
                          </span>
                        ) : (
                          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-emerald-100 text-emerald-700 border border-emerald-200">
                            OBSERVED FACT
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-4 max-w-xs truncate">
                        {prov.source_url ? (
                          <a
                            href={prov.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-indigo-600 hover:underline flex items-center gap-1 font-medium"
                          >
                            <Globe className="w-3.5 h-3.5 shrink-0" />
                            <span className="truncate">{prov.source_url}</span>
                            <ExternalLink className="w-3 h-3 shrink-0 opacity-70" />
                          </a>
                        ) : (
                          <span className="text-slate-400">Internal Resolver</span>
                        )}
                      </td>
                      <td className="px-5 py-4 font-mono text-slate-500">
                        {new Date(prov.collected_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="px-5 py-8 text-center text-slate-500">
                      No provenance records available for this entity.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Raw JSON Viewer */
        <div className="glass-panel p-5 rounded-3xl border border-slate-200 font-mono text-xs text-slate-800 overflow-x-auto bg-slate-900 text-slate-100">
          <pre>{JSON.stringify(entity, null, 2)}</pre>
        </div>
      )}

    </div>
  );
}
