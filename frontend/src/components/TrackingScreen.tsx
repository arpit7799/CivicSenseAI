"use client";

import React, { useEffect, useState } from "react";
import {
  FileText,
  Search,
  CheckCircle2,
  Clock,
  MapPin,
  Building2,
  Trash2,
  ExternalLink,
  ChevronRight,
  Filter,
  PlusCircle,
  Copy,
  Check,
} from "lucide-react";
import { StoredComplaint } from "@/lib/types";
import { getStoredComplaints } from "@/lib/api";

interface TrackingScreenProps {
  onNavigateReport: () => void;
  highlightedComplaintId?: string;
}

export default function TrackingScreen({ onNavigateReport, highlightedComplaintId }: TrackingScreenProps) {
  const [complaints, setComplaints] = useState<StoredComplaint[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selectedComplaint, setSelectedComplaint] = useState<StoredComplaint | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const loadComplaints = () => {
    const list = getStoredComplaints();
    setComplaints(list);
    if (highlightedComplaintId) {
      const match = list.find((c) => c.id === highlightedComplaintId);
      if (match) setSelectedComplaint(match);
    } else if (list.length > 0 && !selectedComplaint) {
      setSelectedComplaint(list[0]);
    }
  };

  useEffect(() => {
    loadComplaints();
  }, [highlightedComplaintId]);

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = complaints.filter((c) => c.id !== id);
    setComplaints(updated);
    localStorage.setItem("civicsense_complaints_v1", JSON.stringify(updated));
    if (selectedComplaint?.id === id) {
      setSelectedComplaint(updated.length > 0 ? updated[0] : null);
    }
  };

  const handleCopyRef = (refNo: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(refNo);
    setCopiedId(refNo);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredList = complaints.filter((c) => {
    const matchesSearch =
      c.reference_no.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.issue_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.authority_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <span>Complaint Tracking & Registry</span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              {complaints.length} Records
            </span>
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Audit history of citizen grievances, generated drafts, and registered municipal reference numbers.
          </p>
        </div>

        <button
          onClick={onNavigateReport}
          className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Report New Issue</span>
        </button>
      </div>

      {complaints.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-4 shadow-xl">
          <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
            <FileText className="w-8 h-8" />
          </div>
          <div className="max-w-sm mx-auto">
            <h3 className="text-lg font-bold text-white">No complaints logged yet</h3>
            <p className="mt-1 text-xs text-slate-400">
              Analyze a civic photograph on the Report screen to generate, preview, and track your first municipal complaint.
            </p>
          </div>
          <button
            onClick={onNavigateReport}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold transition-colors cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Submit a Civic Report</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Complaints List Column */}
          <div className="lg:col-span-5 space-y-4">
            {/* Search and Filters */}
            <div className="space-y-2">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search reference, issue, or location..."
                  className="w-full bg-slate-900 border border-slate-800 focus:border-cyan-500 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center space-x-1.5 text-xs">
                <Filter className="w-3.5 h-3.5 text-slate-500" />
                <button
                  onClick={() => setStatusFilter("all")}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    statusFilter === "all"
                      ? "bg-slate-800 text-white border border-slate-700"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  All ({complaints.length})
                </button>
                <button
                  onClick={() => setStatusFilter("Draft Ready")}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    statusFilter === "Draft Ready"
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                      : "text-slate-400 hover:text-emerald-400"
                  }`}
                >
                  Draft Ready
                </button>
              </div>
            </div>

            {/* List */}
            <div className="space-y-2.5 max-h-[580px] overflow-y-auto pr-1">
              {filteredList.map((item) => {
                const isSelected = selectedComplaint?.id === item.id;
                return (
                  <div
                    key={item.id}
                    onClick={() => setSelectedComplaint(item)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? "bg-slate-800/90 border-cyan-500/60 shadow-lg shadow-cyan-950/40"
                        : "bg-slate-900/80 border-slate-800/90 hover:bg-slate-800/50 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold text-cyan-300">
                          {item.reference_no}
                        </span>
                        <button
                          onClick={(e) => handleCopyRef(item.reference_no, e)}
                          className="text-slate-500 hover:text-slate-300"
                          title="Copy reference number"
                        >
                          {copiedId === item.reference_no ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      </div>

                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                          item.severity === "CRITICAL"
                            ? "bg-rose-950/60 text-rose-400 border-rose-800"
                            : item.severity === "HIGH"
                            ? "bg-amber-950/60 text-amber-400 border-amber-800"
                            : "bg-blue-950/60 text-blue-400 border-blue-800"
                        }`}
                      >
                        {item.severity}
                      </span>
                    </div>

                    <div className="mt-2">
                      <p className="text-xs font-semibold text-slate-200 capitalize">
                        {item.issue_type} Report
                      </p>
                      <p className="text-[11px] text-slate-400 truncate mt-0.5">
                        {item.address}
                      </p>
                    </div>

                    <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                      <span>{new Date(item.created_at).toLocaleDateString()}</span>
                      <div className="flex items-center space-x-2">
                        <span className="text-emerald-400 font-medium">{item.status}</span>
                        <button
                          onClick={(e) => handleDelete(item.id, e)}
                          className="text-slate-600 hover:text-rose-400 p-0.5 transition-colors"
                          title="Remove from history"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Complaint Details View Column */}
          <div className="lg:col-span-7">
            {selectedComplaint ? (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
                {/* Details Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <h2 className="text-lg font-bold text-white font-mono">
                        {selectedComplaint.reference_no}
                      </h2>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                        {selectedComplaint.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 flex items-center space-x-1.5">
                      <Clock className="w-3 h-3 text-slate-500" />
                      <span>Submitted: {new Date(selectedComplaint.created_at).toLocaleString()}</span>
                    </p>
                  </div>

                  <div className="text-xs font-mono text-slate-400">
                    ID: {selectedComplaint.id.slice(0, 12)}...
                  </div>
                </div>

                {/* Routing info badges */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl space-y-1">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">
                      Designated Authority
                    </span>
                    <p className="text-white font-semibold">{selectedComplaint.authority_name}</p>
                    {selectedComplaint.contact_phone && (
                      <p className="text-emerald-400 text-[11px] font-mono">
                        Helpline: {selectedComplaint.contact_phone}
                      </p>
                    )}
                  </div>

                  <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl space-y-1">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">
                      Location & Ward
                    </span>
                    <p className="text-slate-200 font-medium truncate">{selectedComplaint.address}</p>
                    <p className="text-slate-400 text-[11px]">{selectedComplaint.city}, Haryana</p>
                  </div>
                </div>

                {/* Preview Image if stored */}
                {selectedComplaint.image_preview && (
                  <div className="rounded-xl overflow-hidden border border-slate-800 bg-slate-950 max-h-48 flex items-center justify-center">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={selectedComplaint.image_preview}
                      alt="Complaint snapshot"
                      className="max-h-48 w-auto object-contain"
                    />
                  </div>
                )}

                {/* Complaint Body */}
                <div className="space-y-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                    Subject: {selectedComplaint.subject}
                  </span>
                  <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-4 font-mono text-xs text-slate-300 whitespace-pre-wrap max-h-60 overflow-y-auto leading-relaxed">
                    {selectedComplaint.body}
                  </div>
                </div>

                {/* Status Notice */}
                <div className="bg-cyan-950/30 border border-cyan-800/40 rounded-xl p-3 text-[11px] text-cyan-200/90 leading-relaxed">
                  <strong>Notice to Citizen:</strong> This complaint is currently staged as{" "}
                  <strong>Draft Ready</strong>. You can open your email client or submit this reference number through the Municipal Corporation of Gurugram online helpline.
                </div>
              </div>
            ) : (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-500 text-sm">
                Select a complaint from the list to view its official details and letter draft.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
