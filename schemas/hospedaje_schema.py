from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HospedajeCreate(BaseModel):
    habitacion_id: int
    huesped_1_id: int
    huesped_2_id: Optional[int] = None
    cantidad_personas: int
    fecha_entrada: datetime
    fecha_salida: datetime
    total_pagado: float
    metodo_pago: str


class HospedajeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habitacion_id: int
    huesped_1_id: int
    huesped_2_id: Optional[int]
    cantidad_personas: int
    fecha_entrada: datetime
    fecha_salida: datetime
    total_pagado: float
    metodo_pago: str
    usuario_id: int
    created_at: Optional[datetime]
