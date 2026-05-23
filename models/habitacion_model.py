from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, Text
from sqlalchemy.types import Numeric
from sqlalchemy.sql import func

from database import Base


class Habitacion(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, nullable=False)
    estado = Column(
        Enum('libre', 'ocupada', 'limpieza', 'mantenimiento'),
        default='libre'
    )
    precio_1_persona = Column(Numeric(10, 2), nullable=False)
    precio_2_personas = Column(Numeric(10, 2), nullable=False)
    observaciones = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
