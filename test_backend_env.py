#!/usr/bin/env python3
"""
Test script to check backend environment variables
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent
env_path = project_root / ".env"

print("🔍 Testing Backend Environment Variables")
print("=" * 50)

if env_path.exists():
    print(f"✅ .env file found at: {env_path}")
    load_dotenv(env_path)
else:
    print(f"❌ .env file not found at: {env_path}")
    print("Loading from current directory...")
    load_dotenv()

# Check required environment variables
required_vars = [
    "EMAIL_USER",
    "EMAIL_PASS", 
    "JWT_SECRET",
    "BACKEND_URL"
]

print("\n📋 Environment Variables Check:")
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if var in ["EMAIL_PASS", "JWT_SECRET"]:
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: Not set")

# Test email configuration
print("\n📧 Email Configuration Test:")
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")

if email_user and email_pass:
    print(f"✅ Email user: {email_user}")
    print(f"✅ Email password: {'*' * len(email_pass)}")
    
    # Test if it looks like a Gmail app password
    if len(email_pass.replace(" ", "")) == 16:
        print("✅ Email password format looks correct (16 characters)")
    else:
        print("⚠️ Email password format may be incorrect")
else:
    print("❌ Email configuration incomplete")

# Test JWT secret
print("\n🔐 JWT Secret Test:")
jwt_secret = os.getenv("JWT_SECRET")
if jwt_secret:
    if len(jwt_secret) >= 32:
        print("✅ JWT secret is sufficiently long")
    else:
        print("⚠️ JWT secret may be too short")
else:
    print("❌ JWT secret not set")

print("\n🎯 Summary:")
if all(os.getenv(var) for var in required_vars):
    print("✅ All required environment variables are set")
    print("✅ Backend should be able to start properly")
else:
    print("❌ Some environment variables are missing")
    print("❌ Please check your .env file")
