// Browser-based debug script for authentication
// Run this in your browser console after logging in

async function debugAuthInBrowser() {
  console.log('🔍 Debugging Authentication in Browser...\n');
  
  // Check if we have a session token
  const cookies = document.cookie;
  console.log('📋 All cookies:', cookies);
  
  const sessionToken = cookies.split(';').find(cookie => cookie.trim().startsWith('session_token='));
  if (sessionToken) {
    console.log('✅ Session token found:', sessionToken);
  } else {
    console.log('❌ No session token found');
  }
  
  // Test /me endpoint
  console.log('\n🧪 Testing /me endpoint...');
  try {
    const response = await fetch('/api/auth/me', {
      credentials: 'include'
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));
    
    const data = await response.json();
    console.log('Response data:', data);
    
    if (response.ok) {
      console.log('✅ /me endpoint working correctly');
      console.log('👤 User info:', data.user);
    } else {
      console.log('❌ /me endpoint failed');
    }
  } catch (error) {
    console.log('❌ Error testing /me endpoint:', error);
  }
  
  // Test if we can access the main page
  console.log('\n🏠 Testing main page access...');
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

// Run the debug function
debugAuthInBrowser();
