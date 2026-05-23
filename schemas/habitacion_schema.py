from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HabitacionCreate(BaseModel):
    numero: str
    precio_1_persona: float
    precio_2_personas: float
    observaciones: Optional[str] = None


class HabitacionUpdate(BaseModel):
    estado: Optional[str] = None
    precio_1_persona: Optional[float] = None
    precio_2_personas: Optional[float] = None
    observaciones: Optional[str] = None


class HabitacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    estado: Optional[str]
    precio_1_persona: float
    precio_2_personas: float
    observaciones: Optional[str]
    created_at: Optional[datetime]
