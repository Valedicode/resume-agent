"""
CV Agent API Endpoints

Provides endpoints for CV extraction, ambiguity identification, and clarification.
"""

from fastapi import APIRouter, HTTPException, status
from pathlib import Path
import json

from app.models.schemas import (
    CVUploadRequest,
    CVExtractionResponse,
    CVClarificationRequest,
    CVClarificationResponse,
    ResumeInfo,
    ErrorResponse
)
from app.agents.cv_agent import (
    extract_resume_info,
    identify_ambiguities,
    update_resume_with_clarifications
)

router = APIRouter(prefix="/api/cv", tags=["CV Agent"])


@router.post(
    "/extract",
    response_model=CVExtractionResponse,
    summary="Extract CV Information",
    description="Extract structured information from a PDF resume file. Returns the data and any clarifying questions if ambiguities are found."
)
async def extract_cv(request: CVUploadRequest):
    """
    Extract CV information from PDF.
    
    **Workflow:**
    1. Reads PDF and extracts text
    2. Uses LLM to structure the data
    3. Identifies ambiguities or missing information
    4. Returns data and questions (if any)
    
    **Parameters:**
    - `pdf_path`: Path to the PDF resume file
    
    **Returns:**
    - CV data (name, email, phone, skills, education, experience)
    - List of clarifying questions (if ambiguities found)
    - Status indicating if clarification is needed
    """
    try:
        # Validate file exists
        pdf_path = Path(request.pdf_path)
        if not pdf_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CV file not found at path: {request.pdf_path}"
            )
        
        # Extract CV information
        cv_data_json = extract_resume_info.invoke({"pdf_path": str(pdf_path)})
        cv_data_dict = json.loads(cv_data_json)
        
        # Check for ambiguities
        questions_text = identify_ambiguities.invoke({"resume_json": cv_data_json})
        
        # Determine if clarification is needed
        needs_clarification = "no questions" not in questions_text.lower()
        
        if needs_clarification:
            # Parse questions into list
            questions = [
                q.strip() 
                for q in questions_text.split('\n') 
                if q.strip() and any(char.isdigit() or char == '?' for char in q)
            ]
            
            return CVExtractionResponse(
                success=True,
                cv_data=ResumeInfo(**cv_data_dict),
                needs_clarification=True,
                questions=questions if questions else [questions_text],
                message="CV extracted successfully. Clarification needed for some fields."
            )
        else:
            return CVExtractionResponse(
                success=True,
                cv_data=ResumeInfo(**cv_data_dict),
                needs_clarification=False,
                questions=None,
                message="CV extracted successfully. All information is clear."
            )
            
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {request.pdf_path}"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse CV data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting CV: {str(e)}"
        )


@router.post(
    "/clarify",
    response_model=CVClarificationResponse,
    summary="Update CV with Clarifications",
    description="Update the extracted CV data based on user's answers to clarifying questions."
)
async def clarify_cv(request: CVClarificationRequest):
    """
    Update CV data with user's clarification answers.
    
    **Use this endpoint when:**
    - The `/extract` endpoint returned `needs_clarification: true`
    - User has provided answers to the clarifying questions
    
    **Parameters:**
    - `cv_data`: Original CV data from the extract endpoint
    - `clarifications`: User's answers to the questions
    
    **Returns:**
    - Updated CV data incorporating the clarifications
    """
    try:
        # Convert dict to JSON string for the tool
        cv_data_json = json.dumps(request.cv_data)
        
        # Update CV with clarifications
        updated_cv_json = update_resume_with_clarifications.invoke({
            "resume_json": cv_data_json,
            "clarifications": request.clarifications
        })
        
        # Try to parse as JSON first, if it fails, use the LLM response directly
        try:
            updated_cv_dict = json.loads(updated_cv_json)
        except json.JSONDecodeError:
            # LLM might have returned plain text, extract JSON from it
            import re
            json_match = re.search(r'\{.*\}', updated_cv_json, re.DOTALL)
            if json_match:
                updated_cv_dict = json.loads(json_match.group())
            else:
                raise ValueError("Could not extract valid JSON from update response")
        
        return CVClarificationResponse(
            success=True,
            updated_cv_data=ResumeInfo(**updated_cv_dict),
            message="CV updated successfully with clarifications."
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse updated CV data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating CV: {str(e)}"
        )


@router.post(
    "/validate",
    response_model=dict,
    summary="Validate CV Data",
    description="Validate CV data structure without extraction (useful for testing)."
)
async def validate_cv_data(cv_data: ResumeInfo):
    """
    Validate CV data structure.
    
    This is a utility endpoint for testing and validation.
    It checks if the provided CV data matches the expected schema.
    """
    return {
        "success": True,
        "message": "CV data is valid",
        "cv_data": cv_data.model_dump()
    }


