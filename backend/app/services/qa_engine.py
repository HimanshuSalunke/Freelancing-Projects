import os
import re
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import asyncio
import logging
import json
from pathlib import Path

import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np

from .document_request_handler import DocumentRequestHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridQAEngine:
    def __init__(self) -> None:
        # Initialize with safe defaults
        self.gemini_model = None
        self.sentence_model = None
        self.qa_dataset = []
        self.qa_embeddings = []
        self.doc_handler = None
        self._current_document_request = None
        
        # Initialize services with better error handling
        self._initialize_gemini()
        self._initialize_sentence_transformer()
        self._load_qa_dataset()
        
        # Initialize document request handler with better error handling
        try:
            self.doc_handler = DocumentRequestHandler()
            logger.info("✅ Document request handler initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize document request handler: {str(e)}")
            self.doc_handler = None
    
    def _initialize_gemini(self):
        """Initialize Gemini model with enhanced error handling"""
        try:
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            if not api_key:
                logger.warning("⚠️ GOOGLE_GEMINI_API_KEY not found in environment variables")
                return
            
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✅ Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini model: {str(e)}")
            self.gemini_model = None

    def _initialize_sentence_transformer(self):
        """Initialize sentence transformer for semantic search"""
        try:
            # Set cache directory to use existing models
            import os
            models_dir = Path(__file__).parent.parent.parent.parent / "models"
            cache_dir = models_dir / "sentence-transformers"
            
            # Set environment variables for model caching
            os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(cache_dir)
            os.environ["HF_HOME"] = str(models_dir)
            os.environ["TRANSFORMERS_CACHE"] = str(models_dir / "transformers")
            
            # Check if model files exist
            model_path = cache_dir / "models--sentence-transformers--all-MiniLM-L6-v2"
            logger.info(f"🔍 Checking model path: {model_path}")
            logger.info(f"🔍 Cache directory: {cache_dir}")
            logger.info(f"🔍 Models directory: {models_dir}")
            
            if not model_path.exists():
                logger.warning(f"⚠️ Model not found at {model_path}, will download")
            else:
                logger.info(f"✅ Found existing model at {model_path}")
            
            # Try to use local model path first
            model_path = cache_dir / "models--sentence-transformers--all-MiniLM-L6-v2" / "snapshots" / "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
            if model_path.exists():
                logger.info(f"✅ Using local model from {model_path}")
                self.sentence_model = SentenceTransformer(str(model_path))
            else:
                logger.info("⚠️ Local model not found, using cache directory")
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=str(cache_dir))
            logger.info("✅ Sentence transformer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize sentence transformer: {str(e)}")
            self.sentence_model = None
    
    def _load_qa_dataset(self):
        """Load QA dataset and pre-compute embeddings"""
        try:
            qa_file = Path(__file__).parent.parent / "data" / "qa_dataset.json"
            logger.info(f"🔍 Loading QA dataset from: {qa_file}")
            
            if not qa_file.exists():
                logger.warning("⚠️ QA dataset file not found")
                return
            
            # Check file size
            file_size = qa_file.stat().st_size
            logger.info(f"📁 QA dataset file size: {file_size} bytes")
            
            # Read file content first to check for issues
            with open(qa_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"📄 File content length: {len(content)} characters")
            
            # Parse JSON with better error handling
            try:
                self.qa_dataset = json.loads(content)
                logger.info(f"📊 Successfully parsed JSON with {len(self.qa_dataset)} QA pairs")
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing error: {str(e)}")
                logger.error(f"❌ Error at line {e.lineno}, column {e.colno}")
                # Try to show the problematic area
                lines = content.split('\n')
                if e.lineno <= len(lines):
                    logger.error(f"❌ Problematic line {e.lineno}: {lines[e.lineno-1]}")
                return
            
            # Validate dataset structure
            if not isinstance(self.qa_dataset, list):
                logger.error("❌ QA dataset is not a list")
                self.qa_dataset = []
                return
            
            # Count valid QA pairs
            valid_pairs = 0
            for i, qa in enumerate(self.qa_dataset):
                if isinstance(qa, dict) and 'question' in qa and 'answer' in qa:
                    valid_pairs += 1
                else:
                    logger.warning(f"⚠️ Invalid QA pair at index {i}: {qa}")
            
            logger.info(f"📊 Found {valid_pairs} valid QA pairs out of {len(self.qa_dataset)} total entries")
            
            # Pre-compute embeddings for all questions
            if self.sentence_model and self.qa_dataset:
                questions = [qa['question'] for qa in self.qa_dataset if isinstance(qa, dict) and 'question' in qa]
                logger.info(f"🔄 Computing embeddings for {len(questions)} questions...")
                self.qa_embeddings = self.sentence_model.encode(questions)
                logger.info(f"✅ Successfully computed embeddings for {len(self.qa_embeddings)} questions")
            else:
                logger.warning("⚠️ Could not compute embeddings - sentence model not available or dataset empty")
            
        except Exception as e:
            logger.error(f"❌ Failed to load QA dataset: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            self.qa_dataset = []
            self.qa_embeddings = []
    
    def _find_similar_question(self, user_question: str, threshold: float = 0.8) -> Optional[Dict]:
        """Find most similar question from dataset using semantic search"""
        if not self.sentence_model or not self.qa_embeddings or not self.qa_dataset:
            return None
        
        try:
            # Encode user question
            user_embedding = self.sentence_model.encode([user_question])
            
            # Calculate similarities
            similarities = np.dot(self.qa_embeddings, user_embedding.T).flatten()
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_similarity = float(similarities[best_idx])  # Convert to float to avoid array issues
            
            logger.info(f"🔍 Best similarity found: {best_similarity:.3f} (threshold: {threshold})")
            
            if best_similarity >= threshold:
                return {
                    'qa_pair': self.qa_dataset[best_idx],
                    'similarity': best_similarity,
                    'index': int(best_idx)  # Convert to int to avoid array issues
                }
            
            return None
                
        except Exception as e:
            logger.error(f"❌ Error in semantic search: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    async def _gemini_answer(self, question: str) -> str:
        """Generate answer using Gemini API"""
        if not self.gemini_model:
            return "I apologize, but I'm currently unable to process your request. Please try again later."
        
        try:
            # Enhanced prompt for better responses
            prompt = f"""
            You are an AI assistant for Reliance Jio Infotech Solutions. 
            Answer the following question about company policies, procedures, or general HR matters.
            Be helpful, professional, and accurate. If you're not sure about something, say so.
            
            Question: {question}
            
            Please provide a clear, helpful response:
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                prompt
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"❌ Gemini API error: {str(e)}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    async def answer(self, question: str) -> str:
        """Main method to answer questions using hybrid approach"""
        if not question or not question.strip():
            return "Please provide a question so I can help you."
        
        question = question.strip()
        
        # Step 1: Check for document request keywords
        if self.doc_handler and any(keyword in question.lower() for keyword in ['document', 'need document', 'request document', 'get document']):
            try:
                return await self.doc_handler.handle_document_request(question)
            except Exception as e:
                logger.error(f"❌ Document request error: {str(e)}")
        
        # Step 2: Try semantic search in local dataset
        similar_qa = self._find_similar_question(question)
        
        if similar_qa and similar_qa['similarity'] > 0.8:
            logger.info(f"✅ Found similar question in dataset (similarity: {similar_qa['similarity']:.3f})")
            return similar_qa['qa_pair']['answer']
        
        # Step 3: Use Gemini API for complex questions
        logger.info("🔄 Using Gemini API for complex question")
        return await self._gemini_answer(question)
    
    def get_health_status(self) -> Dict:
        """Get health status of QA engine components"""
        return {
            "gemini_model": self.gemini_model is not None,
            "sentence_model": self.sentence_model is not None,
            "qa_dataset_loaded": len(self.qa_dataset) > 0,
            "qa_embeddings_ready": len(self.qa_embeddings) > 0,
            "document_handler": self.doc_handler is not None,
            "total_qa_pairs": len(self.qa_dataset)
        }


