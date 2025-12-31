// ============================================
// Core Types
// ============================================

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  generatedFiles?: DownloadableFile[] | null;
}

// ============================================
// CV Agent Types (matching backend schemas)
// ============================================

export interface ResumeInfo {
  name: string;
  email: string;
  phone: string;
  location?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  skills: string[];
  education: string[];
  experience: string[];
  projects?: string[];
  leadership_activities?: string[];
}

export interface CVExtractionResponse {
  success: boolean;
  cv_data?: ResumeInfo;
  needs_clarification: boolean;
  questions?: string[];
  message: string;
}

export interface CVClarificationRequest {
  cv_data: Record<string, any>;
  clarifications: string;
}

export interface CVClarificationResponse {
  success: boolean;
  updated_cv_data?: ResumeInfo;
  message: string;
}

// ============================================
// Job Agent Types
// ============================================

export interface JobRequirements {
  job_title: string;
  job_level: string;
  required_skills: string[];
  preferred_skills: string[];
  years_experience?: number;
  employment_type: string;
  location: string;
  responsibilities: string[];
  qualifications: string[];
  key_requirements: string[];
}

export interface JobExtractionResponse {
  success: boolean;
  job_data?: JobRequirements;
  message: string;
}

export interface CompanyInfo {
  company_name: string;
  industry: string;
  company_size?: string;
  mission_statement?: string;
  core_values: string[];
  recent_news: string[];
  company_culture: string;
  products_services: string[];
}

export interface CompanyResearchResponse {
  success: boolean;
  company_data?: CompanyInfo;
  message: string;
}

// ============================================
// Writer Agent Types
// ============================================

export interface CVTailoringPlan {
  matching_experiences: string[];
  matching_skills: string[];
  relevant_projects: string[];
  keywords_to_incorporate: string[];
  reordering_suggestions: string;
  emphasis_points: string[];
  reasoning: string;
}

export interface CVJobAlignmentResponse {
  success: boolean;
  tailoring_plan?: CVTailoringPlan;
  message: string;
}

export interface GenerateTailoredCVResponse {
  success: boolean;
  pdf_path?: string;
  html_preview?: string;
  message: string;
}

export interface CoverLetterContent {
  opening_paragraph: string;
  body_paragraph_1: string;
  body_paragraph_2: string;
  body_paragraph_3?: string;
  closing_paragraph: string;
}

export interface GenerateCoverLetterResponse {
  success: boolean;
  pdf_path?: string;
  content?: CoverLetterContent;
  message: string;
}

// ============================================
// Error Types
// ============================================

export interface ErrorResponse {
  success: boolean;
  error: string;
  detail?: string;
}

// ============================================
// API Request Types
// ============================================

export interface JobURLRequest {
  urls: string[];
}

export interface JobTextRequest {
  job_text: string;
}

export interface CVJobAlignmentRequest {
  cv_data: Record<string, any>;
  job_data: Record<string, any>;
}

export interface GenerateTailoredCVRequest {
  cv_data: Record<string, any>;
  tailoring_plan: Record<string, any>;
  output_filename: string;
}

export interface GenerateCoverLetterRequest {
  cv_data: Record<string, any>;
  job_data: Record<string, any>;
  company_data?: Record<string, any>;
  output_filename: string;
  recipient_info?: string;
}

export interface CompanyResearchRequest {
  company_name: string;
}

// ============================================
// Writer Chat Types (New)
// ============================================

export interface WriterChatSessionInitRequest {
  cv_data: ResumeInfo;
  job_data?: JobRequirements;
  mode: 'resume_refinement' | 'job_tailoring';
}

export interface WriterChatSessionInitResponse {
  success: boolean;
  session_id: string;
  initial_message: string;
  message: string;
}

export interface WriterChatMessageRequest {
  session_id: string;
  user_message: string;
}

export interface DownloadableFile {
  filename: string;
  file_type: string;
  download_url: string;
}

export interface WriterChatMessageResponse {
  success: boolean;
  assistant_message: string;
  requires_approval: boolean;
  preview_content?: string | null;
  generated_files?: DownloadableFile[] | null;
  message: string;
}

export interface ResumeSummaryRequest {
  cv_data: ResumeInfo;
}

export interface ResumeSummaryResponse {
  success: boolean;
  summary: string;
  suggestions?: string[] | null;
  message: string;
}

// ============================================
// Audio Transcription Types
// ============================================

export type TranscriptionModel = 
  | 'whisper-1' 
  | 'gpt-4o-transcribe' 
  | 'gpt-4o-mini-transcribe' 
  | 'gpt-4o-transcribe-diarize';

export type TranscriptionResponseFormat = 
  | 'json' 
  | 'text' 
  | 'srt' 
  | 'verbose_json' 
  | 'vtt' 
  | 'diarized_json';

export interface TranscriptionRequest {
  file: File;
  model?: TranscriptionModel;
  response_format?: TranscriptionResponseFormat;
  language?: string;
  prompt?: string;
  temperature?: number;
  timestamp_granularities?: ('word' | 'segment')[];
  chunking_strategy?: 'auto';
}

export interface TranscriptionSegment {
  id: number;
  seek: number;
  start: number;
  end: number;
  text: string;
  tokens: number[];
  temperature: number;
  avg_logprob: number;
  compression_ratio: number;
  no_speech_prob: number;
  speaker?: string; // For diarized_json format
}

export interface TranscriptionWord {
  word: string;
  start: number;
  end: number;
}

export interface TranscriptionResponse {
  success: boolean;
  text?: string | null;
  segments?: TranscriptionSegment[] | null;
  words?: TranscriptionWord[] | null;
  message: string;
}

export interface TranslationRequest {
  file: File;
  model?: 'whisper-1';
  response_format?: 'json' | 'text' | 'srt' | 'verbose_json' | 'vtt';
  prompt?: string;
  temperature?: number;
}

export interface TranslationResponse {
  success: boolean;
  text?: string | null;
  segments?: TranscriptionSegment[] | null;
  words?: TranscriptionWord[] | null;
  message: string;
}

// ============================================
// Application State Types
// ============================================

export interface ApplicationState {
  sessionId?: string;
  cvData?: ResumeInfo;
  jobData?: JobRequirements;
  companyData?: CompanyInfo;
  tailoringPlan?: CVTailoringPlan;
  generatedFiles: GeneratedFile[];
}

export interface GeneratedFile {
  id: string;
  filename: string;
  type: 'cv' | 'cover_letter';
  path: string;
  timestamp: Date;
}
