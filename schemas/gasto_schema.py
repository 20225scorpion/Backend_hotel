from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GastoCreate(BaseModel):
    descripcion: str
    monto: float
    categoria: Optional[str] = 'general'


class GastoUpdate(BaseModel):
    descripcion: Optional[str] = None
    monto: Optional[float] = None
    categoria: Optional[str] = None


class GastoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    descripcion: str
    monto: float
    categoria: str
    usuario_id: int
    fecha_registro: Optional[datetime]
