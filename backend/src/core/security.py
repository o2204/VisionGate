from typing import Annotated

from fastapi import Depends, HTTPException, Request, status 
from fastapi.security import OAuth2PasswordBearer, HTTPBearer

from src.core.utils.utils import decode_access_token 


oauth2_user_scheme = OAuth2PasswordBearer(
    tokenUrl="/user/login"
)

oauth2_admin_scheme = OAuth2PasswordBearer(
    tokenUrl="/admin/login",
    scheme_name="AdminAuth"
)


class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth_credentials =  await super().__call__(request)

        if not auth_credentials:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )
        
        token = auth_credentials.credentials
        token_data = decode_access_token(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized!"
            )
        
        return token_data 


access_token_bearer = AccessTokenBearer()

Annotated[dict, Depends(access_token_bearer)]