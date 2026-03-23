from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime
class Email(BaseModel):
    idMongo: str = Field(alias="_id")
    id: str
    sender: str
    subject: str
    deadline: Optional[Union[datetime, str]]
    customer: str
    estimate: str
    pickup: str
    delivery: str
    vector_data: Optional[list[float]]
    date_email_sent: Optional[Union[datetime, str]]
    class Config:
        populated_by_name=True
        extra="ignore"

class UpdateEmail(BaseModel):
    _id: str = None
    id: str = None
    sender: str = None
    subject: str = None
    deadline: Optional[Union[datetime, str]] = None
    customer: str = None
    estimate: str = None
    pickup: str = None
    delivery: str = None
    vector_data: Optional[list[float]] = None
    date_email_sent: Optional[Union[datetime, str]] = None