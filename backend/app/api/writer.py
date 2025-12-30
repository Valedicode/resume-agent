"""
Writer Agent API Endpoints

Provides endpoints for CV-job alignment analysis, tailored CV generation,
cover letter generation, and conversational chat interface.
"""

from fastapi import APIRouter, HTTPException, status, Depends
import json
import re

from app.models.schemas import (
    CVJobAlignmentRequest,
    CVJobAlignmentResponse,
    GenerateTailoredCVRequest,
    GenerateTailoredCVResponse,
    GenerateCoverLetterRequest,
    GenerateCoverLetterResponse,
    CVTailoringPlan,
    CoverLetterContent,
    ResumeInfo,
    JobRequirements,
    WriterChatSessionInitRequest,
    WriterChatSessionInitResponse,
    WriterChatMessageRequest,
    WriterChatMessageResponse,
    GeneratedFile,
    ResumeSummaryRequest,
    ResumeSummaryResponse
)
from app.agents.writer_agent import (
    analyze_cv_job_alignment,
    generate_tailored_cv_html,
    generate_cover_letter_content,
    generate_cv_pdf,
    generate_cover_letter_pdf,
    agent as writer_agent
)
from app.services.generic_session_manager import (
    get_session_manager,
    GenericSessionManager
)

router = APIRouter(prefix="/api/writer", tags=["Writer Agent"])


@router.post(
    "/analyze-alignment",
    response_model=CVJobAlignmentResponse,
    summary="Analyze CV-Job Alignment",
    description="Analyze how well a CV matches job requirements and create a tailoring plan."
)
async def analyze_alignment(request: CVJobAlignmentRequest):
    """
    Analyze CV-job alignment and create a tailoring plan.
    
    **Purpose:**
    This is the first step in the tailoring process. It performs gap analysis
    to identify which parts of the CV align with the job and how to optimize.
    
    **Workflow:**
    1. Compares CV skills/experience with job requirements
    2. Identifies matching experiences, skills, and projects
    3. Suggests keywords to incorporate
    4. Recommends section reordering and emphasis points
    
    **Parameters:**
    - `cv_data`: Resume data from CV agent (as dict)
    - `job_data`: Job requirements from job agent (as dict)
    
    **Returns:**
    - Tailoring plan with specific, actionable recommendations
    
    **Next Steps:**
    - Present plan to user for approval
    - Use plan in `/generate-cv` endpoint
    """
    try:
        # Validate CV data structure
        try:
            ResumeInfo(**request.cv_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CV data structure: {str(e)}"
            )
        
        # Validate job data structure
        try:
            JobRequirements(**request.job_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job data structure: {str(e)}"
            )
        
        # Convert to JSON strings for the tool
        cv_json = json.dumps(request.cv_data)
        job_json = json.dumps(request.job_data)
        
        # Analyze alignment
        tailoring_plan_json = analyze_cv_job_alignment.invoke({
            "cv_json": cv_json,
            "job_json": job_json
        })
        
        tailoring_plan_dict = json.loads(tailoring_plan_json)
        
        return CVJobAlignmentResponse(
            success=True,
            tailoring_plan=CVTailoringPlan(**tailoring_plan_dict),
            message="Alignment analysis completed successfully."
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse tailoring plan: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing alignment: {str(e)}"
        )


