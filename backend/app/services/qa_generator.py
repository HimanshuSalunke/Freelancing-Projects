import json
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import asyncio

# For document processing
import fitz  # PyMuPDF
from docx import Document
import pandas as pd

# For AI-powered question generation
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import torch


class AdvancedQAGenerator:
    """Advanced QA system with automated question generation and document processing"""
    
    def __init__(self):
        self.qa_file = Path(__file__).parent.parent / "data" / "qa_dataset.json"
        self.policies_dir = Path(__file__).parent.parent.parent.parent / "org_data" / "policies"
        self.it_policies_dir = Path(__file__).parent.parent.parent.parent / "org_data" / "it_policies"
        
        # Initialize Gemini for question generation
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.gemini_model = None
        
        # Initialize sentence transformer for semantic search
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load existing QA data
        self.qa_data = self._load_qa_data()
    
    def _load_qa_data(self) -> List[Dict]:
        """Load existing QA dataset"""
        try:
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_qa_data(self):
        """Save QA dataset"""
        with open(self.qa_file, 'w', encoding='utf-8') as f:
            json.dump(self.qa_data, f, indent=2, ensure_ascii=False)
    
    async def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF document"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path: Path) -> str:
        """Extract text from DOCX document"""
        try:
            doc = Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from {docx_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for processing"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks
    
    async def generate_questions_from_chunk(self, chunk: str, policy_name: str) -> List[Dict]:
        """Generate questions from a text chunk using AI"""
        if not self.gemini_model:
            return []
        
        try:
            prompt = f"""
            Based on the following text from the {policy_name} policy, generate 3-5 natural questions that employees might ask.
            Focus on practical, common questions about policies, procedures, and benefits.
            
            Text:
            {chunk}
            
            Generate questions in this format:
            - Question: [natural question]
            - Answer: [comprehensive answer with formatting]
            
            Make the answers professional, detailed, and include contact information when relevant.
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            # Parse the response to extract Q&A pairs
            qa_pairs = self._parse_qa_response(response.text, policy_name)
            return qa_pairs
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
    
    def _parse_qa_response(self, response: str, policy_name: str) -> List[Dict]:
        """Parse AI response to extract Q&A pairs"""
        qa_pairs = []
        lines = response.split('\n')
        
        current_question = ""
        current_answer = ""
        in_answer = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('- Question:') or line.startswith('Question:'):
                # Save previous pair if exists
                if current_question and current_answer:
                    qa_pairs.append({
                        "question": current_question,
                        "answer": current_answer,
                        "source": policy_name,
                        "generated": True,
                        "timestamp": datetime.now().isoformat()
                    })
                
                current_question = line.replace('- Question:', '').replace('Question:', '').strip()
                current_answer = ""
                in_answer = False
                
            elif line.startswith('- Answer:') or line.startswith('Answer:'):
                in_answer = True
                current_answer = line.replace('- Answer:', '').replace('Answer:', '').strip()
                
            elif in_answer and line:
                current_answer += "\n" + line
        
        # Add the last pair
        if current_question and current_answer:
            qa_pairs.append({
                "question": current_question,
                "answer": current_answer,
                "source": policy_name,
                "generated": True,
                "timestamp": datetime.now().isoformat()
            })
        
        return qa_pairs
    
    async def process_policy_documents(self):
        """Process all policy documents and generate Q&A pairs"""
        print("🔄 Processing policy documents for Q&A generation...")
        
        # Process HR policies
        if self.policies_dir.exists():
            for policy_file in self.policies_dir.glob("*.pdf"):
                await self._process_single_policy(policy_file, "HR Policy")
        
        # Process IT policies
        if self.it_policies_dir.exists():
            for policy_file in self.it_policies_dir.glob("*.pdf"):
                await self._process_single_policy(policy_file, "IT Policy")
    
    async def _process_single_policy(self, policy_file: Path, policy_type: str):
        """Process a single policy document"""
        print(f"📄 Processing {policy_file.name}...")
        
        # Extract text
        text = await self.extract_text_from_pdf(policy_file)
        if not text:
            return
        
        # Chunk the text
        chunks = self.chunk_text(text)
        
        # Generate questions for each chunk
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 100:  # Skip very short chunks
                continue
                
            policy_name = f"{policy_type}: {policy_file.stem}"
            qa_pairs = await self.generate_questions_from_chunk(chunk, policy_name)
            
            # Add to dataset
            for qa_pair in qa_pairs:
                # Check for duplicates
                if not self._is_duplicate_question(qa_pair["question"]):
                    self.qa_data.append(qa_pair)
        
        print(f"✅ Generated {len(qa_pairs)} Q&A pairs from {policy_file.name}")
    
    def _is_duplicate_question(self, question: str) -> bool:
        """Check if question already exists in dataset"""
        question_lower = question.lower().strip()
        for existing_qa in self.qa_data:
            if existing_qa["question"].lower().strip() == question_lower:
                return True
        return False
    
    def get_semantic_suggestions(self, query: str, limit: int = 5) -> List[Dict]:
        """Get semantic suggestions for user queries"""
        if not self.qa_data:
            return []
        
        # Encode query and questions
        query_embedding = self.sentence_model.encode(query)
        questions = [qa["question"] for qa in self.qa_data]
        question_embeddings = self.sentence_model.encode(questions)
        
        # Calculate similarities
        similarities = torch.cosine_similarity(
            torch.tensor(query_embedding).unsqueeze(0),
            torch.tensor(question_embeddings)
        )
        
        # Get top matches
        top_indices = torch.argsort(similarities, descending=True)[:limit]
        
        suggestions = []
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Minimum similarity threshold
                suggestions.append({
                    "question": self.qa_data[idx]["question"],
                    "answer": self.qa_data[idx]["answer"],
                    "similarity": float(similarities[idx]),
                    "source": self.qa_data[idx].get("source", "Unknown")
                })
        
        return suggestions
    
    def update_qa_from_feedback(self, question: str, answer: str, feedback: str):
        """Update QA based on user feedback"""
        # Find existing QA pair
        for qa in self.qa_data:
            if qa["question"].lower().strip() == question.lower().strip():
                # Update based on feedback
                if feedback == "incorrect":
                    qa["needs_review"] = True
                    qa["feedback"] = feedback
                elif feedback == "improve":
                    qa["answer"] = answer
                    qa["last_updated"] = datetime.now().isoformat()
                break
    
    def export_qa_statistics(self) -> Dict:
        """Export QA system statistics"""
        total_qa = len(self.qa_data)
        generated_qa = len([qa for qa in self.qa_data if qa.get("generated", False)])
        manual_qa = total_qa - generated_qa
        
        sources = {}
        for qa in self.qa_data:
            source = qa.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_qa_pairs": total_qa,
            "generated_qa_pairs": generated_qa,
            "manual_qa_pairs": manual_qa,
            "sources": sources,
            "last_updated": datetime.now().isoformat()
        }
    
    async def auto_update_qa_system(self):
        """Automatically update QA system from new documents"""
        print("🔄 Auto-updating QA system...")
        
        # Process new policy documents
        await self.process_policy_documents()
        
        # Save updated dataset
        self._save_qa_data()
        
        # Generate statistics
        stats = self.export_qa_statistics()
        print(f"✅ QA system updated: {stats['total_qa_pairs']} total Q&A pairs")
        
        return stats
