from pydantic import BaseModel

class Autenticacion(BaseModel):
    password: str