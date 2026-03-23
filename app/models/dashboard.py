from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime
class Dashboard(BaseModel):
    lastId: str=None
    customer: str=None
    date: Optional[Union[datetime, str]] = None