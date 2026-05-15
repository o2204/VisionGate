from fastapi import APIRouter, UploadFile, File

from src.core.container import FaceServiceDep
from src.core.utils.utils import generate_access_token


face_router = APIRouter(
    prefix="/face",
    tags=["Face Recognition"]
)


@face_router.post("/login")
async def face_login(
    file: UploadFile = File(...),
    service: FaceServiceDep = None
):

    user = await service.recognize_face(file)

    token = generate_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "message": "Face recognized",
        "access_token": token
    }