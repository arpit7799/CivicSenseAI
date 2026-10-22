// =============================================================================
// CivicSense AI — Frontend API Client
// =============================================================================

import { AnalysisRequest, AnalysisResponse, HealthResponse, StoredComplaint } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function checkBackendHealth(): Promise<HealthResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    console.warn("Backend health check failed:", error);
    return null;
  }
}

export async function analyzeCivicIssue(request: AnalysisRequest): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData.detail || `Analysis failed with HTTP status ${res.status}`;
    throw new Error(message);
  }

  return await res.json();
}

export async function fetchCivicHotspots(lat: number, lon: number, radiusKm: number = 10) {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/hotspots`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        center_latitude: lat,
        center_longitude: lon,
        radius_km: radiusKm,
      }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.warn("Failed to fetch hotspots:", e);
    return null;
  }
}

export async function fetchCivicTrends(region: string = "Gurugram", daysBack: number = 30) {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/trends`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        region,
        days_back: daysBack,
      }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.warn("Failed to fetch trends:", e);
    return null;
  }
}

// Local storage management for submitted complaints
const STORAGE_KEY = "civicsense_complaints_v1";

export function getStoredComplaints(): StoredComplaint[] {
  if (typeof window === "undefined") return [];
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    console.error("Failed to read complaints from storage:", e);
    return [];
  }
}

export function saveComplaint(complaint: StoredComplaint): void {
  if (typeof window === "undefined") return;
  try {
    const list = getStoredComplaints();
    const updated = [complaint, ...list.filter((c) => c.id !== complaint.id)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (e) {
    console.error("Failed to save complaint:", e);
  }
}