@router.post(
    "/generate-cv",
    response_model=GenerateTailoredCVResponse,
    summary="Generate Tailored CV",
    description="Generate a tailored CV PDF based on the original CV and tailoring plan."
)
async def generate_cv(request: GenerateTailoredCVRequest):
    """
    Generate tailored CV HTML and PDF.
    
    **Prerequisites:**
    - Must have run `/analyze-alignment` first to get tailoring plan
    - User should have approved the tailoring plan
    
    **Workflow:**
    1. Generates tailored HTML based on CV + tailoring plan
    2. Converts HTML to professional PDF with styling
    3. Saves PDF to backend/data/ directory
    
    **Parameters:**
    - `cv_data`: Original CV data from CV agent
    - `tailoring_plan`: Tailoring plan from alignment analysis
    - `output_filename`: Desired filename (e.g., "john_doe_cv.pdf")
    
    **Returns:**
    - Path to generated PDF file
    - HTML preview (for frontend display if needed)
    
    **Note:** PDF is saved to backend/data/ directory by default.
    """
    try:
        # Validate data structures
        try:
            ResumeInfo(**request.cv_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CV data: {str(e)}"
            )
        
        try:
            CVTailoringPlan(**request.tailoring_plan)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tailoring plan: {str(e)}"
            )
        
        # Validate filename
        if not request.output_filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Output filename must end with .pdf"
            )
        
        # Convert to JSON strings
        cv_json = json.dumps(request.cv_data)
        plan_json = json.dumps(request.tailoring_plan)
        
        # Generate HTML
        html_content = generate_tailored_cv_html.invoke({
            "cv_json": cv_json,
            "tailoring_plan_json": plan_json
        })
        
        # Generate PDF
        applicant_name = request.cv_data.get('name', 'Applicant')
        pdf_result = generate_cv_pdf.invoke({
            "html_content": html_content,
            "output_filename": request.output_filename,
            "applicant_name": applicant_name
        })
        
        # Check if PDF generation was successful
        if "Error" in pdf_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=pdf_result
            )
        
        # Extract filename from result message
        # Format: "CV PDF generated successfully! The file '{filename}' is ready for download."
        match = re.search(r"The file '([^']+)' is ready for download", pdf_result)
        pdf_path = match.group(1) if match else None
        
        return GenerateTailoredCVResponse(
            success=True,
            pdf_path=pdf_path,
            html_preview=html_content[:500] + "..." if len(html_content) > 500 else html_content,
            message=pdf_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating CV: {str(e)}"
        )


@router.post(
    "/generate-cover-letter",
    response_model=GenerateCoverLetterResponse,
    summary="Generate Cover Letter",
    description="Generate a tailored cover letter PDF based on CV, job requirements, and optional company info."
)
async def generate_cover_letter(request: GenerateCoverLetterRequest):
    """
    Generate tailored cover letter.
    
    **Purpose:**
    Creates a compelling, personalized cover letter that:
    - Connects candidate's background to job requirements
    - Demonstrates understanding of company (if company data provided)
    - Maintains authentic, professional tone
    
    **Workflow:**
    1. Generates structured cover letter content (paragraphs)
    2. Formats into professional business letter
    3. Converts to PDF with appropriate styling
    4. Saves to backend/data/ directory
    
    **Parameters:**
    - `cv_data`: Resume data from CV agent
    - `job_data`: Job requirements from job agent
    - `company_data`: Optional company info from company research
    - `output_filename`: Desired filename (e.g., "john_doe_cover_letter.pdf")
    - `recipient_info`: Who to address (default: "Hiring Manager")
    
    **Returns:**
    - Path to generated PDF
    - Cover letter content (structured paragraphs)
    
    **Tip:** Include company_data for more personalized cover letters.
    """
    try:
        # Validate data structures
        try:
            ResumeInfo(**request.cv_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CV data: {str(e)}"
            )
        
        try:
            JobRequirements(**request.job_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job data: {str(e)}"
            )
        
        # Validate filename
        if not request.output_filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Output filename must end with .pdf"
            )
        
        # Convert to JSON strings
        cv_json = json.dumps(request.cv_data)
        job_json = json.dumps(request.job_data)
        company_json = json.dumps(request.company_data) if request.company_data else ""
        
        # Generate cover letter content
        content_json = generate_cover_letter_content.invoke({
            "cv_json": cv_json,
            "job_json": job_json,
            "company_json": company_json
        })
        
        content_dict = json.loads(content_json)
        
        # Get applicant info for PDF
        applicant_name = request.cv_data.get('name', 'Applicant')
        applicant_email = request.cv_data.get('email', '')
        applicant_phone = request.cv_data.get('phone', '')
        applicant_contact = f"{applicant_email} | {applicant_phone}"
        
        # Generate PDF
        pdf_result = generate_cover_letter_pdf.invoke({
            "content_json": content_json,
            "output_filename": request.output_filename,
            "applicant_name": applicant_name,
            "applicant_contact": applicant_contact,
            "recipient_info": request.recipient_info
        })
        
        # Check if PDF generation was successful
        if "Error" in pdf_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=pdf_result
            )
        
        # Extract filename from result message
        # Format: "CV PDF generated successfully! The file '{filename}' is ready for download."
        match = re.search(r"The file '([^']+)' is ready for download", pdf_result)
        pdf_path = match.group(1) if match else None
        
        return GenerateCoverLetterResponse(
            success=True,
            pdf_path=pdf_path,
            content=CoverLetterContent(**content_dict),
            message=pdf_result
        )
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse cover letter content: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating cover letter: {str(e)}"
        )


