from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.auth_bearer import verify_token
from database import SessionLocal, engine, Base
from models.user_model import Usuario
from models.habitacion_model import Habitacion
from models.huesped_model import Huesped
from models.hospedaje_model import Hospedaje
from models.ingreso_model import Ingreso
from models.gasto_model import Gasto
from models.impuesto_model import Impuesto
from models.auditoria_model import AuditoriaLog
from models.registro_eliminado_model import RegistroEliminado
from auth.role_checker import require_role

from schemas.user_schema import (
    UsuarioCreate,
    UsuarioLogin
)

from auth.auth_handler import (
    hash_password,
    verify_password,
    create_access_token
)

from routers import habitaciones, huespedes, ingresos, gastos, hospedajes, reportes, auditoria


app = FastAPI(title="Hotel Asturias API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(habitaciones.router)
app.include_router(huespedes.router)
app.include_router(ingresos.router)
app.include_router(gastos.router)
app.include_router(hospedajes.router)
app.include_router(reportes.router)
app.include_router(auditoria.router)



# ==========================================
# CONEXIÓN DB
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



# ==========================================
# INICIO
# ==========================================

@app.get("/")
def inicio():

    return {
        "mensaje": "Backend funcionando correctamente"
    }



# ==========================================
# REGISTRO USUARIO
# ==========================================

@app.post("/register")
def register_user(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):

    usuario_existente = db.query(Usuario).filter(
        Usuario.correo == usuario.correo
    ).first()

    if usuario_existente:

        raise HTTPException(
            status_code=400,
            detail="Correo ya registrado"
        )

    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        contrasena=hash_password(usuario.contrasena),
        rol=usuario.rol
    )

    db.add(nuevo_usuario)

    db.commit()

    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario registrado correctamente"
    }



# ==========================================
# LOGIN JWT
# ==========================================

@app.post("/login")
def login(
    usuario: UsuarioLogin,
    db: Session = Depends(get_db)
):

    usuario_db = db.query(Usuario).filter(
        Usuario.correo == usuario.correo
    ).first()

    if not usuario_db:

        raise HTTPException(
            status_code=401,
            detail="Correo incorrecto"
        )

    if not verify_password(
        usuario.contrasena,
        usuario_db.contrasena
    ):

        raise HTTPException(
            status_code=401,
            detail="Contraseña incorrecta"
        )

    token = create_access_token({
        "sub": usuario_db.correo,
        "rol": usuario_db.rol
    })

    log = AuditoriaLog(
        usuario_id=usuario_db.id,
        accion="login",
        descripcion=f"Inicio de sesión: {usuario_db.correo}"
    )
    db.add(log)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario_db.rol
    }

class PerfilUpdate(BaseModel):
    nombre: str


class PasswordChange(BaseModel):
    password_actual: str
    password_nuevo: str


@app.get("/perfil")
def perfil(
    user_data: dict = Depends(verify_token)
):
    return {
        "mensaje": "Ruta protegida",
        "usuario": user_data
    }


@app.put("/perfil")
def actualizar_perfil(
    data: PerfilUpdate,
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    usuario = db.query(Usuario).filter(Usuario.correo == user_data["sub"]).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.nombre = data.nombre
    db.commit()
    db.refresh(usuario)
    return {"mensaje": "Perfil actualizado", "nombre": usuario.nombre}


@app.put("/perfil/password")
def cambiar_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    usuario = db.query(Usuario).filter(Usuario.correo == user_data["sub"]).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not verify_password(data.password_actual, usuario.contrasena):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    usuario.contrasena = hash_password(data.password_nuevo)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente"}

@app.get("/admin")
def admin_panel(
    user_data: dict = Depends(
        require_role(["admin"])
    )
):

    return {
        "mensaje": "Bienvenido administrador",
        "usuario": user_data
    }



# ==========================================
# ASEADOR PRINCIPAL
# ==========================================

@app.get("/aseador")
def aseador_panel(
    user_data: dict = Depends(
        require_role(["aseador_principal"])
    )
):

    return {
        "mensaje": "Bienvenido aseador principal",
        "usuario": user_data
    }
