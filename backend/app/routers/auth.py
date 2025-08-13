from datetime import datetime, timedelta
import os
import secrets
from typing import Optional

import jwt
from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALG = "HS256"

router = APIRouter()


class LoginRequest(BaseModel):
    email: str


class OTPVerifyRequest(BaseModel):
    email: str
    otp: str


# In-memory storage for OTPs for demo purposes
email_to_otp: dict[str, str] = {}


def send_email_otp(email: str, otp: str) -> None:
    # Placeholder for integration with a real SMTP/email service
    print(f"[2FA] OTP for {email}: {otp}")


@router.post("/login/request-otp")
async def request_otp(req: LoginRequest) -> dict:
    try:
        validate_email(req.email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    otp = f"{secrets.randbelow(1000000):06d}"
    email_to_otp[req.email.lower()] = otp
    send_email_otp(req.email, otp)
    return {"message": "OTP sent to email"}


@router.post("/login/verify-otp")
async def verify_otp(req: OTPVerifyRequest) -> dict:
    expected = email_to_otp.get(req.email.lower())
    if not expected or expected != req.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")
    # Issue JWT
    payload = {"sub": req.email.lower(), "exp": datetime.utcnow() + timedelta(hours=8)}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str | None) -> Optional[str]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload.get("sub")
    except Exception:
        return None


