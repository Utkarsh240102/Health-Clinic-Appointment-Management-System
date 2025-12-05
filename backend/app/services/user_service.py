from fastapi import HTTPException, status
from app.core.db import get_users_collection
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token, decode_token, verify_token_type
from app.models.user_model import UserModel
from bson import ObjectId
from datetime import datetime
from typing import Dict, Any
from pymongo import ReturnDocument


async def create_patient(name: str, email: str, phone: str, password: str, 
                        photo: str = None, age: int = None, gender: str = None) -> Dict[str, Any]:
    """Create a new patient account"""
    users_collection = get_users_collection()
    
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if phone already exists
    existing_phone = await users_collection.find_one({"phone": phone})
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create user document
    user_doc = {
        "role": "patient",
        "name": name,
        "email": email,
        "phone": phone,
        "passwordHash": hash_password(password),
        "photoUrl": photo,
        "createdAt": datetime.utcnow(),
        "patientProfile": {
            "age": age,
            "gender": gender,
            "notes": None
        }
    }
    
    # Insert into database
    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = str(result.inserted_id)
    
    # Remove password hash from response
    del user_doc["passwordHash"]
    
    return user_doc


async def authenticate_user(email: str, password: str, required_role: str = None) -> Dict[str, Any]:
    """Authenticate user by email and password"""
    users_collection = get_users_collection()
    
    # Find user by email
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(password, user["passwordHash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check role if specified
    if required_role and user["role"] != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only {required_role}s can access this endpoint"
        )
    
    # Convert ObjectId to string
    user["_id"] = str(user["_id"])
    del user["passwordHash"]
    
    return user


async def generate_tokens(user: Dict[str, Any]) -> Dict[str, str]:
    """Generate access and refresh tokens for user"""
    token_data = {
        "sub": user["_id"],
        "email": user["email"],
        "role": user["role"]
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


async def refresh_access_token(refresh_token: str) -> str:
    """Generate new access token from refresh token"""
    try:
        payload = decode_token(refresh_token)
        verify_token_type(payload, "refresh")
        
        # Verify user still exists
        users_collection = get_users_collection()
        user_id = payload.get("sub")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new access token
        token_data = {
            "sub": str(user["_id"]),
            "email": user["email"],
            "role": user["role"]
        }
        
        access_token = create_access_token(token_data)
        return access_token
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


async def get_user_by_id(user_id: str) -> Dict[str, Any]:
    """Get user by ID"""
    users_collection = get_users_collection()
    
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["_id"] = str(user["_id"])
    if "passwordHash" in user:
        del user["passwordHash"]
    
    return user


async def update_user(user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update user profile (patient only)"""
    users_collection = get_users_collection()
    
    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    # Build update document
    update_doc = {}
    patient_profile_updates = {}
    
    for key, value in update_data.items():
        if key in ["age", "gender", "notes"]:
            patient_profile_updates[f"patientProfile.{key}"] = value
        elif key in ["name", "phone"]:
            update_doc[key] = value
    
    # Merge updates
    update_doc.update(patient_profile_updates)
    
    # Check if phone is being updated and is unique
    if "phone" in update_doc:
        existing_phone = await users_collection.find_one({
            "phone": update_doc["phone"],
            "_id": {"$ne": ObjectId(user_id)}
        })
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )
    
    # Update user
    result = await users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_doc},
        return_document=ReturnDocument.AFTER
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result["_id"] = str(result["_id"])
    if "passwordHash" in result:
        del result["passwordHash"]
    
    return result
