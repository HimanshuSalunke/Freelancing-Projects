#!/usr/bin/env python3
"""
MongoDB Atlas Setup Script for HR Assistant Project
This script helps you migrate from local JSON files to MongoDB Atlas
"""

import os
import json
import sys
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚀 MongoDB Atlas Setup for HR Assistant Project")
    print("=" * 60)

def print_mongodb_setup_instructions():
    print("\n📋 MongoDB Atlas Setup Instructions:")
    print("1. Go to https://www.mongodb.com/atlas")
    print("2. Create a free account")
    print("3. Create a new cluster (M0 Free tier)")
    print("4. Set up database access (create username/password)")
    print("5. Set up network access (allow from anywhere: 0.0.0.0/0)")
    print("6. Get your connection string")
    print("\n🔗 Connection String Format:")
    print("mongodb+srv://username:password@cluster.mongodb.net/hr_assistant?retryWrites=true&w=majority")

def create_env_template():
    """Create .env template with MongoDB configuration"""
    env_content = """# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/hr_assistant?retryWrites=true&w=majority

# Existing Configuration
GOOGLE_GEMINI_API_KEY=your-gemini-api-key
DISABLE_AUTH=false
ORG_NAME="Reliance Jio Infotech Solutions"
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env template file")
        print("📝 Please update the MONGODB_URI with your actual connection string")
    else:
        print("⚠️ .env file already exists. Please add MONGODB_URI manually")

def check_json_files():
    """Check if JSON data files exist"""
    data_dir = Path("backend/app/data")
    required_files = ["employees.json", "qa_dataset.json", "bad_words.json"]
    
    print("\n📁 Checking JSON data files:")
    all_exist = True
    
    for file_name in required_files:
        file_path = data_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} - Found")
        else:
            print(f"❌ {file_name} - Missing")
            all_exist = False
    
    return all_exist

def show_migration_steps():
    """Show migration steps"""
    print("\n🔄 Migration Steps:")
    print("1. Set up MongoDB Atlas cluster")
    print("2. Update .env file with MONGODB_URI")
    print("3. Install MongoDB dependencies:")
    print("   pip install motor pymongo")
    print("4. Run the application - employee data will migrate to MongoDB")
    print("5. QA dataset and other data remain in local JSON files")
    print("6. Verify employee data in MongoDB Atlas dashboard")

def main():
    print_banner()
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Check JSON files
    json_files_exist = check_json_files()
    
    if not json_files_exist:
        print("\n❌ Some JSON files are missing. Please ensure all data files exist.")
        sys.exit(1)
    
    # Show setup instructions
    print_mongodb_setup_instructions()
    
    # Create .env template
    create_env_template()
    
    # Show migration steps
    show_migration_steps()
    
    print("\n🎉 Setup complete! Follow the instructions above to configure MongoDB Atlas.")
    print("\n💡 Pro Tips:")
    print("- Use MongoDB Compass for visual database management")
    print("- Set up database indexes for better performance")
    print("- Enable MongoDB Atlas monitoring for insights")
    print("- Employee data will be in MongoDB Atlas")
    print("- QA dataset and other data stay in local JSON files")

if __name__ == "__main__":
    main()
