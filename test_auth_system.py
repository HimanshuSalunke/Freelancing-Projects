#!/usr/bin/env python3
"""
Test script for the authentication system
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "deoredevayani26@gmail.com"  # First authorized user

def test_auth_endpoints():
    """Test all authentication endpoints"""
    
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    # Test 1: Send OTP
    print("\n1. Testing Send OTP...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/send-otp",
            json={"email": TEST_EMAIL},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ OTP sent successfully")
            data = response.json()
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Failed to send OTP: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending OTP: {e}")
        return False
    
    # Test 2: Try to get user info without authentication
    print("\n2. Testing unauthorized access...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        
        if response.status_code == 401:
            print("✅ Unauthorized access properly blocked")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing unauthorized access: {e}")
    
    # Test 3: Test invalid email
    print("\n3. Testing invalid email...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/send-otp",
            json={"email": "invalid@email.com"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Invalid email properly rejected")
            data = response.json()
            print(f"   Error: {data.get('detail')}")
        else:
            print(f"❌ Unexpected response for invalid email: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing invalid email: {e}")
    
    # Test 4: Test fake employee email (should be rejected)
    print("\n4. Testing fake employee email...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/send-otp",
            json={"email": "vjenkins@rios.com"},  # 5th employee (fake)
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Fake employee email properly rejected")
            data = response.json()
            print(f"   Error: {data.get('detail')}")
        else:
            print(f"❌ Unexpected response for fake employee: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing fake employee: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Authentication system tests completed!")
    print("\n📝 Note: To test OTP verification, you need to:")
    print("   1. Check your email for the OTP")
    print("   2. Use the OTP to test the verify-otp endpoint")
    print("   3. Test the /me endpoint with authentication")
    
    return True

def test_employee_validation():
    """Test employee validation logic"""
    
    print("\n🧪 Testing Employee Validation")
    print("=" * 50)
    
    # Test authorized employees
    authorized_emails = [
        "deoredevayani26@gmail.com",
        "nikumbhashwini17@gmail.com", 
        "jainkhushbu1810@gmail.com",
        "mansibadgujar99@gmail.com"
    ]
    
    print("\n1. Testing authorized employees...")
    for email in authorized_emails:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/send-otp",
                json={"email": email},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ {email} - Authorized")
            else:
                print(f"❌ {email} - Unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {email} - Error: {e}")
    
    # Test unauthorized employees
    unauthorized_emails = [
        "vjenkins@rios.com",
        "harmstrong@mann.com",
        "bhill@moore.com"
    ]
    
    print("\n2. Testing unauthorized employees...")
    for email in unauthorized_emails:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/send-otp",
                json={"email": email},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print(f"✅ {email} - Properly rejected")
            else:
                print(f"❌ {email} - Unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {email} - Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Authentication System Tests")
    print("Make sure the backend is running on http://localhost:8000")
    print()
    
    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend is not responding properly")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Please start the backend with: python -m uvicorn app.main:app --reload --port 8000")
        exit(1)
    
    # Run tests
    test_auth_endpoints()
    test_employee_validation()
    
    print("\n🎉 All tests completed!")