@router.get(
    "/health",
    summary="Writer Agent Health Check",
    description="Check if writer agent tools are available."
)
async def writer_health():
    """
    Health check for writer agent.
    
    Returns status of available tools and dependencies.
    """
    available_tools = [
        "analyze_cv_job_alignment",
        "generate_tailored_cv_html",
        "generate_cover_letter_content",
        "generate_cv_pdf",
        "generate_cover_letter_pdf"
    ]
    
    return {
        "status": "healthy",
        "agent": "writer",
        "available_tools": available_tools,
        "message": "Writer agent is operational"
    }


# ============================================
# Conversational Chat Interface
# ============================================

@router.post(
    "/chat/start",
    response_model=WriterChatSessionInitResponse,
    summary="Start Writer Chat Session",
    description="Initialize a new conversational session with the Writer agent."
)
async def start_writer_chat(
    request: WriterChatSessionInitRequest,
    session_manager: GenericSessionManager = Depends(get_session_manager)
):
    """
    Start a new Writer chat session.
    
    **Purpose:**
    Creates a conversational session where the user can chat with the Writer agent
    to refine their resume or tailor it for a specific job.
    
    **Workflow:**
    1. Receives CV data (and optionally job data)
    2. Determines mode (resume_refinement or job_tailoring)
    3. Generates initial summary/greeting
    4. Returns session ID for subsequent messages
    
    **Modes:**
    - **resume_refinement**: CV only, general resume improvement
    - **job_tailoring**: CV + job, tailored for specific position
    
    **Parameters:**
    - `cv_data`: Resume data from CV agent
    - `job_data`: Job requirements (optional, required for job_tailoring mode)
    - `mode`: "resume_refinement" or "job_tailoring"
    
    **Returns:**
    - `session_id`: Use for subsequent chat messages
    - `initial_message`: Writer's greeting and summary
    
    **Next Steps:**
    Send user messages to `/chat/message` with the session_id.
    """
    try:
        # Validate CV data
        try:
            ResumeInfo(**request.cv_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CV data: {str(e)}"
            )
        
        # Validate job data if provided
        if request.job_data:
            try:
                JobRequirements(**request.job_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid job data: {str(e)}"
                )
        
        # Validate mode
        if request.mode == "job_tailoring" and not request.job_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="job_tailoring mode requires job_data"
            )
        
        # Create session
        session_id = session_manager.create_session(
            session_type="writer",
            initial_data={
                "cv_data": request.cv_data,
                "job_data": request.job_data,
                "mode": request.mode
            }
        )
        
        # Generate initial message based on mode
        if request.mode == "resume_refinement":
            # Generate resume summary
            cv_json = json.dumps(request.cv_data)
            
            # Create initial context for Writer agent
            initial_prompt = f"""I have received the following resume data:

{cv_json}

Please provide a neutral summary of this resume, highlighting the key information (name, contact, skills, experience, education). Then ask if any important information is missing or needs clarification."""
            
            # Invoke Writer agent
            result = writer_agent.invoke({
                "messages": [
                    {"role": "system", "content": "You are helping with resume refinement. Start by providing a neutral summary."},
                    {"role": "user", "content": initial_prompt}
                ]
            })
            
            initial_message = result["messages"][-1].content
            
        else:  # job_tailoring
            # Generate job alignment preview
            cv_json = json.dumps(request.cv_data)
            job_json = json.dumps(request.job_data)
            
            initial_prompt = f"""I have both resume and job data ready for tailoring.

Resume: {cv_json}

Job: {job_json}

Please provide a brief overview of how well the resume matches the job requirements, and what we'll do to tailor it."""
            
            result = writer_agent.invoke({
                "messages": [
                    {"role": "system", "content": "You are helping with job-specific resume tailoring. Provide an overview of the match."},
                    {"role": "user", "content": initial_prompt}
                ]
            })
            
            initial_message = result["messages"][-1].content
        
        # Store initial exchange in session
        session_manager.add_message(session_id, "assistant", initial_message)
        
        return WriterChatSessionInitResponse(
            success=True,
            session_id=session_id,
            initial_message=initial_message,
            message="Writer chat session started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting Writer chat: {str(e)}"
        )


