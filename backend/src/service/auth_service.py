from passlib.context import CryptContext
from fastapi import HTTPException

import pickle
import face_recognition

from src.models.admin_model import AdminModel
from src.core.utils.utils import generate_access_token


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class AuthService:

    def hash_password(self, password: str) -> str:
        return password_context.hash(password)

    def verify_password(
        self,
        password: str,
        hashed: str
    ) -> bool:
        return password_context.verify(
            password,
            hashed
        )

    def generate_face_embedding(
        self,
        image_path: str
    ) -> str:

        # Load image
        image = face_recognition.load_image_file(
            image_path
        )

        # Extract encodings
        encodings = face_recognition.face_encodings(
            image
        )

        # Check if face exists
        if not encodings:
            raise HTTPException(
                status_code=400,
                detail="No face detected in image"
            )

        # First face embedding
        embedding = encodings[0]

        # Serialize embedding
        serialized = pickle.dumps(
            embedding
        ).hex()

        return serialized

    def validate_credentials(
        self,
        entity,
        password: str
    ):

        if not entity:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not self.verify_password(
            password,
            entity.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if (
            hasattr(entity, "email_verified")
            and not entity.email_verified
        ):
            raise HTTPException(
                status_code=401,
                detail="Email not verified"
            )

    def generate_token(
        self,
        entity
    ) -> str:

        role = (
            "admin"
            if isinstance(entity, AdminModel)
            else "user"
        )

        return generate_access_token(
            data={
                "id": str(entity.id),
                "name": getattr(
                    entity,
                    "name",
                    "user"
                ),
                "role": role
            }
        )