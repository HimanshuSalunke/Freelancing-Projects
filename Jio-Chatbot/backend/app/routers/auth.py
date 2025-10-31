import os
import json
import random
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
import jwt
from dotenv import load_dotenv
from ..services.db import db_service
from ..config import get_app_name

# Load environment variables
load_dotenv()

router = APIRouter()
security = HTTPBearer()

# In-memory storage for OTPs (in production, use Redis or database)
otp_storage: Dict[str, Dict] = {}

# JWT secret key (in production, use a secure secret)
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

class EmailRequest(BaseModel):
    email: EmailStr

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None

async def load_employees():
    """Load employees from local JSON file (for authentication, always use local data)"""
    try:
        # ALWAYS use local JSON file for authentication
        # This ensures the correct team members (from employees.json) can login
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "employees.json")
        
        print(f"[DEBUG] Loading employees from: {json_path}")
        
        with open(json_path, "r", encoding="utf-8") as f:
            employees = json.load(f)
            print(f"[DEBUG] Successfully loaded {len(employees)} employees from local JSON")
            return employees
    except Exception as e:
        print(f"[ERROR] Error loading employees: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Employee database not found: {str(e)}")

async def is_valid_employee(email: str) -> bool:
    """Check if email belongs to one of the first 4 employees"""
    try:
        employees = await load_employees()
        print(f"[DEBUG] Loaded {len(employees)} employees from database")
        
        # Only first 4 employees are allowed to login
        allowed_employees = employees[:4]
        print(f"[DEBUG] First 4 employees: {[emp.get('email', 'N/A') for emp in allowed_employees]}")
        print(f"[DEBUG] Checking email: {email.lower()}")
        
        is_valid = any(emp["email"].lower() == email.lower() for emp in allowed_employees)
        print(f"[DEBUG] Is valid employee: {is_valid}")
        
        return is_valid
    except Exception as e:
        print(f"[ERROR] Error in is_valid_employee: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def get_employee_by_email(email: str):
    """Get employee details by email"""
    employees = await load_employees()
    for emp in employees[:4]:  # Only check first 4 employees
        if emp["email"].lower() == email.lower():
            return emp
    return None

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_email_otp(email: str, otp: str) -> bool:
    """Send OTP via email using Gmail SMTP"""
    try:
        # Email configuration (sanitize to avoid hidden spaces/quotes)
        sender_email = os.getenv("EMAIL_USER") or ""
        sender_password = os.getenv("EMAIL_PASS") or ""
        sender_email = sender_email.strip().strip('"').strip("'")
        # Gmail App Passwords are 16 chars without spaces; remove any accidental spaces
        sender_password = sender_password.strip().strip('"').strip("'").replace(" ", "")
        
        if not sender_email or not sender_password:
            raise Exception("Email credentials not configured")
        
        # Create message
        app_name = get_app_name()
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = f"Login OTP - {app_name}"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>Login OTP</h2>
            <p>Your OTP for logging into {app_name} is:</p>
            <h1 style="color: #007bff; font-size: 32px; letter-spacing: 5px;">{otp}</h1>
            <p>This OTP will expire in 5 minutes.</p>
            <p>If you didn't request this OTP, please ignore this email.</p>
            <br>
            <p>Best regards,<br>{app_name} Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def create_jwt_token(email: str, emp_id: int) -> str:
    """Create JWT token for authenticated user"""
    payload = {
        "email": email,
        "emp_id": emp_id,
        "exp": datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/send-otp", response_model=AuthResponse)
async def send_otp(request: EmailRequest):
    """Send OTP to user's email"""
    email = request.email.lower()
    
    # Check if email is valid
    if not await is_valid_employee(email):
        raise HTTPException(status_code=400, detail="Invalid Email ID")
    
    # Generate OTP
    otp = generate_otp()
    expiry_time = datetime.utcnow() + timedelta(minutes=5)
    
    # Store OTP with expiry
    otp_storage[email] = {
        "otp": otp,
        "expiry": expiry_time,
        "attempts": 0
    }
    
    # Send OTP via email
    if send_email_otp(email, otp):
        return AuthResponse(
            success=True,
            message="OTP sent successfully to your email"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: OTPVerification, response: Response):
    """Verify OTP and create session"""
    email = request.email.lower()
    otp = request.otp
    
    # Check if OTP exists
    if email not in otp_storage:
        raise HTTPException(status_code=400, detail="No OTP found. Please request a new OTP")
    
    otp_data = otp_storage[email]
    
    # Check if OTP has expired
    if datetime.utcnow() > otp_data["expiry"]:
        del otp_storage[email]
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new OTP")
    
    # Check attempts
    if otp_data["attempts"] >= 3:
        del otp_storage[email]
        raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new OTP")
    
    # Verify OTP
    if otp_data["otp"] != otp:
        otp_data["attempts"] += 1
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Get employee details
    employee = await get_employee_by_email(email)
    if not employee:
        raise HTTPException(status_code=400, detail="Employee not found")
    
    # Create JWT token
    token = create_jwt_token(email, employee["emp_id"])
    
    # Clear OTP from storage
    del otp_storage[email]
    
    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400  # 24 hours
    )
    
    return AuthResponse(
        success=True,
        message="Login successful",
        token=token
    )

@router.post("/resend-otp", response_model=AuthResponse)
async def resend_otp(request: EmailRequest):
    """Resend OTP to user's email"""
    email = request.email.lower()
    
    # Check if email is valid
    if not await is_valid_employee(email):
        raise HTTPException(status_code=400, detail="Invalid Email ID")
    
    # Remove existing OTP if any
    if email in otp_storage:
        del otp_storage[email]
    
    # Generate new OTP
    otp = generate_otp()
    expiry_time = datetime.utcnow() + timedelta(minutes=5)
    
    # Store new OTP
    otp_storage[email] = {
        "otp": otp,
        "expiry": expiry_time,
        "attempts": 0
    }
    
    # Send new OTP via email
    if send_email_otp(email, otp):
        return AuthResponse(
            success=True,
            message="New OTP sent successfully to your email"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/logout", response_model=AuthResponse)
async def logout(response: Response):
    """Logout user and clear session"""
    response.delete_cookie("session_token")
    return AuthResponse(
        success=True,
        message="Logged out successfully"
    )

@router.get("/me")
async def get_current_user(request: Request):
    """Get current user information"""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = verify_jwt_token(token)
        employee = await get_employee_by_email(payload["email"])
        if not employee:
            raise HTTPException(status_code=401, detail="Employee not found")
        
        return {
            "success": True,
            "user": {
                "emp_id": employee["emp_id"],
                "full_name": employee["full_name"],
                "email": employee["email"],
                "designation": employee["designation"],
                "department": employee["department"],
                "project_role": employee.get("project_role", "Team Member")
            }
        }
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid session")

# Dependency for protected routes
async def get_current_user_dependency(request: Request):
    """Dependency to get current user for protected routes"""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_jwt_token(token)
    employee = await get_employee_by_email(payload["email"])
    if not employee:
        raise HTTPException(status_code=401, detail="Employee not found")
    
    return employee


