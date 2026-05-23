from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from database import Base


class RegistroEliminado(Base):
    __tablename__ = "registros_eliminados"

    id = Column(Integer, primary_key=True, index=True)
    tabla_afectada = Column(String(100), nullable=False)
    registro_id = Column(Integer, nullable=False)
    motivo = Column(Text, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_eliminacion = Column(TIMESTAMP, server_default=func.now())
