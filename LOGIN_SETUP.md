# Login System Setup Guide

## Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Email Configuration for OTP
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# JWT Secret (change this in production)
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Backend URL
BACKEND_URL=http://localhost:8000

# Next.js Environment
NODE_ENV=development
```

## Email Setup Instructions

1. **Gmail Account Setup**:
   - Use a Gmail account for sending OTP emails
   - Enable 2-Factor Authentication on your Gmail account
   - Generate an App Password:
     - Go to Google Account Settings
     - Security → 2-Step Verification → App passwords
     - Generate a new app password for "Mail"
     - Use this password in `EMAIL_PASS`

2. **Email Credentials**:
   - `EMAIL_USER`: Your Gmail address
   - `EMAIL_PASS`: The app password generated above

## Authorized Users

Only the first 4 employees in the database can log in:

1. **Devyani Suresh Deore** - deoredevayani26@gmail.com
2. **Ashwini Anil Nikumbh** - nikumbhashwini17@gmail.com  
3. **Khushbu Arun Jain** - jainkhushbu1810@gmail.com
4. **Mansi Anil Badgujar** - mansibadgujar99@gmail.com

## Features Implemented

✅ **Login Flow**:
- Email validation against authorized users
- OTP generation and email sending
- 6-digit OTP with 5-minute expiry
- OTP verification and session creation

✅ **Security**:
- JWT token-based authentication
- Session cookies with proper security settings
- Middleware protection for all routes
- Automatic redirect to login for unauthenticated users

✅ **User Interface**:
- Responsive login page with email/OTP flow
- User information display in header
- Logout functionality
- Loading states and error handling

✅ **API Endpoints**:
- `/api/auth/send-otp` - Send OTP to email
- `/api/auth/verify-otp` - Verify OTP and create session
- `/api/auth/resend-otp` - Resend OTP
- `/api/auth/logout` - Clear session and logout
- `/api/auth/me` - Get current user information

## Running the Application

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend**:
   ```bash
   npm run dev
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Testing the Login System

1. Navigate to http://localhost:3000
2. You'll be redirected to http://localhost:3000/login
3. Enter one of the authorized email addresses
4. Check your email for the OTP
5. Enter the OTP to log in
6. You'll be redirected to the main application

## Security Notes

- The system only allows the first 4 employees to log in
- OTP expires after 5 minutes
- Maximum 3 failed OTP attempts before requiring a new OTP
- Session tokens expire after 24 hours
- All routes are protected by authentication middleware
