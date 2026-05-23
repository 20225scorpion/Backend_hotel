from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models.huesped_model import Huesped
from models.user_model import Usuario
from models.auditoria_model import AuditoriaLog
from models.registro_eliminado_model import RegistroEliminado
from schemas.huesped_schema import HuespedCreate, HuespedUpdate, HuespedOut

router = APIRouter(prefix="/huespedes", tags=["huespedes"])


@router.get("/", response_model=List[HuespedOut])
def listar_huespedes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(Huesped).all()


@router.get("/cedula/{cedula}", response_model=HuespedOut)
def obtener_por_cedula(
    cedula: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    huesped = db.query(Huesped).filter(Huesped.cedula == cedula).first()
    if not huesped:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")
    return huesped


@router.get("/{id}", response_model=HuespedOut)
def obtener_huesped(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    huesped = db.query(Huesped).filter(Huesped.id == id).first()
    if not huesped:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")
    return huesped


@router.post("/", response_model=HuespedOut)
def crear_huesped(
    data: HuespedCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "recepcionista"):
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar huéspedes")

    existente = db.query(Huesped).filter(Huesped.cedula == data.cedula).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un huésped con esa cédula")

    huesped = Huesped(**data.model_dump())
    db.add(huesped)
    db.flush()
    audit = AuditoriaLog(
        usuario_id=current_user.id,
        accion="crear_huesped",
        descripcion=f"Registró huésped {huesped.nombre} (CC {huesped.cedula})"
    )
    db.add(audit)
    db.commit()
    db.refresh(huesped)
    return huesped


@router.put("/{id}", response_model=HuespedOut)
def actualizar_huesped(
    id: int,
    data: HuespedUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "recepcionista"):
        raise HTTPException(status_code=403, detail="No tienes permisos para actualizar huéspedes")

    huesped = db.query(Huesped).filter(Huesped.id == id).first()
    if not huesped:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")

    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(huesped, campo, valor)

    db.commit()
    db.refresh(huesped)
    return huesped


@router.delete("/{id}")
def eliminar_huesped(
    id: int,
    motivo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede eliminar huéspedes")

    huesped = db.query(Huesped).filter(Huesped.id == id).first()
    if not huesped:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")

    log = RegistroEliminado(
        tabla_afectada="huespedes",
        registro_id=id,
        motivo=motivo,
        usuario_id=current_user.id
    )
    db.add(log)
    audit = AuditoriaLog(
        usuario_id=current_user.id,
        accion="eliminacion",
        descripcion=f"Eliminó huésped {huesped.nombre} (ID {id}): {motivo}"
    )
    db.add(audit)
    db.delete(huesped)
    db.commit()
    return {"mensaje": f"Huésped {huesped.nombre} eliminado"}
