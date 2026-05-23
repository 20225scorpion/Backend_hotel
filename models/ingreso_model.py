from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.sql import func

from database import Base


class Ingreso(Base):
    __tablename__ = "ingresos"

    id = Column(Integer, primary_key=True, index=True)
    hospedaje_id = Column(Integer, ForeignKey("hospedajes.id"))
    monto = Column(Numeric(10, 2), nullable=False)
    descripcion = Column(Text)
    tipo = Column(String(50), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_registro = Column(TIMESTAMP, server_default=func.now(), index=True)
