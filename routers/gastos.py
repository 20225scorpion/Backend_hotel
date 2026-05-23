from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models.gasto_model import Gasto
from models.user_model import Usuario
from models.auditoria_model import AuditoriaLog
from models.registro_eliminado_model import RegistroEliminado
from schemas.gasto_schema import GastoCreate, GastoOut, GastoUpdate

router = APIRouter(prefix="/gastos", tags=["gastos"])


@router.get("/", response_model=List[GastoOut])
def listar_gastos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "contador"):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver gastos")
    return db.query(Gasto).order_by(Gasto.fecha_registro.desc()).all()


@router.post("/", response_model=GastoOut)
def crear_gasto(
    data: GastoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede registrar gastos")

    gasto = Gasto(**data.model_dump(), usuario_id=current_user.id)
    db.add(gasto)
    db.flush()
    audit = AuditoriaLog(
        usuario_id=current_user.id,
        accion="crear_gasto",
        descripcion=f"Registró gasto ${gasto.monto} - {gasto.descripcion}"
    )
    db.add(audit)
    db.commit()
    db.refresh(gasto)
    return gasto


@router.put("/{id}", response_model=GastoOut)
def actualizar_gasto(
    id: int,
    data: GastoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede editar gastos")

    gasto = db.query(Gasto).filter(Gasto.id == id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(gasto, field, value)

    db.commit()
    db.refresh(gasto)
    return gasto


@router.delete("/{id}")
def eliminar_gasto(
    id: int,
    motivo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede eliminar gastos")

    gasto = db.query(Gasto).filter(Gasto.id == id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    log = RegistroEliminado(
        tabla_afectada="gastos",
        registro_id=id,
        motivo=motivo,
        usuario_id=current_user.id
    )
    db.add(log)
    audit = AuditoriaLog(
        usuario_id=current_user.id,
        accion="eliminacion",
        descripcion=f"Eliminó gasto #{id}: {motivo}"
    )
    db.add(audit)
    db.delete(gasto)
    db.commit()
    return {"mensaje": "Gasto eliminado"}
