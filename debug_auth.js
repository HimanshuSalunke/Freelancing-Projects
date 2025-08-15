// Debug script to test authentication flow
const fetch = require('node-fetch');

async function debugAuth() {
  const baseUrl = 'http://localhost:3000';
  const backendUrl = 'http://localhost:8000';
  
  console.log('🔍 Debugging Authentication Flow...\n');
  
  // Test 1: Check if backend is running
  console.log('1. Testing backend connectivity...');
  try {
    const response = await fetch(`${backendUrl}/`);
    if (response.ok) {
      console.log('✅ Backend is running');
    } else {
      console.log('❌ Backend is not responding properly');
      return;
    }
  } catch (error) {
    console.log('❌ Cannot connect to backend:', error.message);
    return;
  }
  
  // Test 2: Send OTP
  console.log('\n2. Testing OTP sending...');
  try {
    const response = await fetch(`${baseUrl}/api/auth/send-otp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: 'deoredevayani26@gmail.com' }),
    });
    
    const data = await response.json();
    console.log('Response status:', response.status);
    console.log('Response data:', data);
    
    if (response.ok) {
      console.log('✅ OTP sent successfully');
    } else {
      console.log('❌ Failed to send OTP');
      return;
    }
  } catch (error) {
    console.log('❌ Error sending OTP:', error.message);
    return;
  }
  
  // Test 3: Check /me endpoint without authentication
  console.log('\n3. Testing /me endpoint without auth...');
  try {
    const response = await fetch(`${baseUrl}/api/auth/me`);
    const data = await response.json();
    console.log('Response status:', response.status);
    console.log('Response data:', data);
    
    if (response.status === 401) {
      console.log('✅ Properly returns 401 for unauthenticated request');
    } else {
      console.log('❌ Unexpected response for unauthenticated request');
    }
  } catch (error) {
    console.log('❌ Error testing /me endpoint:', error.message);
  }
  
  console.log('\n📝 Next steps:');
  console.log('1. Check your email for the OTP');
  console.log('2. Use the OTP to test the verify-otp endpoint');
  console.log('3. Check if the session cookie is set properly');
}

debugAuth().catch(console.error);
