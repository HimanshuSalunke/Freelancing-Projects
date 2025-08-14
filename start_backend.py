#!/usr/bin/env python3
"""
Script to start the backend server
"""

import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    
    print("🚀 Starting Backend Server")
    print("=" * 30)
    
    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and uvicorn are available")
    except ImportError:
        print("❌ FastAPI or uvicorn not found. Installing requirements...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    
    # Start the server
    print("🌐 Starting FastAPI server on http://localhost:8000")
    print("📝 API documentation will be available at http://localhost:8000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_backend()
