from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func

from database import Base


class Huesped(Base):
    __tablename__ = "huespedes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    cedula = Column(String(30), unique=True, nullable=False)
    telefono = Column(String(30))
    correo = Column(String(120))
    placa = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())
