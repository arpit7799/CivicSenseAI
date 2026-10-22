"use client";

import React, { useState } from "react";
import Navbar from "@/components/Navbar";
import DashboardScreen from "@/components/DashboardScreen";
import ReportIssueScreen from "@/components/ReportIssueScreen";
import AnalysisResultsScreen from "@/components/AnalysisResultsScreen";
import ComplaintPreviewScreen from "@/components/ComplaintPreviewScreen";
import TrackingScreen from "@/components/TrackingScreen";
import TestMatrixScreen from "@/components/TestMatrixScreen";
import { AnalysisResponse, StoredComplaint } from "@/lib/types";

type Screen = "dashboard" | "report" | "results" | "complaint" | "tracking" | "matrix";

export default function Home() {
  const [activeScreen, setActiveScreen] = useState<Screen>("dashboard");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [imagePreview, setImagePreview] = useState<string>("");
  const [userDescription, setUserDescription] = useState<string>("");
  const [highlightedComplaintId, setHighlightedComplaintId] = useState<string | undefined>(undefined);

  const handleAnalysisSuccess = (
    response: AnalysisResponse,
    preview: string,
    description: string
  ) => {
    setAnalysisResult(response);
    setImagePreview(preview);
    setUserDescription(description);
    setActiveScreen("results");
  };

  const handleSubmitSuccess = (complaint: StoredComplaint) => {
    setHighlightedComplaintId(complaint.id);
    setActiveScreen("tracking");
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setImagePreview("");
    setUserDescription("");
    setActiveScreen("report");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-slate-950">
      <Navbar
        activeScreen={activeScreen}
        setActiveScreen={setActiveScreen}
        hasAnalysisResults={analysisResult !== null}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeScreen === "dashboard" && (
          <DashboardScreen
            onNavigateReport={() => setActiveScreen("report")}
            onNavigateTracking={() => setActiveScreen("tracking")}
            onNavigateMatrix={() => setActiveScreen("matrix")}
          />
        )}

        {activeScreen === "report" && (
          <ReportIssueScreen
            onAnalysisSuccess={handleAnalysisSuccess}
            onNavigateMatrix={() => setActiveScreen("matrix")}
          />
        )}

        {activeScreen === "results" && analysisResult && (
          <AnalysisResultsScreen
            response={analysisResult}
            imagePreview={imagePreview}
            onProceedToComplaint={() => setActiveScreen("complaint")}
            onReset={handleReset}
          />
        )}

        {activeScreen === "complaint" && analysisResult && (
          <ComplaintPreviewScreen
            response={analysisResult}
            imagePreview={imagePreview}
            onBackToResults={() => setActiveScreen("results")}
            onSubmitSuccess={handleSubmitSuccess}
          />
        )}

        {activeScreen === "tracking" && (
          <TrackingScreen
            onNavigateReport={() => setActiveScreen("report")}
            highlightedComplaintId={highlightedComplaintId}
          />
        )}

        {activeScreen === "matrix" && (
          <TestMatrixScreen onRunTestSuccess={handleAnalysisSuccess} />
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© 2026 CivicSense AI — Citizen Civic Intelligence & Complaint Redressal Portal</p>
          <div className="flex items-center space-x-4 text-slate-400">
            <span>YOLOv8 Computer Vision</span>
            <span>•</span>
            <span>Municipal RAG</span>
            <span>•</span>
            <span>FastAPI Backend</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
