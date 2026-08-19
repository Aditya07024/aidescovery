"use client";

import { useEffect, useState } from "react";
import { createAPIKey, listAPIKeys } from "@/lib/api";
import { APIKeyItem } from "@/types";
import { Key, Plus, Copy, Check, ShieldAlert, Lock } from "lucide-react";

export default function APIKeysPage() {
  const [keys, setKeys] = useState<APIKeyItem[]>([]);
  const [name, setName] = useState("");
  const [newKey, setNewKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadKeys();
  }, []);

  const loadKeys = async () => {
    try {
      const data = await listAPIKeys();
      setKeys(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || loading) return;

    setLoading(true);
    try {
      const res = await createAPIKey(name);
      setNewKey(res.raw_api_key);
      setName("");
      loadKeys();
    } catch (err: any) {
      alert("Failed to create API key");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-4">
      
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold uppercase tracking-wider">
          <Lock className="w-3.5 h-3.5 text-emerald-700" />
          <span>Security & Integration Access</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
          <Key className="w-8 h-8 text-emerald-700" /> API Keys & Access Tokens
        </h1>
        <p className="text-slate-600 text-sm max-w-2xl leading-relaxed">
          Generate REST API keys to programmatically query entity intelligence from applications like <strong>MyMindTherapyFriend</strong>, <strong>Outreach AI</strong>, or custom BI integrations.
        </p>
      </div>

      {/* Secret key reveal banner */}
      {newKey && (
        <div className="glass-panel p-5 rounded-3xl border-2 border-emerald-500 bg-emerald-50/90 space-y-3 shadow-lg animate-pulse">
          <div className="flex items-center gap-2 text-emerald-950 font-bold text-sm">
            <ShieldAlert className="w-5 h-5 text-emerald-700" />
            <span>Secret API Key Created! Save this key immediately; it will not be shown again.</span>
          </div>
          <div className="flex items-center gap-3 bg-white p-3.5 rounded-2xl border border-emerald-200 shadow-sm">
            <code className="text-emerald-950 font-mono text-sm break-all flex-1 select-all">{newKey}</code>
            <button
              onClick={() => copyToClipboard(newKey)}
              className="px-4 py-2 bg-slate-900 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shrink-0 shadow-md active:scale-95 transition-all"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? "Copied!" : "Copy Key"}</span>
            </button>
          </div>
        </div>
      )}

      {/* Generate Key Form */}
      <form onSubmit={handleCreate} className="glass-panel p-6 rounded-3xl border border-slate-200 space-y-4 shadow-md bg-white">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
          <Plus className="w-4 h-4 text-emerald-700" /> Generate New Integration API Key
        </h2>
        <div className="flex items-center gap-3 flex-col sm:flex-row">
          <input
            type="text"
            placeholder="Application Name (e.g. MyMindTherapyFriend / Recruitment Engine)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full sm:flex-1 glass-input px-4 py-3 rounded-2xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none font-medium"
            required
          />
          <button
            type="submit"
            disabled={loading || !name.trim()}
            className="w-full sm:w-auto px-6 py-3 bg-slate-900 hover:bg-emerald-700 text-white font-bold text-sm rounded-2xl flex items-center justify-center gap-2 transition-all disabled:opacity-40 shadow-lg shrink-0 active:scale-95"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <Plus className="w-4 h-4 text-emerald-400" />
                <span>Create Key</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Active API Keys Table */}
      <div className="glass-panel rounded-3xl overflow-hidden border border-slate-200 shadow-md bg-white">
        <div className="p-4 sm:p-5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <span className="text-xs font-extrabold uppercase tracking-widest text-slate-700 flex items-center gap-2">
            <Key className="w-4 h-4 text-emerald-700" />
            Active Integration API Keys ({keys.length})
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-100 text-[10px] uppercase font-bold text-slate-500 tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-5 py-3.5">Application Name</th>
                <th className="px-5 py-3.5">Key Prefix</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5">Created Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {keys.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-5 py-8 text-center text-slate-400">
                    No active API keys found. Generate one above.
                  </td>
                </tr>
              ) : (
                keys.map((k) => (
                  <tr key={k.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-4 font-bold text-slate-900 text-sm">{k.name}</td>
                    <td className="px-5 py-4 font-mono text-emerald-700">{k.key_prefix}...</td>
                    <td className="px-5 py-4">
                      <span className="px-2.5 py-1 rounded-lg font-bold text-[10px] uppercase tracking-wider bg-emerald-50 text-emerald-800 border border-emerald-200">
                        Active
                      </span>
                    </td>
                    <td className="px-5 py-4 text-slate-500 font-mono">{new Date(k.created_at).toLocaleDateString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
