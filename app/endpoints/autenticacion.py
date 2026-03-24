from fastapi import APIRouter, HTTPException, status, Response
import logging
from models.autenticacion import Autenticacion
import os
router = APIRouter(
    prefix="/api",
    tags=["Sistema de login"]
)
logger = logging.getLogger("email_organizer")
@router.post("/login")
async def login(request: Autenticacion, response: Response):
    password = os.getenv("PASSWORD")
    if password != request.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The password is incorrect")
    response.set_cookie(key="ACCESSTOKEN", value=f"{os.getenv("JWT_TOKEN")}", httponly=True, samesite="lax")
    return {"data":"Log in successful"}