from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from io import BytesIO
import json
import logging

from ..services.document_request_handler import DocumentRequestHandler
from .auth import get_current_user_dependency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize document request handler
doc_handler = DocumentRequestHandler()


class DocumentRequest(BaseModel):
    document_type: str
    document_name: str
    details: str
    user_id: str = "anonymous"


class DocumentRequestResponse(BaseModel):
    request_id: str
    document_name: str
    status: str
    submitted_at: str
    message: str


class RequestStatus(BaseModel):
    request_id: str
    document_type: str
    document_name: str
    details: str
    user_id: str
    status: str
    submitted_at: str
    hr_notified: bool


@router.post("/submit", response_model=DocumentRequestResponse)
async def submit_document_request(
    request: DocumentRequest,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Submit a document request and generate PDF with authentication and same-user restriction
    
    Security: Users can only generate documents for themselves.
    Any attempt to generate a document for another employee will result in 403 Forbidden.
    """
    try:
        # Log request
        current_emp_id = str(current_user.get("emp_id", ""))
        logger.info(f"📄 Document request from user {current_emp_id}: {request.document_name}")
        
        # Validate document type
        is_valid, doc_type, doc_name = doc_handler.validate_document_choice(request.document_type)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # Validate details
        is_valid_details, validation_message = doc_handler.validate_document_details(request.details, doc_type)
        if not is_valid_details:
            raise HTTPException(status_code=400, detail=validation_message)
        
        # SECURITY: Extract employee ID from request details and enforce same-user restriction
        try:
            details_dict = json.loads(request.details)
            requested_emp_id_raw = str(details_dict.get('employeeId', '')).strip()

            # Normalize requested employee identifier: allow numeric emp_id or alphanumeric employee_code (e.g., EMP0001)
            requested_emp_id = requested_emp_id_raw
            if not requested_emp_id.isdigit() and requested_emp_id:
                # Resolve employee_code to numeric emp_id
                try:
                    from ..services.employee_validator import EmployeeValidator
                    validator = EmployeeValidator()
                    emp = validator.get_employee_by_id(requested_emp_id)
                    if emp and 'emp_id' in emp:
                        requested_emp_id = str(emp['emp_id'])
                except Exception as _:
                    # If resolution fails, keep original (will fail the check)
                    pass

            # Users can ONLY generate documents for themselves
            if current_emp_id != requested_emp_id:
                logger.warning(
                    f"⚠️ SECURITY: User {current_emp_id} attempted to generate document "
                    f"for user {requested_emp_id_raw} (normalized: {requested_emp_id}) - FORBIDDEN"
                )
                raise HTTPException(
                    status_code=400,
                    detail="You don't have access to generate documents for other users"
                )
        except json.JSONDecodeError:
            logger.error("Failed to parse document details JSON")
            raise HTTPException(status_code=400, detail="Invalid document details format")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating employee ID: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to validate request")
        
        # Submit the request and generate PDF (user_id is now authenticated user's ID)
        submitted_request = doc_handler.submit_document_request(
            doc_type=doc_type,
            doc_name=doc_name,
            details=request.details,
            user_id=current_emp_id
        )
        
        message = "Document generated successfully" if submitted_request.get("pdf_generated", False) else "Document request submitted to HR"
        
        logger.info(f"✅ Document generated successfully for user {current_emp_id}")
        
        return DocumentRequestResponse(
            request_id=submitted_request['id'],
            document_name=submitted_request['document_name'],
            status=submitted_request['status'],
            submitted_at=submitted_request['submitted_at'],
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error submitting document request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit document request: {str(e)}")


@router.get("/status/{request_id}", response_model=RequestStatus)
async def get_request_status(request_id: str):
    """Get status of a document request"""
    try:
        request = doc_handler.get_request_status(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        return RequestStatus(**request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get request status: {str(e)}")


@router.get("/user/{user_id}", response_model=List[RequestStatus])
async def get_user_requests(user_id: str):
    """Get all requests for a specific user"""
    try:
        requests = doc_handler.get_user_requests(user_id)
        return [RequestStatus(**req) for req in requests]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user requests: {str(e)}")


@router.get("/pending/count")
async def get_pending_requests_count():
    """Get count of pending requests"""
    try:
        count = doc_handler.get_pending_requests_count()
        return {"pending_count": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending count: {str(e)}")


@router.get("/documents/list")
async def get_supported_documents():
    """Get list of supported document types"""
    try:
        return {
            "supported_documents": doc_handler.supported_documents,
            "total_count": len(doc_handler.supported_documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document list: {str(e)}")


@router.get("/download/{request_id}")
async def download_document_pdf(request_id: str):
    """Download PDF for a completed document request"""
    try:
        request = doc_handler.get_request_status(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if not request.get('pdf_generated', False):
            raise HTTPException(status_code=400, detail="PDF not generated for this request")
        
        # Get PDF content
        pdf_content = request.get('pdf_content')
        if not pdf_content:
            raise HTTPException(status_code=404, detail="PDF content not found")
        
        # Convert hex string back to bytes
        try:
            pdf_bytes = bytes.fromhex(pdf_content)
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid PDF data format")
        
        # Generate filename
        doc_name = request['document_name'].replace('/', '_').replace(' ', '_')
        filename = f"{doc_name}_{request_id}.pdf"
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download PDF: {str(e)}")


@router.get("/preview/{request_id}")
async def preview_document_pdf(request_id: str):
    """Preview PDF for a completed document request (opens in browser)"""
    try:
        request = doc_handler.get_request_status(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if not request.get('pdf_generated', False):
            raise HTTPException(status_code=400, detail="PDF not generated for this request")
        
        # Get PDF content
        pdf_content = request.get('pdf_content')
        if not pdf_content:
            raise HTTPException(status_code=404, detail="PDF content not found")
        
        # Convert hex string back to bytes
        try:
            pdf_bytes = bytes.fromhex(pdf_content)
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid PDF data format")
        
        # Return PDF for preview (no attachment header)
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview PDF: {str(e)}")


@router.get("/health")
async def document_requests_health():
    """Health check for document requests system"""
    try:
        pending_count = doc_handler.get_pending_requests_count()
        total_requests = len(doc_handler.requests)
        
        return {
            "status": "healthy",
            "pending_requests": pending_count,
            "total_requests": total_requests,
            "supported_documents": len(doc_handler.supported_documents),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
