"use client";

import React, { useState } from "react";
import {
  Play,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Sparkles,
  Layers,
  ArrowRight,
  ShieldAlert,
  Loader2,
} from "lucide-react";
import { analyzeCivicIssue } from "@/lib/api";
import { getPresetDataUrl } from "@/lib/sampleImages";
import { AnalysisRequest, AnalysisResponse } from "@/lib/types";

interface TestMatrixScreenProps {
  onRunTestSuccess: (response: AnalysisResponse, imagePreview: string, userDescription: string) => void;
}

interface TestCase {
  id: string;
  title: string;
  category: "Vision" | "Validation" | "Geographic" | "LLM & RAG" | "Integration";
  description: string;
  expectedBehavior: string;
  requestBuilder: () => AnalysisRequest;
  imagePreview: string;
}

export default function TestMatrixScreen({ onRunTestSuccess }: TestMatrixScreenProps) {
  const [runningTestId, setRunningTestId] = useState<string | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  const testCases: TestCase[] = [
    {
      id: "tc-01-pothole",
      title: "1. Clear Pothole Photograph",
      category: "Vision",
      description: "Asphalt crater on Gurugram arterial road Sector 34.",
      expectedBehavior: "Detects pothole with high confidence, triggers HIGH/CRITICAL severity, routes to Municipal Corp. of Gurugram.",
      imagePreview: getPresetDataUrl("pothole"),
      requestBuilder: () => ({
        image_url: getPresetDataUrl("pothole"),
        latitude: 28.4595,
        longitude: 77.0266,
        user_description: "Large deep pothole on main transit road posing severe hazard to two-wheelers.",
      }),
    },
    {
      id: "tc-02-garbage",
      title: "2. Garbage Accumulation",
      category: "Vision",
      description: "Overflowing commercial garbage heap spilling onto pedestrian walkway.",
      expectedBehavior: "Identifies garbage class, calculates sanitation severity factor, and drafts cleanup action order.",
      imagePreview: getPresetDataUrl("garbage"),
      requestBuilder: () => ({
        image_url: getPresetDataUrl("garbage"),
        latitude: 28.4610,
        longitude: 77.0315,
        user_description: "Uncollected municipal waste overflowing across residential street.",
      }),
    },
    {
      id: "tc-03-non-civic",
      title: "3. Non-Civic Image (Clean Road)",
      category: "Vision",
      description: "Clean asphalt roadway without defects, potholes, or trash.",
      expectedBehavior: "Short-circuits with status 'rejected_no_civic_issue' to prevent false reports.",
      imagePreview: getPresetDataUrl("clean"),
      requestBuilder: () => ({
        image_url: getPresetDataUrl("clean"),
        latitude: 28.4595,
        longitude: 77.0266,
        user_description: "Normal maintained roadway.",
      }),
    },
    {
      id: "tc-04-blurry",
      title: "4. Blurry Photograph",
      category: "Validation",
      description: "Extremely blurred capture taken from moving vehicle.",
      expectedBehavior: "Vision diagnostics flags high blur score and explains image-quality problem.",
      imagePreview: getPresetDataUrl("blurry"),
      requestBuilder: () => ({
        image_url: getPresetDataUrl("blurry"),
        latitude: 28.4595,
        longitude: 77.0266,
        user_description: "Blurry snapshot taken while driving.",
      }),
    },
    {
      id: "tc-05-invalid-coords",
      title: "5. Invalid Coordinates",
      category: "Validation",
      description: "Out-of-range latitude (999.0, 999.0).",
      expectedBehavior: "FastAPI contract validation rejects invalid request with clear error message.",
      imagePreview: getPresetDataUrl("pothole"),
      requestBuilder: () => ({
        image_url: getPresetDataUrl("pothole"),
        latitude: 999.0,
        longitude: 999.0,
        user_description: "Invalid coordinates test.",
      }),
    },
    {
      id: "tc-06-remote-coords",
      title: "6. Location Service Fallback",
      category: "Geographic",
      description: "Valid coordinates in remote unmapped coordinates.",
      expectedBehavior: "Returns partial result with raw coordinates without inventing an address.",
      imagePreview: getPresetDataUrl("pothole"),
      requestBuilder: () => ({
        image_url: getPresetDataUrl("pothole"),
        latitude: 15.1234,
        longitude: 75.1234,
        user_description: "Rural unmapped road section.",
      }),
    },
    {
      id: "tc-07-duplicate",
      title: "7. Potential Duplicate Complaint",
      category: "Integration",
      description: "Second report submitted at the exact same location as existing complaint.",
      expectedBehavior: "Duplicate check flags 'is_potential_duplicate: true' and displays warning with similarity score.",
      imagePreview: getPresetDataUrl("pothole"),
      requestBuilder: () => ({
        image_url: getPresetDataUrl("pothole"),
        latitude: 28.4595,
        longitude: 77.0266,
        user_description: "Repeated complaint for the same Sector 34 pothole.",
      }),
    },
    {
      id: "tc-08-unverified-auth",
      title: "8. Unverified Authority Tagging",
      category: "Integration",
      description: "Geographic area without verified municipal database record.",
      expectedBehavior: "Marks authority explicitly as Unverified/Demo and never presents invented phone numbers as genuine.",
      imagePreview: getPresetDataUrl("streetlight"),
      requestBuilder: () => ({
        image_url: getPresetDataUrl("streetlight"),
        latitude: 24.1234,
        longitude: 82.5678,
        user_description: "Remote area streetlight issue.",
      }),
    },
  ];

  const handleRunTestCase = async (tc: TestCase) => {
    setTestError(null);
    setRunningTestId(tc.id);

    try {
      const payload = tc.requestBuilder();
      const response = await analyzeCivicIssue(payload);
      setRunningTestId(null);
      onRunTestSuccess(response, tc.imagePreview, payload.user_description || "");
    } catch (err: unknown) {
      setRunningTestId(null);
      const msg = err instanceof Error ? err.message : "Test execution failed";
      setTestError(`Test Case "${tc.title}" returned error: ${msg}`);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <span>Interactive Functional Testing Matrix</span>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            10 Test Scenarios
          </span>
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Execute benchmark test cases against the live FastAPI backend to verify vision classification, error rejections, severity scoring, and LLM drafting.
        </p>
      </div>

      {testError && (
        <div className="bg-red-950/60 border border-red-500/40 text-red-200 px-4 py-3 rounded-xl flex items-start space-x-3 shadow-lg text-sm">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-300">Test Execution Output</p>
            <p className="mt-0.5 text-red-200/90">{testError}</p>
          </div>
        </div>
      )}

      {/* Grid of Test Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {testCases.map((tc) => {
          const isRunning = runningTestId === tc.id;
          return (
            <div
              key={tc.id}
              className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider bg-slate-800 text-indigo-300 border border-indigo-800/40">
                    {tc.category}
                  </span>
                  {tc.id === "tc-03-non-civic" ? (
                    <span className="text-[11px] text-slate-400 font-mono">Status: Reject expected</span>
                  ) : (
                    <span className="text-[11px] text-emerald-400 font-mono">Status: Complete expected</span>
                  )}
                </div>

                <h3 className="text-base font-bold text-white">{tc.title}</h3>
                <p className="text-xs text-slate-300">{tc.description}</p>

                <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 text-xs text-slate-400 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">
                    Expected Behavior
                  </span>
                  <p className="text-slate-300 text-[11px] leading-relaxed">{tc.expectedBehavior}</p>
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => handleRunTestCase(tc)}
                  disabled={isRunning || runningTestId !== null}
                  className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
                >
                  {isRunning ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Executing Test...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Run Test Case Live</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
