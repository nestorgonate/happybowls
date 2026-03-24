from fastapi import APIRouter, HTTPException, Depends
from core.dependencies import getEmailService
from models.dashboard import Dashboard
import logging
from datetime import datetime
from models.email import UpdateEmail
from middleware.validar_cookies import cookie_validator
router = APIRouter(
    prefix="/api",
    tags=["Manage email data"],
    dependencies=[Depends(cookie_validator)]
)
logger = logging.getLogger("email_organizer")
@router.post("/emails")
async def getEmails(dashboard: Dashboard, email_service=Depends(getEmailService)):
    try:
        date = None
        if dashboard.date:
            # Intentamos parsear solo fecha o fecha con hora
            try:
                if len(dashboard.date) <= 10: # Caso "2023-10-25"
                    date = datetime.strptime(dashboard.date, "%Y-%m-%d")
                else: # Caso "2023-10-25 14:30:00"
                    date = datetime.strptime(dashboard.date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DD HH:MM:SS")
        emails = await email_service.getEmails(last_id=dashboard.lastId, customer=dashboard.customer, date=date)
        if not emails:
            return{"data":[]}
        #Obtener lastId
        lastId: str
        lastId = emails[-1]["idMongo"]
        return{
            "data":emails,
            "last_id":lastId
        }
    except Exception as error:
        logger.error(f"Can not get emails: {error}")
        raise HTTPException(status_code=500, detail="The server can not process your request")

@router.patch("/emails/{email_id}")
async def updateEmails(email_id: str, data: UpdateEmail, email_service = Depends(getEmailService)):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    result = await email_service.updateEmail(email_id, update_data)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if result.modified_count == 0:
        return {"message": "No updated since data is the same"}
    return {"data": "Update completed successfully"}

@router.get("/check")
async def check():
    return {"data":"You are log in"}