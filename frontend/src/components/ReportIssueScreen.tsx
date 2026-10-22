"use client";

import React, { useState } from "react";
import { 
  Upload, 
  MapPin, 
  Compass, 
  AlertTriangle, 
  FileCheck2, 
  Sparkles, 
  Camera, 
  X, 
  Info,
  Loader2,
  CheckCircle2
} from "lucide-react";
import { AnalysisRequest, AnalysisResponse } from "@/lib/types";
import { analyzeCivicIssue } from "@/lib/api";
import { getSamplePresets, getPresetDataUrl } from "@/lib/sampleImages";

interface ReportIssueScreenProps {
  onAnalysisSuccess: (response: AnalysisResponse, imagePreview: string, userDescription: string) => void;
  onNavigateMatrix: () => void;
}

export default function ReportIssueScreen({ onAnalysisSuccess, onNavigateMatrix }: ReportIssueScreenProps) {
  // Form State
  const [imagePreview, setImagePreview] = useState<string>("");
  const [latitude, setLatitude] = useState<number>(28.4595); // Default Gurugram Sector 34
  const [longitude, setLongitude] = useState<number>(77.0266);
  const [description, setDescription] = useState<string>("");
  const [isGettingLocation, setIsGettingLocation] = useState<boolean>(false);
  const [locationSuccessMsg, setLocationSuccessMsg] = useState<string>("");

  // Validation & Loading State
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisStage, setAnalysisStage] = useState<string>("");

  // Handle local file selection
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValidationError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setValidationError("Please select a valid image file (JPG, PNG, WebP).");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setValidationError("Image file size exceeds 10MB limit.");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setImagePreview(reader.result as string);
    };
    reader.onerror = () => {
      setValidationError("Failed to read image file. Please try another image.");
    };
    reader.readAsDataURL(file);
  };

  // Quick preset loader
  const handleSelectPreset = (type: "pothole" | "garbage" | "streetlight" | "clean" | "blurry") => {
    setValidationError(null);
    const dataUrl = getPresetDataUrl(type);
    setImagePreview(dataUrl);

    if (type === "pothole") {
      setDescription("Large deep pothole on main transit road posing severe hazard to two-wheelers.");
      setLatitude(28.4595);
      setLongitude(77.0266);
    } else if (type === "garbage") {
      setDescription("Massive uncollected garbage accumulation overflowing near residential entrance.");
      setLatitude(28.4610);
      setLongitude(77.0315);
    } else if (type === "streetlight") {
      setDescription("Streetlight fixture broken and pole damaged with exposed cables.");
      setLatitude(28.4720);
      setLongitude(77.0420);
    } else if (type === "clean") {
      setDescription("Normal clean asphalt roadway with regular painted lane markers.");
      setLatitude(28.4595);
      setLongitude(77.0266);
    } else if (type === "blurry") {
      setDescription("Out of focus picture taken while driving.");
      setLatitude(28.4595);
      setLongitude(77.0266);
    }
  };

  // Obtain coordinates with browser geolocation
  const handleGetGPS = () => {
    if (!navigator.geolocation) {
      setValidationError("Geolocation is not supported by your browser. Please enter coordinates manually.");
      return;
    }

    setIsGettingLocation(true);
    setLocationSuccessMsg("");
    setValidationError(null);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = parseFloat(pos.coords.latitude.toFixed(6));
        const lon = parseFloat(pos.coords.longitude.toFixed(6));
        setLatitude(lat);
        setLongitude(lon);
        setIsGettingLocation(false);
        setLocationSuccessMsg(`Obtained GPS coordinates (${lat}, ${lon}) with accuracy ~${Math.round(pos.coords.accuracy)}m`);
      },
      (err) => {
        setIsGettingLocation(false);
        setValidationError(`GPS permission denied or unavailable (${err.message}). Using manual coordinates.`);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  // Submit and analyze
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!imagePreview) {
      setValidationError("Please upload a photograph of the civic issue or select a test preset.");
      return;
    }

    if (isNaN(latitude) || latitude < -90 || latitude > 90) {
      setValidationError("Latitude must be a valid number between -90 and 90.");
      return;
    }

    if (isNaN(longitude) || longitude < -180 || longitude > 180) {
      setValidationError("Longitude must be a valid number between -180 and 180.");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisStage("1. Validating image resolution & quality checks...");

    try {
      const stageTimer1 = setTimeout(() => {
        setAnalysisStage("2. Running YOLOv8 Vision Detection & Confidence Scoring...");
      }, 700);

      const stageTimer2 = setTimeout(() => {
        setAnalysisStage("3. Computing Multi-Factor Severity & Risk Breakdown...");
      }, 1500);

      const stageTimer3 = setTimeout(() => {
        setAnalysisStage("4. Resolving Geographic Jurisdiction & Authority Contacts...");
      }, 2300);

      const stageTimer4 = setTimeout(() => {
        setAnalysisStage("5. Formulating Civic Complaint Letter & RAG Charter Check...");
      }, 3100);

      const payload: AnalysisRequest = {
        image_url: imagePreview,
        latitude,
        longitude,
        user_description: description.trim() || undefined,
      };

      const result = await analyzeCivicIssue(payload);

      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      clearTimeout(stageTimer3);
      clearTimeout(stageTimer4);

      setIsAnalyzing(false);
      onAnalysisSuccess(result, imagePreview, description);
    } catch (err: unknown) {
      setIsAnalyzing(false);
      const errMsg = err instanceof Error ? err.message : "Analysis request failed. Please check backend connection.";
      setValidationError(errMsg);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="border-b border-slate-800 pb-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
              <span>Report a Civic Issue</span>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Interactive Testing
              </span>
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Submit a real photograph or select a benchmark sample to run multimodal AI detection, severity analysis, and civic complaint generation.
            </p>
          </div>
          <button
            onClick={onNavigateMatrix}
            className="hidden sm:flex items-center space-x-1.5 text-xs text-indigo-400 bg-indigo-950/60 hover:bg-indigo-900/60 border border-indigo-700/50 px-3 py-1.5 rounded-lg transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Open Test Matrix</span>
          </button>
        </div>
      </div>

      {/* Validation Error Alert */}
      {validationError && (
        <div className="bg-red-950/60 border border-red-500/40 text-red-200 px-4 py-3 rounded-xl flex items-start space-x-3 shadow-lg">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-semibold text-red-300">Validation Issue</p>
            <p className="mt-0.5 text-red-200/90">{validationError}</p>
          </div>
          <button
            onClick={() => setValidationError(null)}
            className="ml-auto text-red-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Image Upload & Preview */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <Camera className="w-4 h-4 text-emerald-400" />
              <span>Step 1: Civic Issue Photograph</span>
              <span className="text-xs text-rose-400">*required</span>
            </label>
            {imagePreview && (
              <button
                type="button"
                onClick={() => setImagePreview("")}
                className="text-xs text-slate-400 hover:text-rose-400 flex items-center space-x-1"
              >
                <X className="w-3.5 h-3.5" />
                <span>Clear image</span>
              </button>
            )}
          </div>

          {/* Preset Buttons for Quick Testing */}
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="text-slate-400 py-1 font-medium">Quick Presets:</span>
            <button
              type="button"
              onClick={() => handleSelectPreset("pothole")}
              className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-emerald-950 text-slate-300 hover:text-emerald-300 border border-slate-700 hover:border-emerald-500/40 transition-colors"
            >
              🚧 Pothole (Gurugram)
            </button>
            <button
              type="button"
              onClick={() => handleSelectPreset("garbage")}
              className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-amber-950 text-slate-300 hover:text-amber-300 border border-slate-700 hover:border-amber-500/40 transition-colors"
            >
              🗑️ Garbage Dump
            </button>
            <button
              type="button"
              onClick={() => handleSelectPreset("streetlight")}
              className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-blue-950 text-slate-300 hover:text-blue-300 border border-slate-700 hover:border-blue-500/40 transition-colors"
            >
              💡 Broken Streetlight
            </button>
            <button
              type="button"
              onClick={() => handleSelectPreset("clean")}
              className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition-colors"
            >
              🛣️ Clean Road (Rejection Test)
            </button>
            <button
              type="button"
              onClick={() => handleSelectPreset("blurry")}
              className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-purple-950 text-slate-400 hover:text-purple-300 border border-slate-700 hover:border-purple-500/40 transition-colors"
            >
              🌫️ Blurry Image (Quality Check)
            </button>
          </div>

          {/* Upload Dropzone & Preview Box */}
          {!imagePreview ? (
            <label className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer bg-slate-950/40 hover:bg-slate-800/40 transition-all group">
              <div className="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-emerald-400 group-hover:scale-105 transition-all shadow-inner">
                <Upload className="w-7 h-7" />
              </div>
              <p className="mt-4 text-sm font-medium text-slate-200">
                Click to browse or drop photograph here
              </p>
              <p className="mt-1 text-xs text-slate-400">
                Supports real JPG, PNG, WebP photographs up to 10MB
              </p>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          ) : (
            <div className="relative rounded-xl overflow-hidden border border-slate-700 bg-slate-950/60 flex items-center justify-center max-h-96">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={imagePreview}
                alt="Civic issue preview"
                className="max-h-96 w-auto object-contain"
              />
              <div className="absolute bottom-2 left-2 bg-slate-900/90 border border-slate-700 px-3 py-1 rounded-lg text-xs text-slate-300 flex items-center space-x-1.5 shadow-md">
                <FileCheck2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Image loaded & ready for vision inference</span>
              </div>
            </div>
          )}
        </div>

        {/* Step 2: Location Settings */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <label className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-cyan-400" />
              <span>Step 2: Incident Coordinates</span>
              <span className="text-xs text-rose-400">*required</span>
            </label>
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={handleGetGPS}
                disabled={isGettingLocation}
                className="flex items-center space-x-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-cyan-950/70 text-cyan-300 border border-cyan-700/50 hover:bg-cyan-900/70 transition-colors disabled:opacity-50"
              >
                <Compass className={`w-3.5 h-3.5 ${isGettingLocation ? "animate-spin" : ""}`} />
                <span>{isGettingLocation ? "Locating..." : "Use My GPS"}</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setLatitude(28.4595);
                  setLongitude(77.0266);
                  setLocationSuccessMsg("Preset coordinates set: Gurugram Sector 34");
                }}
                className="text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 transition-colors"
              >
                Reset Gurugram Default
              </button>
            </div>
          </div>

          {locationSuccessMsg && (
            <div className="text-xs text-emerald-400 flex items-center space-x-1.5 bg-emerald-950/30 border border-emerald-500/20 px-3 py-1.5 rounded-lg">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{locationSuccessMsg}</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <span className="block text-xs font-medium text-slate-400 mb-1">
                Latitude (°N)
              </span>
              <input
                type="number"
                step="0.000001"
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value))}
                placeholder="e.g. 28.459500"
                className="w-full bg-slate-950 border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 transition-colors"
                required
              />
            </div>
            <div>
              <span className="block text-xs font-medium text-slate-400 mb-1">
                Longitude (°E)
              </span>
              <input
                type="number"
                step="0.000001"
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value))}
                placeholder="e.g. 77.026600"
                className="w-full bg-slate-950 border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 transition-colors"
                required
              />
            </div>
          </div>
          <p className="text-xs text-slate-500 flex items-center space-x-1">
            <Info className="w-3.5 h-3.5 shrink-0" />
            <span>
              Geographic reverse resolution identifies the state, city, and jurisdiction department (Municipal Corporation of Gurugram for Haryana coordinates).
            </span>
          </p>
        </div>

        {/* Step 3: Description Input */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm space-y-4">
          <label className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
            <span>Step 3: Citizen Problem Description</span>
            <span className="text-xs text-slate-400">(optional)</span>
          </label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Explain the problem (e.g. 'Near Sector 34 junction, water accumulation inside pothole causing traffic obstruction')..."
            className="w-full bg-slate-950 border border-slate-700 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 transition-colors resize-none"
          />
        </div>

        {/* Action Button & Live Pipeline Indicator */}
        <div className="pt-2">
          {isAnalyzing ? (
            <div className="bg-slate-900 border border-emerald-500/40 rounded-2xl p-6 shadow-2xl text-center space-y-3">
              <div className="flex items-center justify-center space-x-2 text-emerald-400">
                <Loader2 className="w-6 h-6 animate-spin" />
                <span className="font-bold text-base">CivicSense AI Pipeline Executing</span>
              </div>
              <p className="text-sm font-medium text-slate-200">{analysisStage}</p>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-gradient-to-r from-emerald-500 via-cyan-500 to-indigo-500 h-2 animate-pulse w-full" />
              </div>
              <p className="text-xs text-slate-400">
                Evaluating vision model, checking duplicates, resolving jurisdiction, and drafting municipal complaint letter.
              </p>
            </div>
          ) : (
            <button
              type="submit"
              className="w-full py-4 px-6 rounded-xl font-bold text-base text-slate-950 bg-gradient-to-r from-emerald-400 to-cyan-400 hover:from-emerald-300 hover:to-cyan-300 shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transform active:scale-[0.99] transition-all flex items-center justify-center space-x-2 cursor-pointer"
            >
              <Sparkles className="w-5 h-5 font-bold" />
              <span>Analyze Civic Issue with AI</span>
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
