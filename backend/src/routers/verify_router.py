from fastapi import APIRouter, UploadFile, File, HTTPException, status
import cv2
import numpy as np

from src.service.recognition_service import recognize_face

verify_router = APIRouter()

@verify_router.post("/verify-face")
async def verify_face(file: UploadFile = File(...)):

    result = await recognize_face(file)

    if not result["authorized"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )

    return result 