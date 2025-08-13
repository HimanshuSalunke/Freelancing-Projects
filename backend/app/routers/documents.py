import os
import fitz  # PyMuPDF
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from ..config import auth_disabled
from ..services.summarizer import Summarizer

router = APIRouter()

# Initialize the summarizer service
summarizer = Summarizer()


class SummarizeResponse(BaseModel):
    document_type: str
    executive_summary: str
    section_summary: list[dict]
    table_insights: list[dict]
    keywords: list[str]
    patterns: list[str]
    anomalies: list[str]


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF content"""
    text = ""
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {e}")
    return text


def extract_keywords(text: str) -> list[str]:
    """Extract keywords from text"""
    # Simple keyword extraction - look for capitalized words and common terms
    import re
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    # Remove common words
    stop_words = {'The', 'This', 'That', 'With', 'From', 'Have', 'Will', 'Are', 'For', 'And', 'But', 'Not', 'You', 'All', 'Any', 'Can', 'Had', 'Her', 'Was', 'One', 'Our', 'Out', 'Day', 'Get', 'Has', 'Him', 'His', 'How', 'Man', 'New', 'Now', 'Old', 'See', 'Two', 'Way', 'Who', 'Boy', 'Did', 'Its', 'Let', 'Put', 'Say', 'She', 'Too', 'Use'}
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    return list(set(keywords))[:10]  # Return unique keywords, max 10


@router.post("/upload", response_model=SummarizeResponse)
async def upload(file: UploadFile = File(...)):
    """Upload and summarize PDF with enhanced error handling"""
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Check file size (limit to 50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="File size too large. Maximum 50MB allowed.")
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Extract text from PDF
        try:
            raw_text = extract_text_from_pdf(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")
        
        if not raw_text or not raw_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in PDF")
        
        # Generate summary using the proper summarizer service
        try:
            summary = summarizer.summarize(raw_text, max_words=250)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
        
        # Extract keywords
        try:
            keywords = extract_keywords(raw_text)
        except Exception as e:
            print(f"Warning: Failed to extract keywords: {e}")
            keywords = []
        
        # Determine document type
        doc_type = "LONG" if len(raw_text) > 10000 else "MEDIUM" if len(raw_text) > 1000 else "SHORT"
        
        return {
            "document_type": doc_type,
            "executive_summary": summary,
            "section_summary": [],
            "table_insights": [],
            "keywords": keywords,
            "patterns": [],
            "anomalies": []
        }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in PDF upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


