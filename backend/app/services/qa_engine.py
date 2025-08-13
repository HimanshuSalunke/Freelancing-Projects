import json
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import asyncio
import logging

import torch
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai

from .document_request_handler import DocumentRequestHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QASemanticEngine:
    def __init__(self) -> None:
        # Initialize with safe defaults
        self.questions: List[str] = []
        self.answers: List[str] = []
        self.model = None
        self.q_embeddings = None
        self.gemini_model = None
        self.doc_handler = None
        self._current_document_request = None
        
        # Load QA dataset with better error handling
        self._load_qa_dataset()
        
        # Initialize sentence transformer with better error handling
        self._initialize_sentence_transformer()
        
        # Initialize Gemini with better error handling
        self._initialize_gemini()
        
        # Initialize document request handler with better error handling
        self._initialize_document_handler()
        
        # Define conversational patterns
        self.greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\bhow are you\b',
            r'\bwhat\'?s up\b',
            r'\bgreetings\b'
        ]
        
        self.farewell_patterns = [
            r'\b(bye|goodbye|see you|farewell)\b',
            r'\b(thank you|thanks|thx)\b'
        ]
        
        self.help_patterns = [
            r'\b(help|what can you do|capabilities|features)\b',
            r'\b(how does this work|how to use)\b'
        ]

    def _load_qa_dataset(self) -> None:
        """Load QA dataset with enhanced error handling"""
        try:
            data_path = Path(__file__).resolve().parent.parent / "data" / "qa_dataset.json"
            
            if not data_path.exists():
                logger.warning(f"QA dataset not found at {data_path}")
                return
                
            with open(data_path, "r", encoding="utf-8") as f:
                qa_data = json.load(f)
            
            if not isinstance(qa_data, list):
                logger.error("QA dataset must be a list")
                return
                
            # Filter out invalid entries
            valid_qa_pairs = []
            for item in qa_data:
                if isinstance(item, dict) and item.get("question") and item.get("answer"):
                    valid_qa_pairs.append(item)
            
            self.questions = [item.get("question", "").strip() for item in valid_qa_pairs]
            self.answers = [item.get("answer", "").strip() for item in valid_qa_pairs]
            
            if len(self.questions) != len(self.answers):
                logger.error("Questions and answers arrays must have the same length")
                self.questions = []
                self.answers = []
                return
                
            logger.info(f"✅ Loaded {len(self.questions)} QA pairs successfully")
                
        except Exception as e:
            logger.error(f"Error loading QA dataset: {str(e)}")
            self.questions = []
            self.answers = []

    def _initialize_sentence_transformer(self) -> None:
        """Initialize sentence transformer with enhanced error handling"""
        try:
            # Resolve cache folder explicitly (env override or ./models)
            project_root = Path(__file__).resolve().parents[3]
            default_cache = project_root / "models" / "sentence-transformers"
            cache_folder = os.getenv("SENTENCE_TRANSFORMERS_HOME", str(default_cache))

            # device auto selection
            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2",
                device="cuda" if torch.cuda.is_available() else "cpu",
                cache_folder=cache_folder,
            )
            
            # Only create embeddings if we have questions
            if self.questions and len(self.questions) > 0:
                self.q_embeddings = self.model.encode(self.questions, convert_to_tensor=True, device=self.model.device)
                logger.info("✅ Sentence transformer initialized successfully")
            else:
                logger.warning("No questions available for embeddings")
                
        except Exception as e:
            logger.error(f"Error initializing sentence transformer: {str(e)}")
            self.model = None
            self.q_embeddings = None

    def _initialize_gemini(self) -> None:
        """Initialize Gemini with enhanced error handling"""
        try:
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✅ Gemini model initialized successfully")
            else:
                logger.warning("GOOGLE_GEMINI_API_KEY not found - Gemini features disabled")
                self.gemini_model = None
        except Exception as e:
            logger.error(f"Error initializing Gemini: {str(e)}")
            self.gemini_model = None

    def _initialize_document_handler(self) -> None:
        """Initialize document request handler with enhanced error handling"""
        try:
            self.doc_handler = DocumentRequestHandler()
            logger.info("✅ Document request handler initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing document request handler: {str(e)}")
            self.doc_handler = None

    def _is_greeting(self, query: str) -> bool:
        """Check if the query is a greeting"""
        if not query or not isinstance(query, str):
            return False
            
        query_lower = query.lower().strip()
        for pattern in self.greeting_patterns:
            if re.search(pattern, query_lower):
                return True
        return False

    def _is_farewell(self, query: str) -> bool:
        """Check if the query is a farewell or thank you"""
        if not query or not isinstance(query, str):
            return False
            
        query_lower = query.lower().strip()
        for pattern in self.farewell_patterns:
            if re.search(pattern, query_lower):
                return True
        return False

    def _is_help_request(self, query: str) -> bool:
        """Check if the query is asking for help"""
        if not query or not isinstance(query, str):
            return False
            
        query_lower = query.lower().strip()
        for pattern in self.help_patterns:
            if re.search(pattern, query_lower):
                return True
        return False
    
    def _is_document_details_submission(self, query: str) -> bool:
        """Check if the query contains document details submission"""
        if not query or not isinstance(query, str):
            return False
            
        # Check if we have a current document request
        if not hasattr(self, '_current_document_request') or not self._current_document_request:
            return False
        
        # Check if the query contains typical document details
        query_lower = query.lower()
        detail_indicators = [
            'name:', 'employee', 'id:', 'purpose:', 'joining', 'leaving',
            'salary', 'period:', 'financial', 'year:', 'destination',
            'travel', 'dates:', 'visa', 'noc', 'reason:', 'damaged',
            'lost', 'replacement', 'insurance', 'medical'
        ]
        
        return any(indicator in query_lower for indicator in detail_indicators)

    def _get_contextual_response(self, query: str) -> Optional[str]:
        """Get contextual responses based on query type"""
        if not query or not isinstance(query, str):
            return None
            
        query_lower = query.lower().strip()
        
        # Greetings
        if self._is_greeting(query):
            current_hour = datetime.now().hour
            if 5 <= current_hour < 12:
                return "Good morning! ☀️ Welcome to Reliance Jio Infotech Solutions! I'm your AI assistant, ready to help you with HR questions, document processing, and certificate generation. How can I assist you today?"
            elif 12 <= current_hour < 17:
                return "Good afternoon! 🌤️ I hope your day at Reliance Jio Infotech Solutions is going well! I'm ready to assist you with HR queries, document processing, or any other questions you might have. What do you need help with?"
            else:
                return "Good evening! 🌙 I hope you had a great day at Reliance Jio Infotech Solutions! I'm still here to help you with any questions about policies, documents, or certificates. What can I assist you with?"
        
        # Farewells
        elif self._is_farewell(query):
            if 'thank' in query_lower:
                return "You're very welcome! 🙏 I'm here to make your experience at Reliance Jio Infotech Solutions as smooth as possible. If you need anything else - whether it's HR questions, document processing, or certificate generation - just let me know. Have a great day!"
            else:
                return "Goodbye! 👋 Thank you for using the Reliance Jio Infotech Solutions AI assistant. I hope I was able to help you today. Have a wonderful day, and don't hesitate to return if you need assistance with HR questions, document processing, or certificates!"
        
        # Help requests
        elif self._is_help_request(query):
            return "I'm here to help! 🤖 Here's how I can assist you at Reliance Jio Infotech Solutions:\n\n**🎯 Quick Start:**\n• **HR Questions**: Just ask about policies, benefits, procedures\n• **PDF Processing**: Upload any PDF for summarization\n• **Certificates**: Fill the form to generate employee certificates\n\n**💡 Mode Switching:**\n• Click the mode buttons above (HR Q&A, PDF, Certificate)\n• Or type: 'qa', 'summarize', 'certificate'\n\n**🔍 Employee Search:**\n• 'search employee [name/ID]' - Find employee details\n• 'fill form for [name/ID]' - Auto-fill certificate form\n\n**📞 Need More Help?**\n• Ask me anything about company policies\n• I can guide you through any process\n• Contact HR at hr@reliancejio.com for complex issues\n\nWhat would you like to know?"
        
        return None

    async def _generate_dynamic_answer(self, query: str, best_match_idx: int, similarity_score: float) -> str:
        """Generate dynamic answer using AI when exact match not found"""
        try:
            if not self.gemini_model:
                return f"I understand you're asking about '{query}'. While I don't have a specific answer in my database, I can help you with general HR questions. Please contact HR at hr@reliancejio.com for specific queries, or try asking about common topics like attendance, leave, benefits, or IT policies."
            
            # Get the most similar question and answer as context with bounds checking
            similar_question = "general HR question"
            similar_answer = "Please contact HR for assistance."
            
            if (best_match_idx >= 0 and 
                best_match_idx < len(self.questions) and 
                best_match_idx < len(self.answers)):
                similar_question = self.questions[best_match_idx]
                similar_answer = self.answers[best_match_idx]
            
            prompt = f"""
            You are an HR assistant for Reliance Jio Infotech Solutions. A user asked: "{query}"
            
            The most similar question in our database is: "{similar_question}"
            With answer: "{similar_answer}"
            
            Generate a helpful, accurate answer for the user's question. If the similar question is relevant, use it as context. If not, provide a general but helpful response about Reliance Jio Infotech Solutions policies.
            
            Make your answer:
            - Professional and company-branded
            - Include contact information (hr@reliancejio.com)
            - Use emojis and formatting for readability
            - Be concise but comprehensive
            
            Answer:
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                raise Exception("Invalid response from Gemini")
            
        except Exception as e:
            logger.error(f"Error generating dynamic answer: {e}")
            return f"I understand you're asking about '{query}'. While I don't have a specific answer in my database, I can help you with general HR questions. Please contact HR at hr@reliancejio.com for specific queries, or try asking about common topics like attendance, leave, benefits, or IT policies."

    async def _handle_document_details_submission(self, details: str) -> str:
        """Handle document details submission and generate PDF"""
        try:
            if not self.doc_handler:
                return "❌ **Error:** Document request handler is not available. Please try again later."
                
            if not hasattr(self, '_current_document_request') or not self._current_document_request:
                return "❌ **Error:** No document request in progress. Please start a new document request."
                
            doc_type = self._current_document_request.get("doc_type")
            doc_name = self._current_document_request.get("doc_name")
            
            if not doc_type or not doc_name:
                return "❌ **Error:** Invalid document request. Please try again."
            
            # Validate details
            is_valid, validation_message = self.doc_handler.validate_document_details(details, doc_type)
            if not is_valid:
                return f"❌ **Validation Error:** {validation_message}\n\nPlease provide the required information."
            
            # Submit document request and generate PDF
            request = self.doc_handler.submit_document_request(doc_type, doc_name, details)
            
            # Clear current document request
            self._current_document_request = None
            
            # Return appropriate message based on PDF generation status
            if request and request.get("pdf_generated", False):
                return self.doc_handler.get_confirmation_message(
                    doc_name, 
                    request.get("id", "unknown"), 
                    pdf_generated=True
                )
            else:
                return self.doc_handler.get_confirmation_message(
                    doc_name, 
                    request.get("id", "unknown") if request else "unknown", 
                    pdf_generated=False,
                    error=request.get("error") if request else "Unknown error"
                )
                
        except Exception as e:
            # Clear current document request on error
            self._current_document_request = None
            logger.error(f"Error processing document request: {str(e)}")
            return f"❌ **Error processing document request:** {str(e)}\n\nPlease try again or contact HR at hr@reliancejio.com for assistance."

    async def answer(self, query: str) -> str:
        """Enhanced answer method with better conversational handling and error handling"""
        try:
            # Enhanced input validation
            if not query or not isinstance(query, str):
                return "I didn't receive a message. Please try again."
                
            query = query.strip()
            
            # Validate input
            if len(query) == 0:
                return "I didn't receive a message. Please try again."
            
            # Check for document requests first
            if self.doc_handler and self.doc_handler.is_document_request(query):
                return self.doc_handler.get_document_list()
            
            # Check for document choice (numbers 1-16)
            if query.strip().isdigit() and 1 <= int(query.strip()) <= 16:
                if self.doc_handler:
                    is_valid, doc_type, doc_name = self.doc_handler.validate_document_choice(query)
                    if is_valid:
                        # Store current document request
                        self._current_document_request = {
                            "doc_type": doc_type,
                            "doc_name": doc_name
                        }
                        # Return special response to trigger form display
                        return f"SHOW_FORM:{doc_type}:{doc_name}"
                    else:
                        return "Please select a valid document number (1-16)."
                else:
                    return "Document request system is not available. Please try again later."
            
            # Check for document details submission (when user provides details after document selection)
            if hasattr(self, '_current_document_request') and self._current_document_request:
                return await self._handle_document_details_submission(query)
            
            # Check for contextual responses first
            contextual_response = self._get_contextual_response(query)
            if contextual_response:
                return contextual_response
            
            # Use semantic search for policy-related questions
            if (self.model and 
                self.q_embeddings is not None and 
                len(self.questions) > 0 and 
                len(self.answers) > 0):
                try:
                    query_embedding = self.model.encode(query, convert_to_tensor=True, device=self.model.device)
                    similarity_scores = util.cos_sim(query_embedding, self.q_embeddings)[0]
                    best_match_idx = int(similarity_scores.argmax())
                    best_score = float(similarity_scores[best_match_idx])
                    
                    # Lower threshold for better matching
                    if best_score >= 0.6 and best_match_idx < len(self.answers):
                        return self.answers[best_match_idx]
                    
                    # If no good match found, try dynamic answer generation
                    if self.gemini_model and best_score >= 0.4:  # Lower threshold for AI generation
                        return await self._generate_dynamic_answer(query, best_match_idx, best_score)
                    
                except Exception as search_error:
                    logger.error(f"Error in semantic search: {search_error}")
                    # Continue to fallback response
            
            # If no good match found, provide helpful response
            return "I understand you're asking about something, but I'm not finding a specific match in our knowledge base. 🤔\n\n**💡 Here's how I can help:**\n• **HR Policies**: Ask about attendance, leave, benefits, conduct, etc.\n• **IT Policies**: Ask about acceptable use, passwords, devices, software\n• **Document Requests**: Type 'document' or 'I need a document' to request official documents\n• **General Help**: Type 'help' to see all my capabilities\n• **Mode Switching**: Use the buttons above or type 'qa', 'summarize', 'certificate'\n\n**📞 For specific questions not covered here:**\nPlease contact HR at hr@reliancejio.com or IT support for technical issues.\n\nWhat would you like to know about?"
            
        except Exception as e:
            logger.error(f"Error in QA engine answer method: {str(e)}")
            return "I apologize, but I'm experiencing technical difficulties right now. Please try again in a moment or contact HR at hr@reliancejio.com for assistance."


