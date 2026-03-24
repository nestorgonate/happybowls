from fastapi import Cookie, HTTPException, status, Depends, Response
from typing import Optional
import os

# Esta es tu "llave de paso"
async def cookie_validator(ACCESSTOKEN: Optional[str] = Cookie(None)):
    if ACCESSTOKEN != f"{os.getenv("JWT_TOKEN")}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes una cookie de sesión válida"
        )
    return ACCESSTOKEN