from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from app.schemas.user import UserResponse, UpdateUserRequest
from app.core.security import get_current_user, get_current_patient
from app.services.user_service import update_user
from app.core.db import get_users_collection
from typing import Dict, Any, List
import os
import shutil
from pathlib import Path
from app.config import settings

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile
    
    - Returns authenticated user's profile data
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UpdateUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_patient)
):
    """
    Update current patient profile
    
    - Only patients can update their profile
    - Doctors cannot update via this endpoint
    """
    updated_user = await update_user(
        user_id=current_user["_id"],
        update_data=update_data.model_dump(exclude_unset=True)
    )
    
    return updated_user


@router.post("/me/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload profile photo
    
    - Accepts image file
    - Saves to uploads directory
    - Updates user's photoUrl
    """
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    user_id = current_user["_id"]
    filename = f"{user_id}_{file.filename}"
    file_path = upload_dir / filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Update user's photoUrl in database
    from app.core.db import get_users_collection
    from bson import ObjectId
    
    users_collection = get_users_collection()
    photo_url = f"{settings.BACKEND_URL}/uploads/{filename}"
    
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"photoUrl": photo_url}}
    )
    
    return {
        "message": "Photo uploaded successfully",
        "photoUrl": photo_url
    }


@router.get("/doctors", response_model=List[UserResponse])
async def get_all_doctors():
    """
    Get list of all doctors
    
    - Returns all users with role='doctor'
    - Public endpoint for appointment booking
    """
    users_collection = get_users_collection()
    
    doctors = await users_collection.find({"role": "doctor"}).to_list(length=None)
    
    # Convert ObjectId to string
    for doctor in doctors:
        doctor["_id"] = str(doctor["_id"])
    
    return doctors
