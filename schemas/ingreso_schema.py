from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IngresoCreate(BaseModel):
    hospedaje_id: Optional[int] = None
    monto: float
    descripcion: Optional[str] = None
    tipo: str


class IngresoUpdate(BaseModel):
    monto: Optional[float] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None


class IngresoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hospedaje_id: Optional[int]
    monto: float
    descripcion: Optional[str]
    tipo: str
    usuario_id: int
    fecha_registro: Optional[datetime]
