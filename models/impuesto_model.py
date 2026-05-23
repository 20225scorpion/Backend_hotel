from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.sql import func

from database import Base


class Impuesto(Base):
    __tablename__ = "impuestos"

    id = Column(Integer, primary_key=True, index=True)
    iva_generado = Column(Numeric(10, 2), nullable=False)
    iva_descontable = Column(Numeric(10, 2), nullable=False)
    total_pagar = Column(Numeric(10, 2), nullable=False)
    fecha_calculo = Column(TIMESTAMP, server_default=func.now())
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
