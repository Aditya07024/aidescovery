"use client";

import Link from "next/link";
import { CheckCircle2, XCircle, Globe, Mail, Phone, MapPin, ExternalLink, ShieldCheck, ArrowRight, UserCheck, Building2, Video, Compass } from "lucide-react";
import { SearchResultItem } from "@/types";

interface EntityCardProps {
  item: SearchResultItem;
}

export function EntityCard({ item }: EntityCardProps) {
  const getScoreBadge = (score: number) => {
    if (score >= 80) return "text-emerald-800 bg-emerald-50 border-emerald-300 shadow-sm";
    if (score >= 60) return "text-amber-800 bg-amber-50 border-amber-300 shadow-sm";
    return "text-rose-800 bg-rose-50 border-rose-300 shadow-sm";
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
    <div className="glass-panel glass-panel-hover rounded-3xl p-7 sm:p-9 space-y-7 flex flex-col justify-between border border-slate-200 bg-white/95 group shadow-md hover:shadow-xl transition-all duration-300 my-4">
      
      {/* Header Section */}
      <div className="space-y-6">
        
        {/* Top Badges & Score */}
        <div className="flex items-start justify-between gap-5 pb-3 border-b border-slate-100">
          <div className="space-y-3">
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-900 px-3.5 py-1.5 rounded-xl bg-slate-100 border border-slate-200 flex items-center gap-1.5 shadow-2xs">
                <EntityTypeIcon className="w-3.5 h-3.5 text-emerald-700" />
                {item.entity_type}
              </span>

              {item.is_qualified ? (
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-800 px-3.5 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                  Verified Qualified
                </span>
              ) : (
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 px-3.5 py-1.5 rounded-xl bg-slate-100 border border-slate-200 flex items-center gap-1.5">
                  <XCircle className="w-3.5 h-3.5 text-slate-400" />
                  Unverified Match
                </span>
              )}
            </div>

            <Link href={`/entity/${item.entity_id}`} className="block group-hover:underline pt-1.5">
              <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 group-hover:text-emerald-800 transition-colors leading-snug tracking-tight">
                {item.name}
              </h3>
            </Link>

            {item.location_summary && (
              <p className="text-xs sm:text-sm text-slate-600 flex items-center gap-2 font-medium pt-1">
                <MapPin className="w-4 h-4 text-emerald-700 shrink-0" />
                <span>{item.location_summary}</span>
              </p>
            )}
          </div>

          {/* Match Score Badge */}
          <div className={`px-4 py-3 rounded-2xl border flex flex-col items-center justify-center shrink-0 ${getScoreBadge(item.match_score)}`}>
            <span className="text-[9px] font-extrabold uppercase tracking-widest text-slate-500">Match</span>
            <span className="text-xl font-black leading-none mt-1">{scorePct}%</span>
          </div>
        </div>

        {/* Description Snippet */}
        {item.description && (
          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-normal bg-slate-50/90 p-5 rounded-2xl border border-slate-200/80 shadow-2xs my-4">
            "{item.description}"
          </p>
        )}

      </div>

      {/* Bottom Qualification Justification & Links */}
      <div className="space-y-6 pt-4">
        
        {/* Qualification Reasoning checklist */}
        {item.qualification_reasons && item.qualification_reasons.length > 0 && (
          <div className="bg-slate-50/90 rounded-2xl p-5 sm:p-6 border border-slate-200 space-y-3 shadow-2xs">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-700" /> AI Qualification Evidence:
            </span>
            <ul className="text-xs space-y-2.5 text-slate-800 font-medium pt-1">
              {item.qualification_reasons.slice(0, 3).map((reason, idx) => (
                <li key={idx} className="flex items-start gap-2.5 leading-relaxed">
                  <span className="text-emerald-700 font-bold shrink-0 mt-0.5">✓</span>
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Links & Lineage Button */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600 flex-wrap gap-4">
          <div className="flex items-center gap-4 flex-wrap font-medium">
            {item.website && (
              <a
                href={item.website}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 text-slate-900 hover:text-emerald-700 font-bold px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-200 transition-colors shadow-2xs"
              >
                <Globe className="w-3.5 h-3.5 text-emerald-700" />
                <span>Visit Domain</span>
                <ExternalLink className="w-3 h-3 opacity-60" />
              </a>
            )}
            {item.email && (
              <span className="flex items-center gap-1.5 text-slate-700 font-semibold px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-200">
                <Mail className="w-3.5 h-3.5 text-teal-700" />
                {item.email}
              </span>
            )}
            {item.phone && (
              <span className="flex items-center gap-1.5 text-slate-700 font-semibold px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-200">
                <Phone className="w-3.5 h-3.5 text-emerald-700" />
                {item.phone}
              </span>
            )}
          </div>

          <Link
            href={`/entity/${item.entity_id}`}
            className="text-xs font-bold text-slate-900 hover:text-emerald-800 flex items-center gap-1.5 transition-all ml-auto group-hover:translate-x-1 px-4 py-2 rounded-xl bg-slate-100 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-200 shadow-2xs"
          >
            <span>Audit Lineage</span>
            <ArrowRight className="w-4 h-4 text-emerald-700" />
          </Link>
        </div>

      </div>

    </div>
  );
}
