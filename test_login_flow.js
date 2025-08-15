// Test script for the complete login flow
// Run this in your browser console after the page loads

async function testCompleteLoginFlow() {
  console.log('🧪 Testing Complete Login Flow...\n');
  
  // Step 1: Check if we're on login page
  const isOnLoginPage = window.location.pathname === '/login';
  console.log('1. Current page:', window.location.pathname);
  console.log(isOnLoginPage ? '✅ On login page' : '❌ Not on login page');
  
  // Step 2: Test OTP sending
  console.log('\n2. Testing OTP sending...');
  try {
    const response = await fetch('/api/auth/send-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: 'deoredevayani26@gmail.com' }),
    });
    
    const data = await response.json();
    console.log('OTP send response:', response.status, data);
    
    if (response.ok) {
      console.log('✅ OTP sent successfully');
    } else {
      console.log('❌ Failed to send OTP');
      return;
    }
  } catch (error) {
    console.log('❌ Error sending OTP:', error);
    return;
  }
  
  // Step 3: Check cookies after OTP send
  console.log('\n3. Checking cookies after OTP send...');
  const cookiesAfterOtp = document.cookie;
  console.log('Cookies:', cookiesAfterOtp);
  
  // Step 4: Test /me endpoint before login
  console.log('\n4. Testing /me endpoint before login...');
  try {
    const response = await fetch('/api/auth/me', {
      credentials: 'include'
    });
    
    console.log('/me response status:', response.status);
    
    if (response.status === 401) {
      console.log('✅ Properly returns 401 before login');
    } else {
      console.log('❌ Unexpected response before login');
    }
  } catch (error) {
    console.log('❌ Error testing /me before login:', error);
  }
  
  console.log('\n📝 Next steps:');
  console.log('1. Check your email for the OTP');
  console.log('2. Enter the OTP in the login form');
  console.log('3. Watch the console for verification logs');
  console.log('4. Check if you get redirected to the main page');
}

// Function to test after login
async function testAfterLogin() {
  console.log('🔍 Testing After Login...\n');
  
  // Check current page
  console.log('Current page:', window.location.pathname);
  
  // Check cookies
  const cookies = document.cookie;
  console.log('Cookies:', cookies);
  
  const sessionToken = cookies.split(';').find(cookie => cookie.trim().startsWith('session_token='));
  if (sessionToken) {
    console.log('✅ Session token found:', sessionToken);
  } else {
    console.log('❌ No session token found');
  }
  
  // Test /me endpoint
  console.log('\nTesting /me endpoint...');
  try {
    const response = await fetch('/api/auth/me', {
      credentials: 'include'
    });
    
    console.log('/me response status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ /me endpoint working:', data);
    } else {
      console.log('❌ /me endpoint failed');
    }
  } catch (error) {
    console.log('❌ Error testing /me:', error);
  }
  
  // Test main page access
  console.log('\nTesting main page access...');
  try {
    const response = await fetch('/', {
      credentials: 'include'
    });
    
    console.log('Main page status:', response.status);
    
    if (response.ok) {
      console.log('✅ Main page accessible');
    } else {
      console.log('❌ Main page not accessible');
    }
  } catch (error) {
    console.log('❌ Error accessing main page:', error);
  }
}

// Export functions for use in console
window.testCompleteLoginFlow = testCompleteLoginFlow;
window.testAfterLogin = testAfterLogin;

console.log('🔧 Debug functions loaded:');
console.log('- testCompleteLoginFlow() - Test the complete login flow');
console.log('- testAfterLogin() - Test after successful login');
