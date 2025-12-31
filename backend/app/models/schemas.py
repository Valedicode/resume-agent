"""
API Request and Response Models

This module defines all Pydantic models used for API communication.
These models provide validation, serialization, and documentation for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal


# ============================================
# CV Agent Models
# ============================================

class CVUploadRequest(BaseModel):
    """Request to extract CV information from a PDF file."""
    pdf_path: str = Field(
        ...,
        description="Path to the PDF resume file",
        example="C:/Documents/resume.pdf"
    )


class ResumeInfo(BaseModel):
    """Structured resume information extracted from CV."""
    name: str = Field(description="Full name of the applicant")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    location: Optional[str] = Field(
        default=None,
        description="Location (city, state, country, or full address)"
    )
    github_url: Optional[str] = Field(
        default=None,
        description="GitHub profile URL"
    )
    linkedin_url: Optional[str] = Field(
        default=None,
        description="LinkedIn profile URL"
    )
    portfolio_url: Optional[str] = Field(
        default=None,
        description="Personal portfolio or website URL"
    )
    skills: List[str] = Field(description="List of professional skills")
    education: List[str] = Field(description="Educational qualifications")
    experience: List[str] = Field(description="Work experience entries")
    projects: List[str] = Field(description="List of projects the applicant has worked on")
    leadership_activities: Optional[List[str]] = Field(
        default=[],
        description="Leadership roles, extracurricular activities, volunteer work, or other relevant activities"
    )


class CVExtractionResponse(BaseModel):
    """Response from CV extraction."""
    success: bool
    cv_data: Optional[ResumeInfo] = None
    needs_clarification: bool = False
    questions: Optional[List[str]] = None
    message: str


class CVClarificationRequest(BaseModel):
    """Request to update CV with clarification answers."""
    cv_data: Dict[str, Any] = Field(description="Original CV data as JSON")
    clarifications: str = Field(description="User's answers to clarifying questions")


class CVClarificationResponse(BaseModel):
    """Response from CV clarification."""
    success: bool
    updated_cv_data: Optional[ResumeInfo] = None
    message: str


# ============================================
# Job Agent Models
# ============================================

class JobURLRequest(BaseModel):
    """Request to extract job information from URL."""
    urls: List[str] = Field(
        ...,
        description="List of job posting URLs",
        example=["https://example.com/careers/job/123"]
    )


class JobTextRequest(BaseModel):
    """Request to extract job information from pasted text."""
    job_text: str = Field(
        ...,
        description="Raw job posting text",
        example="We are looking for a Senior Software Engineer..."
    )


class JobRequirements(BaseModel):
    """Structured job requirements extracted from posting."""
    job_title: str = Field(description="Job title")
    job_level: str = Field(description="Experience level (entry, mid, senior, etc.)")
    required_skills: List[str] = Field(description="Required technical skills")
    preferred_skills: List[str] = Field(default=[], description="Preferred skills")
    years_experience: Optional[int] = Field(default=None, description="Years of experience required")
    employment_type: str = Field(description="Employment type (Full-time, Contract, etc.)")
    location: str = Field(description="Job location")
    responsibilities: List[str] = Field(description="Key responsibilities")
    qualifications: List[str] = Field(default=[], description="Required qualifications")
    key_requirements: List[str] = Field(description="Critical must-have requirements")


class JobExtractionResponse(BaseModel):
    """Response from job extraction."""
    success: bool
    job_data: Optional[JobRequirements] = None
    message: str


class CompanyResearchRequest(BaseModel):
    """Request to research company information."""
    company_name: str = Field(
        ...,
        description="Name of the company to research",
        example="Google"
    )


class CompanyInfo(BaseModel):
    """Structured company information from research."""
    company_name: str = Field(description="Official company name")
    industry: str = Field(description="Industry sector")
    company_size: Optional[str] = Field(default=None, description="Company size category")
    mission_statement: Optional[str] = Field(default=None, description="Mission statement")
    core_values: List[str] = Field(description="Core values and principles")
    recent_news: List[str] = Field(default=[], description="Recent news and developments")
    company_culture: str = Field(description="Company culture description")
    products_services: List[str] = Field(default=[], description="Main products or services")


class CompanyResearchResponse(BaseModel):
    """Response from company research."""
    success: bool
    company_data: Optional[CompanyInfo] = None
    message: str


# ============================================
# Writer Agent Models
# ============================================

class CVJobAlignmentRequest(BaseModel):
    """Request to analyze CV-job alignment."""
    cv_data: Dict[str, Any] = Field(description="Resume data from CV agent")
    job_data: Dict[str, Any] = Field(description="Job requirements from job agent")


class CVTailoringPlan(BaseModel):
    """Plan for tailoring CV to match job."""
    matching_experiences: List[str] = Field(description="Matching experience entries")
    matching_skills: List[str] = Field(description="Matching skills")
    relevant_projects: List[str] = Field(description="Relevant projects")
    keywords_to_incorporate: List[str] = Field(description="Keywords to include")
    reordering_suggestions: str = Field(description="Suggestions for reordering")
    emphasis_points: List[str] = Field(description="Points to emphasize")
    reasoning: str = Field(description="Reasoning for changes")


class CVJobAlignmentResponse(BaseModel):
    """Response from alignment analysis."""
    success: bool
    tailoring_plan: Optional[CVTailoringPlan] = None
    message: str


class GenerateTailoredCVRequest(BaseModel):
    """Request to generate tailored CV."""
    cv_data: Dict[str, Any] = Field(description="Original CV data")
    tailoring_plan: Dict[str, Any] = Field(description="Tailoring plan from alignment analysis")
    output_filename: str = Field(
        description="Desired filename for PDF",
        example="john_doe_cv_tailored.pdf"
    )


class GenerateTailoredCVResponse(BaseModel):
    """Response from CV generation."""
    success: bool
    pdf_path: Optional[str] = None
    html_preview: Optional[str] = None
    message: str


class GenerateCoverLetterRequest(BaseModel):
    """Request to generate cover letter."""
    cv_data: Dict[str, Any] = Field(description="Resume data")
    job_data: Dict[str, Any] = Field(description="Job requirements")
    company_data: Optional[Dict[str, Any]] = Field(default=None, description="Optional company info")
    output_filename: str = Field(
        description="Desired filename for PDF",
        example="john_doe_cover_letter.pdf"
    )
    recipient_info: str = Field(
        default="Hiring Manager",
        description="Who the letter is addressed to"
    )


class CoverLetterContent(BaseModel):
    """Structured cover letter content."""
    opening_paragraph: str = Field(description="Opening expressing interest in the specific position and company")
    body_paragraph_1: str = Field(description="First body paragraph connecting relevant experience to job requirements")
    body_paragraph_2: str = Field(description="Second body paragraph highlighting additional relevant qualifications")
    body_paragraph_3: str = Field(default="", description="Optional third body paragraph if needed for company-specific points")
    closing_paragraph: str = Field(description="Closing with call to action and appreciation")


class GenerateCoverLetterResponse(BaseModel):
    """Response from cover letter generation."""
    success: bool
    pdf_path: Optional[str] = None
    content: Optional[CoverLetterContent] = None
    message: str


# ============================================
# Writer Chat Models (Conversational Interface)
# ============================================

class WriterChatSessionInitRequest(BaseModel):
    """Request to start a new Writer chat session."""
    cv_data: Dict[str, Any] = Field(description="Resume data from CV agent")
    job_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Job requirements from job agent (optional for resume refinement mode)"
    )
    mode: Literal["resume_refinement", "job_tailoring"] = Field(
        default="resume_refinement",
        description="Chat mode: resume_refinement (CV only) or job_tailoring (CV + job)"
    )


class WriterChatSessionInitResponse(BaseModel):
    """Response when starting a Writer chat session."""
    success: bool
    session_id: str = Field(description="Session ID for subsequent chat messages")
    initial_message: str = Field(description="Writer's initial greeting/summary")
    greeting_message: Optional[str] = Field(default=None, description="Separate greeting message")
    summary_message: Optional[str] = Field(default=None, description="Separate summary message")
    message: str = Field(description="Status message")


class WriterChatMessageRequest(BaseModel):
    """Request to send a message in Writer chat."""
    session_id: str = Field(description="Session identifier from init")
    user_message: str = Field(description="User's message to the Writer agent")


class GeneratedFile(BaseModel):
    """Metadata for a generated file."""
    filename: str = Field(description="Name of the generated file")
    file_type: str = Field(description="Type of file (cv, cover_letter, etc.)")
    download_url: str = Field(description="URL to download the file")


class WriterChatMessageResponse(BaseModel):
    """Response from Writer agent."""
    success: bool
    assistant_message: str = Field(description="Writer's response")
    requires_approval: bool = Field(
        default=False,
        description="Whether user approval is needed before proceeding"
    )
    preview_content: Optional[str] = Field(
        default=None,
        description="Preview content for user review (e.g., tailoring plan)"
    )
    generated_files: Optional[List[GeneratedFile]] = Field(
        default=None,
        description="List of files generated in this response (for download)"
    )
    message: str = Field(description="Status message")


class ResumeSummaryRequest(BaseModel):
    """Request to generate resume summary."""
    cv_data: Dict[str, Any] = Field(description="Resume data from CV agent")


class ResumeSummaryResponse(BaseModel):
    """Response with resume summary."""
    success: bool
    summary: str = Field(description="Neutral summary of the resume")
    suggestions: Optional[List[str]] = Field(
        default=None,
        description="Optional suggestions for improvement"
    )
    message: str = Field(description="Status message")


# ============================================
# File Upload Models (for future multipart support)
# ============================================

class FileUploadResponse(BaseModel):
    """Response from file upload."""
    success: bool
    file_path: str
    filename: str
    message: str


# ============================================
# Audio Transcription Models
# ============================================

class TranscriptionRequest(BaseModel):
    """Request parameters for audio transcription (used for query params)."""
    model: Literal["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe", "gpt-4o-transcribe-diarize"] = Field(
        default="gpt-4o-transcribe",
        description="Model to use for transcription"
    )
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt", "diarized_json"] = Field(
        default="json",
        description="Format of the transcription response"
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code (ISO 639-1 or 639-3) for the audio"
    )
    prompt: Optional[str] = Field(
        default=None,
        description="Optional text to guide the model's style or continue a previous audio segment"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Sampling temperature (0-1). Higher values make output more random."
    )
    timestamp_granularities: Optional[List[Literal["word", "segment"]]] = Field(
        default=None,
        description="Granularity of timestamps (only for whisper-1)"
    )
    chunking_strategy: Optional[Literal["auto"]] = Field(
        default=None,
        description="Chunking strategy for long audio (required for gpt-4o-transcribe-diarize when audio > 30s)"
    )


class TranscriptionResponse(BaseModel):
    """Response from audio transcription."""
    success: bool
    text: Optional[str] = Field(default=None, description="Transcribed text")
    segments: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Segments with timestamps (for verbose_json or diarized_json formats)"
    )
    words: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Word-level timestamps (for verbose_json with word granularity)"
    )
    message: str


class TranslationRequest(BaseModel):
    """Request parameters for audio translation (used for query params)."""
    model: Literal["whisper-1"] = Field(
        default="whisper-1",
        description="Model to use for translation (only whisper-1 supported)"
    )
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] = Field(
        default="json",
        description="Format of the translation response"
    )
    prompt: Optional[str] = Field(
        default=None,
        description="Optional text to guide the model's style"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Sampling temperature (0-1)"
    )


class TranslationResponse(BaseModel):
    """Response from audio translation."""
    success: bool
    text: Optional[str] = Field(default=None, description="Translated text (always in English)")
    segments: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Segments with timestamps (for verbose_json format)"
    )
    words: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Word-level timestamps (for verbose_json with word granularity)"
    )
    message: str


# ============================================
# Generic Response Models
# ============================================

class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    agents_available: List[str]
    message: str


