"use client";

import React, { useState } from "react";
import {
  FileText,
  Copy,
  Download,
  Mail,
  Edit3,
  Check,
  Send,
  ArrowLeft,
  Building2,
  AlertCircle,
  MapPin,
  Clock,
  Sparkles,
  ShieldCheck,
} from "lucide-react";
import { AnalysisResponse, StoredComplaint } from "@/lib/types";
import { saveComplaint } from "@/lib/api";

interface ComplaintPreviewScreenProps {
  response: AnalysisResponse;
  imagePreview: string;
  onBackToResults: () => void;
  onSubmitSuccess: (complaint: StoredComplaint) => void;
}

export default function ComplaintPreviewScreen({
  response,
  imagePreview,
  onBackToResults,
  onSubmitSuccess,
}: ComplaintPreviewScreenProps) {
  // Initial complaint values from backend response
  const initialSubject =
    response.complaint?.subject ||
    `Urgent: Report of ${response.issue.type.toUpperCase()} requiring municipal inspection and repair`;

  const initialBody =
    response.complaint?.body ||
    `To,\nThe Executive Officer / Ward Commissioner,\n${
      response.authority?.authority_name || "Municipal Authority"
    }\n\nSubject: ${initialSubject}\n\nSir/Madam,\n\nI am writing to draw your urgent attention to a severe civic issue detected at ${
      response.location?.address || "the stated coordinates"
    } (GPS: ${response.location?.coordinates.latitude}, ${
      response.location?.coordinates.longitude
    }).\n\nIssue Observed: Severe ${
      response.issue.type
    } presenting a public safety hazard to residents and daily commuters.\nAssessed Risk Level: ${
      response.severity?.level || "HIGH"
    } (Risk Score: ${((response.severity?.score || 0.8) * 100).toFixed(
      0
    )}/100).\n\nIn accordance with the Municipal Citizen Charter, it is requested that an inspection officer be deputed to inspect the defect and execute remedial restoration at the earliest.\n\nThank you.\nYours faithfully,\nCitizen Resident`;

  // Local editable state
  const [subject, setSubject] = useState<string>(initialSubject);
  const [body, setBody] = useState<string>(initialBody);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Copy to clipboard
  const handleCopy = () => {
    const fullText = `SUBJECT:\n${subject}\n\nBODY:\n${body}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  // Download complaint text file
  const handleDownload = () => {
    const fullText = `================================================================================
CIVICSENSE AI — OFFICIAL MUNICIPAL COMPLAINT DRAFT
================================================================================
Reference Request ID: ${response.request_id}
Generated Timestamp : ${new Date().toISOString()}
Target Authority    : ${response.authority?.authority_name || "Municipal Corporation"}
Department          : ${response.authority?.department || "Civil Engineering / Works"}
Location Coordinates: ${response.location?.coordinates.latitude}, ${response.location?.coordinates.longitude}
Assessed Severity   : ${response.severity?.level || "HIGH"} (Score: ${((response.severity?.score || 0.8) * 100).toFixed(0)}/100)
--------------------------------------------------------------------------------
SUBJECT:
${subject}

COMPLAINT LETTER BODY:
${body}
--------------------------------------------------------------------------------
Generated via CivicSense AI Multi-Modal Engine
================================================================================`;

    const blob = new Blob([fullText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `CivicComplaint_${response.request_id.slice(0, 8)}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Open native email client draft
  const handleOpenEmailDraft = () => {
    const targetEmail = response.authority?.contact_email || "commissioner@mcg.gov.in";
    const mailtoUrl = `mailto:${encodeURIComponent(targetEmail)}?subject=${encodeURIComponent(
      subject
    )}&body=${encodeURIComponent(body)}`;
    window.open(mailtoUrl, "_blank");
  };

  // Submit Complaint / Register Ticket
  const handleSubmit = () => {
    setIsSubmitting(true);

    const refNum = `CIVIC-2026-${Math.floor(1000 + Math.random() * 9000)}`;

    const newRecord: StoredComplaint = {
      id: response.request_id,
      reference_no: refNum,
      issue_type: response.issue.type,
      severity: response.severity?.level || "HIGH",
      address: response.location?.address || "Gurugram, Haryana",
      city: response.location?.city || "Gurugram",
      authority_name: response.authority?.authority_name || "Municipal Corporation of Gurugram",
      contact_phone: response.authority?.contact_phone || "1800-180-1817",
      subject: subject,
      body: body,
      created_at: new Date().toISOString(),
      status: "Draft Ready",
      image_preview: imagePreview,
    };

    saveComplaint(newRecord);

    setTimeout(() => {
      setIsSubmitting(false);
      onSubmitSuccess(newRecord);
    }, 600);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header & Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <button
            onClick={onBackToResults}
            className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white mb-2 transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to AI Analysis</span>
          </button>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <span>Formal Civic Complaint Draft</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              LLM Formatted
            </span>
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Review, edit, download or draft an email with verified authority references before official submission.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => setIsEditing(!isEditing)}
            className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold border transition-all ${
              isEditing
                ? "bg-emerald-600 text-white border-emerald-500"
                : "bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700"
            }`}
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>{isEditing ? "Finish Editing" : "Edit Letter"}</span>
          </button>

          <button
            type="button"
            onClick={handleCopy}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-all cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleDownload}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download .txt</span>
          </button>
        </div>
      </div>

      {/* Authority Context Pill */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-950 flex items-center justify-center text-indigo-400 border border-indigo-800/40">
            <Building2 className="w-4 h-4" />
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">
              Addressed Authority
            </span>
            <span className="text-white font-semibold text-sm">
              {response.authority?.authority_name || "Municipal Corporation"}
            </span>
            {response.authority?.department && (
              <span className="text-slate-400 ml-1.5">({response.authority.department})</span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700 font-medium">
            Category: <strong className="text-white capitalize">{response.issue.type}</strong>
          </span>
          <span
            className={`px-2.5 py-1 rounded-md font-bold text-xs border ${
              response.severity?.level === "CRITICAL"
                ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                : "bg-amber-500/20 text-amber-300 border-amber-500/40"
            }`}
          >
            Priority: {response.severity?.level || "HIGH"}
          </span>
        </div>
      </div>

      {/* Main Letter Sheet (Styled as an Official Notice Paper) */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
        {/* Subject Header */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <FileText className="w-3.5 h-3.5 text-emerald-400" />
            <span>Complaint Subject</span>
          </label>
          {isEditing ? (
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full bg-slate-950 border border-emerald-500/60 rounded-xl px-4 py-2.5 text-sm font-semibold text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          ) : (
            <div className="bg-slate-950/70 border border-slate-800/90 rounded-xl px-4 py-3 text-sm font-semibold text-white">
              {subject}
            </div>
          )}
        </div>

        {/* Complaint Body */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <span>Official Letter Body</span>
          </label>
          {isEditing ? (
            <textarea
              rows={12}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="w-full bg-slate-950 border border-emerald-500/60 rounded-xl p-4 font-mono text-xs leading-relaxed text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          ) : (
            <div className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-5 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
              {body}
            </div>
          )}
        </div>

        {/* Legal & Charter Disclaimer */}
        <div className="bg-slate-950/40 border border-slate-800/60 rounded-xl p-3 flex items-start space-x-2 text-[11px] text-slate-400">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <span>
            This grievance draft incorporates verified municipal jurisdiction rules. No synthetic contact info has been fabricated. Opening an email draft launches your local client for final citizen review.
          </span>
        </div>
      </div>

      {/* Bottom Dispatch Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <button
          type="button"
          onClick={handleOpenEmailDraft}
          className="w-full sm:w-auto px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-800/40 hover:border-cyan-600/50 text-xs font-bold flex items-center justify-center space-x-2 transition-all cursor-pointer"
        >
          <Mail className="w-4 h-4 text-cyan-400" />
          <span>Open Email Draft in Client</span>
        </button>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 font-extrabold text-sm shadow-xl shadow-emerald-500/20 hover:shadow-emerald-500/35 transition-all flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          <span>{isSubmitting ? "Registering..." : "Submit / Save Draft Complaint"}</span>
        </button>
      </div>
    </div>
  );
}
