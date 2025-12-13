/**
 * API Service Layer for Backend Integration
 * 
 * This module provides functions to interact with the backend API endpoints.
 * All API calls go through the Next.js proxy configured in next.config.ts
 */

import {
  CVExtractionResponse,
  CVClarificationRequest,
  CVClarificationResponse,
  JobExtractionResponse,
  JobURLRequest,
  JobTextRequest,
  CompanyResearchResponse,
  CompanyResearchRequest,
  CVJobAlignmentRequest,
  CVJobAlignmentResponse,
  GenerateTailoredCVRequest,
  GenerateTailoredCVResponse,
  GenerateCoverLetterRequest,
  GenerateCoverLetterResponse,
  SupervisorSessionInitResponse,
  SupervisorSessionResponse,
  SupervisorMessageRequest,
  ErrorResponse,
} from '@/types';

// ============================================
// API Configuration
// ============================================

const API_BASE_URL = '/api'; // Proxied through Next.js

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || errorData.error || 'API request failed',
        response.status,
        errorData.detail
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

// ============================================
// CV Agent API
// ============================================

/**
 * Upload CV PDF file for extraction
 */
export async function uploadCV(file: File): Promise<CVExtractionResponse> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/cv/upload`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header - browser will set it with boundary
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || 'CV upload failed',
        response.status,
        errorData.detail
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : 'Upload failed',
      0
    );
  }
}

/**
 * Submit clarifications for ambiguous CV data
 */
export async function clarifyCV(
  request: CVClarificationRequest
): Promise<CVClarificationResponse> {
  return apiFetch<CVClarificationResponse>('/cv/clarify', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Validate CV data structure
 */
export async function validateCVData(cvData: any): Promise<any> {
  return apiFetch<any>('/cv/validate', {
    method: 'POST',
    body: JSON.stringify(cvData),
  });
}

// ============================================
// Job Agent API
// ============================================

/**
 * Extract job requirements from URL(s)
 */
export async function extractJobFromURL(
  request: JobURLRequest
): Promise<JobExtractionResponse> {
  return apiFetch<JobExtractionResponse>('/job/extract-url', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Extract job requirements from pasted text
 */
export async function extractJobFromText(
  request: JobTextRequest
): Promise<JobExtractionResponse> {
  return apiFetch<JobExtractionResponse>('/job/extract-text', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Research company information
 */
export async function researchCompany(
  request: CompanyResearchRequest
): Promise<CompanyResearchResponse> {
  return apiFetch<CompanyResearchResponse>('/job/research-company', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// ============================================
// Writer Agent API
// ============================================

/**
 * Analyze CV-job alignment and get tailoring plan
 */
export async function analyzeAlignment(
  request: CVJobAlignmentRequest
): Promise<CVJobAlignmentResponse> {
  return apiFetch<CVJobAlignmentResponse>('/writer/analyze-alignment', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Generate tailored CV PDF
 */
export async function generateTailoredCV(
  request: GenerateTailoredCVRequest
): Promise<GenerateTailoredCVResponse> {
  return apiFetch<GenerateTailoredCVResponse>('/writer/generate-cv', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Generate cover letter PDF
 */
export async function generateCoverLetter(
  request: GenerateCoverLetterRequest
): Promise<GenerateCoverLetterResponse> {
  return apiFetch<GenerateCoverLetterResponse>('/writer/generate-cover-letter', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// ============================================
// Supervisor Agent API
// ============================================

/**
 * Start a new supervisor session
 */
export async function startSupervisorSession(): Promise<SupervisorSessionInitResponse> {
  return apiFetch<SupervisorSessionInitResponse>('/supervisor/session/start', {
    method: 'POST',
  });
}

/**
 * Send message to supervisor agent
 */
export async function sendSupervisorMessage(
  request: SupervisorMessageRequest
): Promise<SupervisorSessionResponse> {
  return apiFetch<SupervisorSessionResponse>('/supervisor/session/message', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Get current session state
 */
export async function getSupervisorSessionState(
  sessionId: string
): Promise<any> {
  return apiFetch<any>(`/supervisor/session/${sessionId}/state`, {
    method: 'GET',
  });
}

// ============================================
// File Download API
// ============================================

/**
 * Download generated file (CV or cover letter)
 */
export async function downloadFile(filename: string): Promise<Blob> {
  try {
    const response = await fetch(`${API_BASE_URL}/files/${filename}`);

    if (!response.ok) {
      throw new APIError('File download failed', response.status);
    }

    return await response.blob();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : 'Download failed',
      0
    );
  }
}

/**
 * Helper to trigger browser download
 */
export function triggerFileDownload(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

// ============================================
// Health Check
// ============================================

/**
 * Check API health status
 */
export async function healthCheck(): Promise<any> {
  return apiFetch<any>('/health', {
    method: 'GET',
  });
}

// ============================================
// Error Handling Utilities
// ============================================

export function isAPIError(error: unknown): error is APIError {
  return error instanceof APIError;
}

export function getErrorMessage(error: unknown): string {
  if (isAPIError(error)) {
    return error.detail || error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}

export { APIError };

