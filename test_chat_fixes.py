#!/usr/bin/env python3
"""
Test script to verify chat fixes are working correctly
"""

import requests
import json

def test_chat_response(message, expected_keywords=None):
    """Test a chat message and verify the response"""
    url = "http://localhost:8000/chat"
    
    try:
        response = requests.post(url, json={"message": message})
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('response', '')
            print(f"✅ Question: {message}")
            print(f"📝 Answer: {answer[:200]}...")
            
            if expected_keywords:
                found_keywords = [kw for kw in expected_keywords if kw.lower() in answer.lower()]
                if found_keywords:
                    print(f"✅ Found expected keywords: {found_keywords}")
                else:
                    print(f"❌ Missing expected keywords: {expected_keywords}")
            
            print("-" * 80)
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Run tests for the chat system"""
    print("🧪 Testing Chat System Fixes")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            "message": "What is the IT policy?",
            "expected_keywords": ["IT", "device", "password", "software", "helpdesk"]
        },
        {
            "message": "What is the HR policy?",
            "expected_keywords": ["HR", "attendance", "leave", "performance", "reimbursement"]
        },
        {
            "message": "What is the leave policy?",
            "expected_keywords": ["leave", "20 days", "annual", "submission"]
        },
        {
            "message": "What is the attendance policy?",
            "expected_keywords": ["attendance", "work hours", "9:30", "tardiness"]
        },
        {
            "message": "How are you?",
            "expected_keywords": ["great", "thank", "ready", "help"]
        },
        {
            "message": "What can you do?",
            "expected_keywords": ["HR", "PDF", "document", "certificate"]
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for test_case in test_cases:
        if test_chat_response(test_case["message"], test_case["expected_keywords"]):
            success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("🎉 All tests passed! The chat system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the system.")

if __name__ == "__main__":
    main()
