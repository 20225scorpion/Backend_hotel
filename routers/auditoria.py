from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models.auditoria_model import AuditoriaLog
from models.registro_eliminado_model import RegistroEliminado
from models.user_model import Usuario
from auth.role_checker import require_role
from auth.auth_handler import hash_password

router = APIRouter()


class PasswordReset(BaseModel):
    nueva_password: str


@router.get("/auditoria")
def listar_auditoria(
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_role(["auditor"]))
):
    results = (
        db.query(AuditoriaLog, Usuario.nombre, Usuario.correo)
        .join(Usuario, AuditoriaLog.usuario_id == Usuario.id)
        .order_by(AuditoriaLog.fecha.desc())
        .all()
    )
    return [
        {
            "id": log.id,
            "usuario_id": log.usuario_id,
            "usuario_nombre": nombre,
            "usuario_correo": correo,
            "accion": log.accion,
            "descripcion": log.descripcion,
            "fecha": log.fecha
        }
        for log, nombre, correo in results
    ]


@router.get("/registros-eliminados")
def listar_registros_eliminados(
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_role(["auditor"]))
):
    results = (
        db.query(RegistroEliminado, Usuario.nombre, Usuario.correo)
        .join(Usuario, RegistroEliminado.usuario_id == Usuario.id)
        .order_by(RegistroEliminado.fecha_eliminacion.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "tabla_afectada": r.tabla_afectada,
            "registro_id": r.registro_id,
            "motivo": r.motivo,
            "usuario_id": r.usuario_id,
            "usuario_nombre": nombre,
            "usuario_correo": correo,
            "fecha_eliminacion": r.fecha_eliminacion
        }
        for r, nombre, correo in results
    ]


@router.get("/usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    user_data: dict = Depends(require_role(["auditor"]))
):
    usuarios = db.query(Usuario).order_by(Usuario.id).all()
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "correo": u.correo,
            "rol": u.rol,
            "activo": bool(u.activo),
            "created_at": str(u.created_at) if u.created_at else None
        }
        for u in usuarios
    ]


@router.put("/usuarios/{id}/activar")
def toggle_activar_usuario(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "auditor":
        raise HTTPException(status_code=403, detail="No tienes permisos")

    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = not usuario.activo

    log = AuditoriaLog(
        usuario_id=current_user.id,
        accion="toggle_usuario",
        descripcion=f"{'Activó' if usuario.activo else 'Desactivó'} al usuario {usuario.correo} (ID {id})"
    )
    db.add(log)
    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": f"Usuario {'activado' if usuario.activo else 'desactivado'} correctamente",
        "id": usuario.id,
        "activo": bool(usuario.activo)
    }


@router.put("/usuarios/{id}/password")
def restablecer_password_usuario(
    id: int,
    data: PasswordReset,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "auditor":
        raise HTTPException(status_code=403, detail="No tienes permisos")

    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.contrasena = hash_password(data.nueva_password)

    log = AuditoriaLog(
        usuario_id=current_user.id,
        accion="restablecer_password",
        descripcion=f"Restableció contraseña de {usuario.correo} (ID {id})"
    )
    db.add(log)
    db.commit()

    return {"mensaje": f"Contraseña de {usuario.nombre} restablecida correctamente"}
