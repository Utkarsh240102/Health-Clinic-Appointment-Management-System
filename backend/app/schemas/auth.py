from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class PatientSignupRequest(BaseModel):
    """Patient signup request schema"""
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    password: str = Field(..., min_length=8, max_length=100)
    photo: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=150)
    gender: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema (for both patient and doctor)"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response"""
    access_token: str
    token_type: str = "bearer"
