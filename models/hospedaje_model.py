from sqlalchemy import Column, Integer, String, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.sql import func

from database import Base


class Hospedaje(Base):
    __tablename__ = "hospedajes"

    id = Column(Integer, primary_key=True, index=True)
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"), nullable=False)
    huesped_1_id = Column(Integer, ForeignKey("huespedes.id"), nullable=False)
    huesped_2_id = Column(Integer, ForeignKey("huespedes.id"))
    cantidad_personas = Column(Integer, nullable=False)
    fecha_entrada = Column(DateTime, nullable=False)
    fecha_salida = Column(DateTime, nullable=False)
    total_pagado = Column(Numeric(10, 2), nullable=False)
    metodo_pago = Column(String(50), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
