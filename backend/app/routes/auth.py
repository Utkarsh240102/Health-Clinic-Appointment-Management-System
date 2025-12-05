from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import (
    PatientSignupRequest, 
    LoginRequest, 
    TokenResponse, 
    RefreshTokenRequest,
    TokenRefreshResponse
)
from app.services.user_service import (
    create_patient,
    authenticate_user,
    generate_tokens,
    refresh_access_token
)

router = APIRouter()


@router.post("/patient/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def patient_signup(request: PatientSignupRequest):
    """
    Patient signup endpoint
    
    - Creates a new patient account
    - Returns access token, refresh token, and user data
    """
    # Create patient
    user = await create_patient(
        name=request.name,
        email=request.email,
        phone=request.phone,
        password=request.password,
        photo=request.photo,
        age=request.age,
        gender=request.gender
    )
    
    # Generate tokens
    tokens = await generate_tokens(user)
    
    return {
        **tokens,
        "token_type": "bearer",
        "user": user
    }


@router.post("/patient/login", response_model=TokenResponse)
async def patient_login(request: LoginRequest):
    """
    Patient login endpoint
    
    - Authenticates patient by email and password
    - Returns access token, refresh token, and user data
    """
    # Authenticate patient
    user = await authenticate_user(request.email, request.password, required_role="patient")
    
    # Generate tokens
    tokens = await generate_tokens(user)
    
    return {
        **tokens,
        "token_type": "bearer",
        "user": user
    }


@router.post("/doctor/login", response_model=TokenResponse)
async def doctor_login(request: LoginRequest):
    """
    Doctor login endpoint (only for seeded doctors)
    
    - Authenticates doctor by email and password
    - Returns access token, refresh token, and user data
    - Note: Doctors cannot signup, only login with pre-seeded accounts
    """
    # Authenticate doctor
    user = await authenticate_user(request.email, request.password, required_role="doctor")
    
    # Generate tokens
    tokens = await generate_tokens(user)
    
    return {
        **tokens,
        "token_type": "bearer",
        "user": user
    }


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token
    
    - Accepts a valid refresh token
    - Returns a new access token
    """
    access_token = await refresh_access_token(request.refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
