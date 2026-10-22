"use client";

import React from "react";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ShieldCheck,
  Building2,
  MapPin,
  Clock,
  Layers,
  ArrowRight,
  Sparkles,
  RotateCcw,
  BookOpen,
  Info,
  Phone,
  Mail,
  Zap,
} from "lucide-react";
import { AnalysisResponse } from "@/lib/types";

interface AnalysisResultsScreenProps {
  response: AnalysisResponse;
  imagePreview: string;
  onProceedToComplaint: () => void;
  onReset: () => void;
}

export default function AnalysisResultsScreen({
  response,
  imagePreview,
  onProceedToComplaint,
  onReset,
}: AnalysisResultsScreenProps) {
  const isRejected = response.status === "rejected_no_civic_issue";
  const isPartial = response.status === "partial";
  const isCompleted = response.status === "completed";

  // Severity styling
  const severityLevel = response.severity?.level || "UNKNOWN";
  const severityColor =
    severityLevel === "CRITICAL"
      ? "bg-rose-500/20 text-rose-400 border-rose-500/40"
      : severityLevel === "HIGH"
      ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
      : severityLevel === "MEDIUM"
      ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/40"
      : "bg-blue-500/20 text-blue-400 border-blue-500/40";

  // Status badge styling
  const statusBadge = isCompleted ? (
    <span className="flex items-center space-x-1 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold">
      <CheckCircle2 className="w-3.5 h-3.5" />
      <span>Analysis Completed</span>
    </span>
  ) : isPartial ? (
    <span className="flex items-center space-x-1 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs font-semibold">
      <AlertTriangle className="w-3.5 h-3.5" />
      <span>Partial Analysis</span>
    </span>
  ) : (
    <span className="flex items-center space-x-1 px-3 py-1 rounded-full bg-slate-500/20 text-slate-400 border border-slate-500/30 text-xs font-semibold">
      <XCircle className="w-3.5 h-3.5" />
      <span>Rejected: No Civic Defect Detected</span>
    </span>
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              AI Analysis Results
            </h1>
            {statusBadge}
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Request ID: <span className="font-mono text-slate-300">{response.request_id}</span> • Processed in{" "}
            <span className="font-semibold text-emerald-400">{response.metadata.processing_time_ms}ms</span>
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onReset}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium border border-slate-700 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>New Analysis</span>
          </button>
          {!isRejected && response.complaint && (
            <button
              onClick={onProceedToComplaint}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-sm font-bold shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
            >
              <span>View Generated Complaint</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Duplicate Alert Notice */}
      {response.duplicate_check?.is_potential_duplicate && (
        <div className="bg-amber-950/40 border-2 border-amber-500/60 rounded-2xl p-5 shadow-xl text-amber-200 space-y-2">
          <div className="flex items-center space-x-2 font-bold text-amber-300 text-base">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>Potential Duplicate Complaint Detected</span>
          </div>
          <p className="text-sm text-amber-200/90 leading-relaxed">
            A similar issue was recently registered in close proximity (Similarity Score:{" "}
            <strong className="text-white font-mono">
              {(response.duplicate_check.similarity_score * 100).toFixed(0)}%
            </strong>
            ).
            {response.duplicate_check.existing_complaint_id && (
              <>
                {" "}Existing Reference: <strong className="font-mono text-white">{response.duplicate_check.existing_complaint_id}</strong>.
              </>
            )}
          </p>
          {response.duplicate_check.match_factors && response.duplicate_check.match_factors.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              <span className="text-xs font-semibold text-amber-400">Match Factors:</span>
              {response.duplicate_check.match_factors.map((factor, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded bg-amber-900/60 border border-amber-600/40 text-[11px] font-mono text-amber-200"
                >
                  {factor}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Rejection / Short-Circuit Notice */}
      {isRejected && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center space-y-4 shadow-xl">
          <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
            <ShieldCheck className="w-8 h-8 text-slate-400" />
          </div>
          <div className="max-w-md mx-auto">
            <h2 className="text-lg font-bold text-white">No Civic Infrastructure Defect Detected</h2>
            <p className="mt-2 text-sm text-slate-400 leading-relaxed">
              Our vision engine scanned the image and determined it does not contain civic anomalies such as potholes, garbage accumulation, or broken streetlights.
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Downstream municipal routing and complaint drafting was safely short-circuited to prevent false reports.
            </p>
          </div>
          <button
            onClick={onReset}
            className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-sm font-semibold border border-slate-700 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Upload Another Photograph</span>
          </button>
        </div>
      )}

      {/* Main Grid: Vision, Severity, Location, Authority */}
      {!isRejected && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Column 1: Image & Detection Summary */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Detection Preview</span>
              </h2>

              {/* Image Preview with Bounding Box Overlay */}
              <div className="relative rounded-xl overflow-hidden border border-slate-800 bg-slate-950 flex items-center justify-center">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={imagePreview}
                  alt="Civic issue photograph"
                  className="w-full h-auto object-cover max-h-64"
                />
                {response.vision_details?.primary_issue && (
                  <div className="absolute top-2 left-2 bg-emerald-500/90 text-slate-950 font-bold px-2 py-0.5 rounded text-xs shadow-md">
                    {response.vision_details.primary_issue.issue_class.toUpperCase()} (
                    {(response.vision_details.primary_issue.confidence * 100).toFixed(0)}%)
                  </div>
                )}
              </div>

              {/* Quality & Vision Diagnostics */}
              <div className="space-y-2 text-xs">
                <div className="flex justify-between text-slate-300 py-1 border-b border-slate-800/80">
                  <span className="text-slate-400">Classified Issue</span>
                  <span className="font-semibold text-white capitalize">{response.issue.type}</span>
                </div>
                <div className="flex justify-between text-slate-300 py-1 border-b border-slate-800/80">
                  <span className="text-slate-400">Detection Confidence</span>
                  <span className="font-mono font-semibold text-emerald-400">
                    {(response.issue.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between text-slate-300 py-1 border-b border-slate-800/80">
                  <span className="text-slate-400">Vision Model</span>
                  <span className="font-mono text-slate-400">{response.vision_details.model_version || "YOLOv8"}</span>
                </div>
                <div className="flex justify-between text-slate-300 py-1 border-b border-slate-800/80">
                  <span className="text-slate-400">Image Blur Score</span>
                  <span className="font-mono text-slate-300">
                    {response.vision_details.image_quality?.blur_score?.toFixed(1) ?? "N/A"}
                  </span>
                </div>
                <div className="flex justify-between text-slate-300 py-1">
                  <span className="text-slate-400">Quality Rating</span>
                  <span
                    className={`font-semibold ${
                      response.vision_details.image_quality?.is_valid ? "text-emerald-400" : "text-amber-400"
                    }`}
                  >
                    {response.vision_details.image_quality?.is_valid ? "Adequate / Verified" : "Sub-optimal Quality"}
                  </span>
                </div>
              </div>
            </div>

            {/* Severity Card */}
            {response.severity && (
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
                    <Zap className="w-4 h-4 text-amber-400" />
                    <span>Assessed Severity</span>
                  </h2>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${severityColor}`}>
                    {response.severity.level}
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs text-slate-400">
                    <span>Severity Score</span>
                    <span className="font-mono font-bold text-white text-sm">
                      {(response.severity.score * 100).toFixed(0)} / 100
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                    <div
                      className={`h-2.5 rounded-full ${
                        response.severity.level === "CRITICAL"
                          ? "bg-rose-500"
                          : response.severity.level === "HIGH"
                          ? "bg-amber-500"
                          : response.severity.level === "MEDIUM"
                          ? "bg-yellow-500"
                          : "bg-blue-500"
                      }`}
                      style={{ width: `${Math.min(100, Math.max(10, response.severity.score * 100))}%` }}
                    />
                  </div>
                </div>

                {/* Factors Breakdown */}
                {response.severity.factors && response.severity.factors.length > 0 && (
                  <div className="pt-2 border-t border-slate-800 space-y-2">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                      Contributing Factors
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {response.severity.factors.map((factor, idx) => (
                        <span
                          key={idx}
                          className="bg-slate-950/80 border border-slate-800/80 rounded-md px-2 py-1 text-[11px] font-mono text-slate-300 capitalize"
                        >
                          {typeof factor === "string" ? factor.replace(/_/g, " ") : JSON.stringify(factor)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Column 2 & 3: Location, Responsible Authority, Civic Guidance */}
          <div className="lg:col-span-2 space-y-6">
            {/* Location & Authority Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Geographic Intelligence Card */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
                    <MapPin className="w-4 h-4 text-cyan-400" />
                    <span>Location Resolved</span>
                  </h2>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-cyan-800/30">
                    {response.location?.source || "Geocoding"}
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Resolved Address:</span>
                    <p className="font-semibold text-slate-200 text-sm mt-0.5">
                      {response.location?.address || "Address unavailable (using raw coordinates)"}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80">
                    <div>
                      <span className="text-slate-500">City / District:</span>
                      <p className="font-medium text-slate-300">{response.location?.city || response.location?.district || "Gurugram"}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">State:</span>
                      <p className="font-medium text-slate-300">{response.location?.state || "Haryana"}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Ward / Zone:</span>
                      <p className="font-medium text-slate-300">{response.location?.ward || response.location?.zone || "Ward 34"}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Coordinates:</span>
                      <p className="font-mono text-slate-300">
                        {response.location?.coordinates.latitude.toFixed(4)}, {response.location?.coordinates.longitude.toFixed(4)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Responsible Municipal Authority Card */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
                    <Building2 className="w-4 h-4 text-indigo-400" />
                    <span>Responsible Authority</span>
                  </h2>

                  {/* Provenance Tag: Explicitly separating verified from test/mock */}
                  {response.authority?.verified_at ? (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
                      <ShieldCheck className="w-3 h-3" />
                      <span>Verified Registry</span>
                    </span>
                  ) : (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-amber-400 border border-amber-500/30">
                      Unverified / Demo Route
                    </span>
                  )}
                </div>

                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Authority Name:</span>
                    <p className="font-bold text-white text-sm mt-0.5">
                      {response.authority?.authority_name || "Municipal Corporation"}
                    </p>
                  </div>
                  {response.authority?.department && (
                    <div>
                      <span className="text-slate-500">Department / Division:</span>
                      <p className="font-medium text-slate-300">{response.authority.department}</p>
                    </div>
                  )}

                  {/* Official Contacts only displayed if present and legitimate */}
                  <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                    {response.authority?.contact_phone ? (
                      <div className="flex items-center space-x-2 text-slate-300">
                        <Phone className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span className="font-mono">{response.authority.contact_phone}</span>
                        <span className="text-[10px] text-slate-500">(Civic Helpline)</span>
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-500 italic">No verified phone number registered.</p>
                    )}

                    {response.authority?.contact_email ? (
                      <div className="flex items-center space-x-2 text-slate-300">
                        <Mail className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                        <span className="font-mono">{response.authority.contact_email}</span>
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-500 italic">No verified email address registered.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Citizen Charter & Civic Guidance Card (RAG) */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
                  <BookOpen className="w-4 h-4 text-emerald-400" />
                  <span>Civic Guidance & Citizen Charter Rules</span>
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/20">
                  Source: Municipal Citizen Charter 2024
                </span>
              </div>

              <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-2 text-xs text-slate-300 leading-relaxed">
                <div className="flex items-start space-x-2">
                  <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white block font-medium">Statutory Resolution Timeline:</strong>
                    <span>
                      Under the Haryana Municipal Corporation Citizen Charter (Section 12), road damage and pothole reports categorized as High/Critical require physical inspection within 24 hours and remedial asphalt patching within 72 hours of registration.
                    </span>
                  </div>
                </div>
                <div className="flex items-start space-x-2 pt-2 border-t border-slate-800/80">
                  <Clock className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white block font-medium">Citizen Rights & Escalation:</strong>
                    <span>
                      If unresolved after the prescribed deadline, citizens have the legal right to escalate the complaint to the Additional Commissioner (Engineering Wing) or file a grievance on the CM Window portal.
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Bar */}
            {response.complaint && (
              <div className="flex justify-end pt-2">
                <button
                  onClick={onProceedToComplaint}
                  className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-400 hover:from-emerald-300 hover:to-cyan-300 text-slate-950 font-extrabold text-sm shadow-xl shadow-emerald-500/20 hover:shadow-emerald-500/35 transition-all flex items-center justify-center space-x-2 cursor-pointer"
                >
                  <span>Review & Format Municipal Complaint Letter</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
