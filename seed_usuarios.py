"""
Script de seed: inserta 4 usuarios con contraseñas hasheadas con bcrypt.
Ejecutar desde la carpeta backend-hotel-finanzas:
    python seed_usuarios.py
"""

import sys
import os

# Permite importar los módulos del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
from models.user_model import Usuario
from auth.auth_handler import hash_password

USUARIOS = [
    {
        "nombre":    "Administrador",
        "correo":    "admin@hotel.com",
        "password":  "admin123",
        "rol":       "admin",
    },
    {
        "nombre":    "Recepcionista",
        "correo":    "recepcion@hotel.com",
        "password":  "recepcion123",
        "rol":       "recepcionista",
    },
    {
        "nombre":    "Contador",
        "correo":    "contador@hotel.com",
        "password":  "contador123",
        "rol":       "contador",
    },
    {
        "nombre":    "Aseador",
        "correo":    "aseador@hotel.com",
        "password":  "aseador123",
        "rol":       "aseador_principal",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        insertados = 0
        omitidos   = 0

        for u in USUARIOS:
            existe = db.query(Usuario).filter(Usuario.correo == u["correo"]).first()
            if existe:
                print(f"  [omitido]  {u['correo']} ya existe")
                omitidos += 1
                continue

            nuevo = Usuario(
                nombre=u["nombre"],
                correo=u["correo"],
                contrasena=hash_password(u["password"]),
                rol=u["rol"],
            )
            db.add(nuevo)
            insertados += 1
            print(f"  [OK]       {u['correo']} ({u['rol']})")

        db.commit()
        print(f"\nResultado: {insertados} insertado(s), {omitidos} omitido(s).\n")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    finally:
        db.close()


def mostrar_usuarios():
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).order_by(Usuario.id).all()
        sep = "-" * 80
        print(sep)
        print(f"{'ID':<5} {'NOMBRE':<20} {'CORREO':<30} {'ROL':<20} {'ACTIVO'}")
        print(sep)
        for u in usuarios:
            print(
                f"{u.id:<5} {u.nombre:<20} {u.correo:<30} {u.rol:<20} {u.activo}"
            )
        print(sep)
        print(f"Total: {len(usuarios)} usuario(s)\n")
    finally:
        db.close()


if __name__ == "__main__":
    print("\n=== Insertando usuarios ===\n")
    seed()
    print("=== SELECT * FROM usuarios ===\n")
    mostrar_usuarios()
