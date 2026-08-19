"use client";

import Link from "next/link";
import { CheckCircle2, XCircle, Globe, Mail, Phone, MapPin, ExternalLink, ShieldCheck, ArrowRight, UserCheck, Building2, Video, Compass } from "lucide-react";
import { SearchResultItem } from "@/types";

interface EntityCardProps {
  item: SearchResultItem;
}

export function EntityCard({ item }: EntityCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-800 bg-emerald-50 border-emerald-300";
    if (score >= 60) return "text-amber-800 bg-amber-50 border-amber-300";
    return "text-rose-800 bg-rose-50 border-rose-300";
  };

  const getEntityIcon = (type: string) => {
    const t = type.toLowerCase();
    if (t.includes("person") || t.includes("professional")) return UserCheck;
    if (t.includes("business") || t.includes("company")) return Building2;
    if (t.includes("creator") || t.includes("channel")) return Video;
    return Compass;
  };

  const EntityTypeIcon = getEntityIcon(item.entity_type);
  const scorePct = Math.round(item.match_score);

  return (
    <div className="glass-panel glass-panel-hover rounded-3xl p-5.5 space-y-4 relative flex flex-col justify-between border border-slate-200 bg-white/95 group shadow-md">
      
      {/* Header Section */}
      <div className="space-y-3">
        
        {/* Top Badges & Score */}
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-900 px-2.5 py-0.5 rounded-lg bg-slate-100 border border-slate-300 flex items-center gap-1">
                <EntityTypeIcon className="w-3 h-3 text-emerald-700" />
                {item.entity_type}
              </span>

              {item.is_qualified ? (
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 px-2 py-0.5 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-700" />
                  Verified Qualified
                </span>
              ) : (
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-2 py-0.5 rounded-lg bg-slate-100 border border-slate-200 flex items-center gap-1">
                  <XCircle className="w-3 h-3 text-slate-400" />
                  Unverified Match
                </span>
              )}
            </div>

            <Link href={`/entity/${item.entity_id}`} className="block group-hover:underline">
              <h3 className="text-lg font-bold text-slate-900 group-hover:text-emerald-700 transition-colors leading-snug">
                {item.name}
              </h3>
            </Link>

            {item.location_summary && (
              <p className="text-xs text-slate-500 flex items-center gap-1 font-medium">
                <MapPin className="w-3.5 h-3.5 text-emerald-700 shrink-0" />
                <span>{item.location_summary}</span>
              </p>
            )}
          </div>

          {/* Match Score Badge */}
          <div className={`px-3 py-2 rounded-2xl border flex flex-col items-center justify-center shrink-0 ${getScoreColor(item.match_score)} shadow-sm`}>
            <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Match</span>
            <span className="text-lg font-black leading-none mt-0.5">{scorePct}%</span>
          </div>
        </div>

        {/* Description Snippet */}
        {item.description && (
          <p className="text-xs sm:text-sm text-slate-700 line-clamp-2 leading-relaxed font-normal bg-slate-50 p-3 rounded-xl border border-slate-100">
            "{item.description}"
          </p>
        )}

      </div>

      {/* Bottom Qualification Justification & Links */}
      <div className="space-y-3 pt-2">
        
        {/* Qualification Reasoning checklist */}
        {item.qualification_reasons && item.qualification_reasons.length > 0 && (
          <div className="bg-slate-50/90 rounded-2xl p-3 border border-slate-200 space-y-1.5">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-700 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" /> AI Fact Qualification:
            </span>
            <ul className="text-[11px] space-y-1 text-slate-800 font-medium">
              {item.qualification_reasons.slice(0, 3).map((reason, idx) => (
                <li key={idx} className="flex items-start gap-1.5 leading-normal">
                  <span className="text-emerald-700 font-bold shrink-0">✓</span>
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Links & Lineage Button */}
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600 flex-wrap gap-2">
          <div className="flex items-center gap-3 flex-wrap font-medium">
            {item.website && (
              <a
                href={item.website}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-slate-800 hover:text-emerald-700 font-semibold transition-colors"
              >
                <Globe className="w-3.5 h-3.5 text-emerald-700" />
                <span>Source Domain</span>
                <ExternalLink className="w-3 h-3 opacity-70" />
              </a>
            )}
            {item.email && (
              <span className="flex items-center gap-1 text-slate-700">
                <Mail className="w-3.5 h-3.5 text-teal-700" />
                {item.email}
              </span>
            )}
            {item.phone && (
              <span className="flex items-center gap-1 text-slate-700">
                <Phone className="w-3.5 h-3.5 text-emerald-700" />
                {item.phone}
              </span>
            )}
          </div>

          <Link
            href={`/entity/${item.entity_id}`}
            className="text-xs font-bold text-slate-900 hover:text-emerald-700 flex items-center gap-1 transition-all ml-auto group-hover:translate-x-0.5"
          >
            <span>Provenance Lineage</span>
            <ArrowRight className="w-3.5 h-3.5 text-emerald-700" />
          </Link>
        </div>

      </div>

    </div>
  );
}
