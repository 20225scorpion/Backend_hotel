from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP
from sqlalchemy.sql import func

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(100), nullable=False)

    correo = Column(String(120), unique=True, nullable=False)

    contrasena = Column(String(255), nullable=False)

    rol = Column(
        Enum(
            'admin',
            'recepcionista',
            'contador',
            'aseador_principal',
            'auditor'
        ),
        nullable=False
    )

    activo = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )