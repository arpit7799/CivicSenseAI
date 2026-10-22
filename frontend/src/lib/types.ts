// =============================================================================
// CivicSense AI — Frontend TypeScript API Contracts
// =============================================================================
// Mirrors the backend Pydantic schemas from app.contracts.*
// =============================================================================

export interface AnalysisRequest {
  image_url: string;
  latitude: number;
  longitude: number;
  user_description?: string;
}

export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface Detection {
  issue_class: string;
  confidence: number;
  bounding_box: BoundingBox;
}

export interface ImageQuality {
  is_valid: boolean;
  resolution_adequate: boolean;
  blur_score: number;
  overall_quality_score: number;
  issues: string[];
}

export interface VisionResult {
  detections: Detection[];
  primary_issue: Detection | null;
  secondary_issues: Detection[];
  image_quality: ImageQuality;
  classification_status: string;
  processing_time_ms: number;
  model_version: string;
  source: string;
}

export interface SeverityContributingFactor {
  name: string;
  weight: number;
  description: string;
}

export interface SeverityResult {
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  score: number;
  factors?: string[];
  confidence: number;
  source: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface LocationResult {
  address?: string | null;
  city?: string | null;
  district?: string | null;
  state?: string | null;
  ward?: string | null;
  zone?: string | null;
  pincode?: string | null;
  coordinates: Coordinates;
  confidence: number;
  source: string;
}

export interface AuthorityResult {
  authority_name: string;
  department?: string | null;
  jurisdiction?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  office_address?: string | null;
  confidence: number;
  source: string;
  source_reference?: string | null;
  verified_at?: string | null;
}

export interface ComplaintResult {
  subject: string;
  body: string;
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  requested_action?: string | null;
  generated_at: string;
  source: string;
}

export interface DuplicateResult {
  is_potential_duplicate: boolean;
  existing_complaint_id?: string | null;
  similarity_score: number;
  match_factors: string[];
  source: string;
}

export interface AnalysisMetadata {
  request_id: string;
  processing_time_ms: number;
  api_version: string;
  providers: Record<string, string>;
}

export interface IssueInfo {
  type: string;
  confidence: number;
}

export interface AnalysisResponse {
  request_id: string;
  status: "completed" | "partial" | "rejected_no_civic_issue" | "failed";
  issue: IssueInfo;
  severity: SeverityResult | null;
  location: LocationResult | null;
  authority: AuthorityResult | null;
  complaint: ComplaintResult | null;
  duplicate_check: DuplicateResult | null;
  vision_details: VisionResult;
  metadata: AnalysisMetadata;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  provider_mode?: string;
  providers: Record<string, string>;
}

export interface StoredComplaint {
  id: string;
  reference_no: string;
  issue_type: string;
  severity: string;
  address: string;
  city: string;
  authority_name: string;
  contact_phone?: string | null;
  subject: string;
  body: string;
  created_at: string;
  status: "Draft Ready" | "Dispatched" | "In Review" | "Resolved";
  image_preview?: string;
}
