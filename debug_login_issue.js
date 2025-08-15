// Comprehensive debugging script for login issue
// Run this in your browser console

async function debugLoginIssue() {
  console.log('🔍 DEBUGGING LOGIN ISSUE');
  console.log('=' * 50);
  
  // Step 1: Check current page
  console.log('1. Current page:', window.location.pathname);
  console.log('2. Full URL:', window.location.href);
  
  // Step 2: Check cookies
  console.log('\n3. Checking cookies...');
  const cookies = document.cookie;
  console.log('All cookies:', cookies);
  
  const sessionToken = cookies.split(';').find(cookie => cookie.trim().startsWith('session_token='));
  if (sessionToken) {
    console.log('✅ Session token found:', sessionToken);
  } else {
    console.log('❌ No session token found');
  }
  
  // Step 3: Test OTP sending
  console.log('\n4. Testing OTP sending...');
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
    }
  } catch (error) {
    console.log('❌ Error sending OTP:', error);
  }
  
  // Step 4: Test /me endpoint
  console.log('\n5. Testing /me endpoint...');
  try {
    const response = await fetch('/api/auth/me', {
      credentials: 'include'
    });
    
    console.log('/me response status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ /me endpoint working:', data);
    } else {
      const data = await response.json();
      console.log('❌ /me endpoint failed:', data);
    }
  } catch (error) {
    console.log('❌ Error testing /me:', error);
  }
  
  // Step 5: Test main page access
  console.log('\n6. Testing main page access...');
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
  
  // Step 6: Check if backend is running
  console.log('\n7. Testing backend connectivity...');
  try {
    const response = await fetch('http://localhost:8000/');
    console.log('Backend status:', response.status);
    
    if (response.ok) {
      console.log('✅ Backend is running');
    } else {
      console.log('❌ Backend not responding properly');
    }
  } catch (error) {
    console.log('❌ Cannot connect to backend:', error);
  }
}

// Function to simulate the complete login flow
async function simulateLoginFlow() {
  console.log('🧪 SIMULATING COMPLETE LOGIN FLOW');
  console.log('=' * 50);
  
  // Step 1: Send OTP
  console.log('1. Sending OTP...');
  try {
    const response = await fetch('/api/auth/send-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: 'deoredevayani26@gmail.com' }),
    });
    
    const data = await response.json();
    console.log('OTP send result:', response.status, data);
    
    if (!response.ok) {
      console.log('❌ OTP send failed, stopping test');
      return;
    }
  } catch (error) {
    console.log('❌ Error sending OTP:', error);
    return;
  }
  
  // Step 2: Check cookies after OTP send
  console.log('\n2. Cookies after OTP send:', document.cookie);
  
  // Step 3: Test /me before login
  console.log('\n3. Testing /me before login...');
  try {
    const response = await fetch('/api/auth/me', {
      credentials: 'include'
    });
    
    console.log('/me before login:', response.status);
    
    if (response.status === 401) {
      console.log('✅ Correctly returns 401 before login');
    } else {
      console.log('❌ Unexpected response before login');
    }
  } catch (error) {
    console.log('❌ Error testing /me before login:', error);
  }
  
  console.log('\n📝 Next steps:');
  console.log('1. Check your email for the OTP');
  console.log('2. Enter the OTP in the login form');
  console.log('3. Watch for console logs during verification');
  console.log('4. Check if redirect happens');
}

// Function to test after OTP verification
async function testAfterOTPVerification() {
  console.log('🔍 TESTING AFTER OTP VERIFICATION');
  console.log('=' * 50);
  
  // Check current page
  console.log('1. Current page:', window.location.pathname);
  
  // Check cookies
  console.log('\n2. Cookies after verification:', document.cookie);
  
  const sessionToken = document.cookie.split(';').find(cookie => cookie.trim().startsWith('session_token='));
  if (sessionToken) {
    console.log('✅ Session token found after verification');
  } else {
    console.log('❌ No session token found after verification');
  }
  
  // Test /me endpoint
  console.log('\n3. Testing /me after verification...');
  try {
    const response = await fetch('/api/auth/me', {
      credentials: 'include'
    });
    
    console.log('/me after verification:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ /me working after verification:', data);
    } else {
      const data = await response.json();
      console.log('❌ /me failed after verification:', data);
    }
  } catch (error) {
    console.log('❌ Error testing /me after verification:', error);
  }
  
  // Test main page access
  console.log('\n4. Testing main page access after verification...');
  try {
    const response = await fetch('/', {
      credentials: 'include'
    });
    
    console.log('Main page after verification:', response.status);
    
    if (response.ok) {
      console.log('✅ Main page accessible after verification');
    } else {
      console.log('❌ Main page not accessible after verification');
    }
  } catch (error) {
    console.log('❌ Error accessing main page after verification:', error);
  }
}

// Export functions
window.debugLoginIssue = debugLoginIssue;
window.simulateLoginFlow = simulateLoginFlow;
window.testAfterOTPVerification = testAfterOTPVerification;

console.log('🔧 Debug functions loaded:');
console.log('- debugLoginIssue() - Comprehensive debugging');
console.log('- simulateLoginFlow() - Simulate complete login flow');
console.log('- testAfterOTPVerification() - Test after OTP verification');
