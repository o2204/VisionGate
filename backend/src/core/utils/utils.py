from datetime import datetime, timedelta, timezone
from uuid import uuid4  ## Added for generating unique token identifiers
import jwt

from fastapi import HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer 

from src.core.config import settings

_serializer = URLSafeTimedSerializer(settings.JWT_SECRET)


def generate_access_token(
        data: dict,
        expiry: timedelta = timedelta(hours=24),
) -> str:
    
    payload = {
        **data,
        "jti": str(uuid4()),
        "exp": datetime.now(timezone.utc) + expiry,
    }

    token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        ) 
    return token

def decode_access_token(token: str) -> dict:
    try: 
        return jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        ) 
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token"
        ) 
    
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )  
    

def generate_url_safe_token(data: dict, salt: str | None = None) -> str:
    return _serializer.dumps(data, salt=salt)

def decode_url_safe_token(token: str, salt: str | None = None, expiry: timedelta | None = None) -> dict | None:
    try:
        return _serializer.loads(
            token,
            salt=salt,
            max_age=int(expiry.total_seconds()) if expiry else None,
        )
    except (BadSignature, SignatureExpired):
        return None 