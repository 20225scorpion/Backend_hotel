from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.sql import func

from database import Base


class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(Text, nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_registro = Column(TIMESTAMP, server_default=func.now())
    categoria = Column(String(50), nullable=False, default='general')