@router.post(
    "/chat/message",
    response_model=WriterChatMessageResponse,
    summary="Send Message to Writer",
    description="Send a message to the Writer agent and get a response."
)
async def send_writer_message(
    request: WriterChatMessageRequest,
    session_manager: GenericSessionManager = Depends(get_session_manager)
):
    """
    Send a message to the Writer agent and continue the conversation.
    
    **Purpose:**
    Main endpoint for chatting with the Writer agent. The Writer will:
    - Answer questions about the resume
    - Provide suggestions for improvement
    - Analyze alignment with job requirements
    - Generate tailored content when approved
    - Create PDFs when requested
    
    **Workflow:**
    1. Retrieves session and conversation history
    2. Adds user message to history
    3. Invokes Writer agent with full context
    4. Returns Writer's response
    5. Updates session history
    
    **Parameters:**
    - `session_id`: Session ID from `/chat/start`
    - `user_message`: User's message/question
    
    **Returns:**
    - `assistant_message`: Writer's response
    - `requires_approval`: Whether user approval is needed
    - `preview_content`: Preview for user review (if applicable)
    
    **The Writer can:**
    - Provide resume analysis and suggestions
    - Generate tailoring plans (requires approval)
    - Create tailored CVs (after approval)
    - Generate cover letters
    - Answer questions about the process
    """
    try:
        # Retrieve session
        session = session_manager.get_session(request.session_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired. Please start a new session."
            )
        
        # Add user message to history
        session_manager.add_message(request.session_id, "user", request.user_message)
        
        # Build conversation context for Writer agent
        messages = []
        
        # System message with context
        cv_json = json.dumps(session["cv_data"])
        job_json = json.dumps(session["job_data"]) if session["job_data"] else ""
        mode = session["mode"]
        
        system_context = f"""You are a professional CV and cover letter writer.

Mode: {mode}

CV Data:
{cv_json}
"""
        
        if job_json:
            system_context += f"""
Job Data:
{job_json}
"""
        
        system_context += """
Your role:
- If in resume_refinement mode: Help improve the resume generally
- If in job_tailoring mode: Tailor the resume for the specific job

Follow the human-in-the-loop workflow:
1. Analyze and propose changes
2. Wait for user approval
3. Generate content after approval
4. Create PDFs when requested

Be conversational, helpful, and professional."""
        
        messages.append({"role": "system", "content": system_context})
        
        # Add conversation history
        for msg in session["messages"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Invoke Writer agent
        try:
            result = writer_agent.invoke({"messages": messages})
            assistant_message = result["messages"][-1].content
            
            # Store assistant response
            session_manager.add_message(request.session_id, "assistant", assistant_message)
            
            # Check if response requires approval (simple heuristic)
            requires_approval = any(phrase in assistant_message.lower() for phrase in [
                "would you like me to",
                "shall i proceed",
                "do you approve",
                "would you like to proceed",
                "should i generate"
            ])
            
            # TODO: TECHNICAL DEBT - Replace regex parsing with tool result tracking
            # Current: Parsing text response (fragile, not best practice)
            # Better: Access result["intermediate_steps"] to get actual tool calls
            # See: APPROACH_ANALYSIS.md for detailed migration plan
            # Estimated effort: 2-3 hours
            
            # Detect generated files in the response
            generated_files = []
            import re
            
            # Look for PDF generation success messages
            # Updated to match new format: "CV PDF generated successfully! The file 'filename.pdf' is ready for download."
            pdf_patterns = [
                r"CV PDF generated successfully! The file '([^']+\.pdf)'",
                r"Cover letter PDF generated successfully! The file '([^']+\.pdf)'",
                r"PDF generated successfully! The file '([^']+\.pdf)'",
                # Fallback patterns for backward compatibility (if old format still exists)
                r"generated successfully at: .*/([^/\n]+\.pdf)"
            ]
            
            # Track seen filenames to avoid duplicates
            seen_filenames = set()
            
            for pattern in pdf_patterns:
                matches = re.findall(pattern, assistant_message)
                for filename in matches:
                    # Skip if we've already added this filename
                    if filename in seen_filenames:
                        continue
                    
                    seen_filenames.add(filename)
                    
                    # Determine file type from filename
                    file_type = "cover_letter" if "cover" in filename.lower() else "cv"
                    
                    generated_files.append(GeneratedFile(
                        filename=filename,
                        file_type=file_type,
                        download_url=f"/api/files/{filename}"
                    ))
            
            return WriterChatMessageResponse(
                success=True,
                assistant_message=assistant_message,
                requires_approval=requires_approval,
                preview_content=None,  # Could extract structured previews in future
                generated_files=generated_files if generated_files else None,
                message="Message processed successfully"
            )
            
        except Exception as e:
            error_message = f"I encountered an error: {str(e)}\n\nPlease try rephrasing your request."
            
            return WriterChatMessageResponse(
                success=False,
                assistant_message=error_message,
                requires_approval=False,
                preview_content=None,
                message=f"Error in Writer agent: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post(
    "/summarize-resume",
    response_model=ResumeSummaryResponse,
    summary="Generate Resume Summary",
    description="Generate a neutral summary of the resume for initial display."
)
async def summarize_resume(request: ResumeSummaryRequest):
    """
    Generate a neutral summary of the resume.
    
    **Purpose:**
    Creates an initial summary to show the user after CV upload.
    This helps the user verify that the CV was extracted correctly.
    
    **Workflow:**
    1. Receives CV data
    2. Generates neutral summary
    3. Optionally provides improvement suggestions
    
    **Parameters:**
    - `cv_data`: Resume data from CV agent
    
    **Returns:**
    - `summary`: Neutral description of the resume
    - `suggestions`: Optional list of improvement ideas
    
    **Use Case:**
    Display this summary immediately after CV upload to give the user
    confidence that their resume was processed correctly.
    """
    try:
        # Validate CV data
        try:
            ResumeInfo(**request.cv_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CV data: {str(e)}"
            )
        
        cv_json = json.dumps(request.cv_data)
        
        # Generate summary using Writer agent
        prompt = f"""Please provide a neutral, factual summary of this resume:

{cv_json}

Format the summary as a brief paragraph highlighting:
- Name and contact information
- Key skills
- Experience level
- Education background

Keep it objective and factual."""
        
        result = writer_agent.invoke({
            "messages": [
                {"role": "system", "content": "You are summarizing a resume. Be neutral and factual."},
                {"role": "user", "content": prompt}
            ]
        })
        
        summary = result["messages"][-1].content
        
        return ResumeSummaryResponse(
            success=True,
            summary=summary,
            suggestions=None,  # Could add suggestions in future
            message="Resume summary generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )


