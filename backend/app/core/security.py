from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt import decode_token, verify_token_type
from app.core.db import get_users_collection
from bson import ObjectId
from typing import Dict, Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        verify_token_type(payload, "access")
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Fetch user from database
        users_collection = get_users_collection()
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if user is None:
            raise credentials_exception
        
        # Convert ObjectId to string for JSON serialization
        user["_id"] = str(user["_id"])
        return user
        
    except ValueError:
        raise credentials_exception


async def get_current_patient(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Ensure current user is a patient"""
    if current_user.get("role") != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access this resource"
        )
    return current_user


async def get_current_doctor(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Ensure current user is a doctor"""
    if current_user.get("role") != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this resource"
        )
    return current_user
