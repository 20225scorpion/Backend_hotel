from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HuespedCreate(BaseModel):
    nombre: str
    cedula: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    placa: Optional[str] = None


class HuespedUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    placa: Optional[str] = None


class HuespedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    cedula: str
    telefono: Optional[str]
    correo: Optional[str]
    placa: Optional[str]
    created_at: Optional[datetime]
