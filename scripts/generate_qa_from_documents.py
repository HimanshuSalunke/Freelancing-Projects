#!/usr/bin/env python3
"""
Advanced QA Generation Script
Automatically generates Q&A pairs from policy documents using AI
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# Add the backend directory to the path
backend_dir = project_root / "backend"
sys.path.append(str(backend_dir))

from app.services.qa_generator import AdvancedQAGenerator


async def main():
    """Main function to generate QA from documents"""
    print("🚀 Starting Advanced QA Generation from Policy Documents...")
    
    # Initialize the QA generator
    qa_generator = AdvancedQAGenerator()
    
    try:
        # Check if Gemini API key is available
        if not qa_generator.gemini_model:
            print("❌ Error: GOOGLE_GEMINI_API_KEY not found in environment variables")
            print("Please set the API key to enable AI-powered question generation")
            return
        
        print("✅ Gemini API key found")
        print("📄 Processing policy documents...")
        
        # Process policy documents and generate QA pairs
        stats = await qa_generator.auto_update_qa_system()
        
        print("\n📊 QA Generation Complete!")
        print(f"📈 Total Q&A pairs: {stats['total_qa_pairs']}")
        print(f"🤖 Generated Q&A pairs: {stats['generated_qa_pairs']}")
        print(f"✍️ Manual Q&A pairs: {stats['manual_qa_pairs']}")
        print(f"📅 Last updated: {stats['last_updated']}")
        
        print("\n📚 Sources:")
        for source, count in stats['sources'].items():
            print(f"   • {source}: {count} Q&A pairs")
        
        print("\n✅ QA system is now ready with enhanced knowledge base!")
        
    except Exception as e:
        print(f"❌ Error during QA generation: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
