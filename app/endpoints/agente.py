from fastapi import APIRouter, HTTPException, status, Depends
from google.api_core import exceptions
from core.dependencies import getEmailService
router = APIRouter(
    prefix="/api",
    tags=["Gemini endpoints"]
)
@router.post("/question")
async def input_to_gemini(input: str, email_service=Depends(getEmailService)):
    try:
        response = await email_service.analyzeEmails(input=input)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="Gemini didn't generate an answer"
            )
        return {"data":response}
    except exceptions.Unauthenticated:
        raise HTTPException(status_code=401, detail="Incorrect Gemini API Key")
    except exceptions.ResourceExhausted:
        raise HTTPException(status_code=409, detail="Your Gemini plan has run out of tokens")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")