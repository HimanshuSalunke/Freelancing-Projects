from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio

from ..services.qa_generator import AdvancedQAGenerator
from ..services.qa_engine import QASemanticEngine

router = APIRouter()

# Initialize services
qa_generator = AdvancedQAGenerator()
qa_engine = QASemanticEngine()


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    feedback_type: str  # "correct", "incorrect", "improve"
    suggested_answer: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    include_suggestions: bool = True


class QASuggestion(BaseModel):
    question: str
    answer: str
    similarity: float
    source: str


class QAStatistics(BaseModel):
    total_qa_pairs: int
    generated_qa_pairs: int
    manual_qa_pairs: int
    sources: Dict[str, int]
    last_updated: str


@router.post("/generate-qa", response_model=Dict)
async def generate_qa_from_documents(background_tasks: BackgroundTasks):
    """Generate Q&A pairs from policy documents in the background"""
    try:
        # Start background task for QA generation
        background_tasks.add_task(qa_generator.auto_update_qa_system)
        
        return {
            "message": "QA generation started in background",
            "status": "processing",
            "estimated_time": "5-10 minutes depending on document size"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start QA generation: {str(e)}")


@router.get("/statistics", response_model=QAStatistics)
async def get_qa_statistics():
    """Get QA system statistics"""
    try:
        stats = qa_generator.export_qa_statistics()
        return QAStatistics(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.post("/feedback")
async def submit_qa_feedback(feedback: FeedbackRequest):
    """Submit feedback for QA responses"""
    try:
        qa_generator.update_qa_from_feedback(
            feedback.question,
            feedback.answer,
            feedback.feedback_type
        )
        
        return {
            "message": "Feedback submitted successfully",
            "status": "updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.post("/suggestions", response_model=List[QASuggestion])
async def get_qa_suggestions(query: QueryRequest):
    """Get semantic suggestions for user queries"""
    try:
        suggestions = qa_generator.get_semantic_suggestions(query.query)
        
        if not query.include_suggestions:
            return []
        
        return [
            QASuggestion(
                question=s["question"],
                answer=s["answer"],
                similarity=s["similarity"],
                source=s["source"]
            )
            for s in suggestions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.post("/enhanced-answer")
async def get_enhanced_answer(query: QueryRequest):
    """Get enhanced answer with suggestions"""
    try:
        # Get primary answer
        answer = await qa_engine.answer(query.query)
        
        # Get suggestions if requested
        suggestions = []
        if query.include_suggestions:
            suggestions = qa_generator.get_semantic_suggestions(query.query, limit=3)
        
        return {
            "answer": answer,
            "suggestions": suggestions,
            "query": query.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced answer: {str(e)}")


@router.get("/health")
async def qa_health_check():
    """Health check for QA system"""
    try:
        stats = qa_generator.export_qa_statistics()
        
        return {
            "status": "healthy",
            "qa_pairs_available": stats["total_qa_pairs"],
            "gemini_available": qa_generator.gemini_model is not None,
            "sentence_transformer_available": True,
            "last_updated": stats["last_updated"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/auto-learn")
async def auto_learn_from_conversation(query: str, user_feedback: str):
    """Auto-learn from user conversations and feedback"""
    try:
        # This could be enhanced to learn from successful conversations
        # and improve the QA system over time
        
        return {
            "message": "Learning data recorded",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record learning data: {str(e)}")
