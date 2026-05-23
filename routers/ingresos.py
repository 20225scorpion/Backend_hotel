from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models.ingreso_model import Ingreso
from models.user_model import Usuario
from models.auditoria_model import AuditoriaLog
from models.registro_eliminado_model import RegistroEliminado
from schemas.ingreso_schema import IngresoCreate, IngresoOut, IngresoUpdate

router = APIRouter(prefix="/ingresos", tags=["ingresos"])


@router.get("/", response_model=List[IngresoOut])
def listar_ingresos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "contador", "recepcionista"):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver ingresos")
    return db.query(Ingreso).order_by(Ingreso.fecha_registro.desc()).all()


@router.post("/", response_model=IngresoOut)
def crear_ingreso(
    data: IngresoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "recepcionista"):
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar ingresos")

    ingreso = Ingreso(**data.model_dump(), usuario_id=current_user.id)
    db.add(ingreso)
    db.flush()
    audit = AuditoriaLog(
        usuario_id=current_user.id,
        accion="crear_ingreso",
        descripcion=f"Registró ingreso ${ingreso.monto} tipo {ingreso.tipo}"
    )
    db.add(audit)
    db.commit()
    db.refresh(ingreso)
    return ingreso


@router.put("/{id}", response_model=IngresoOut)
def actualizar_ingreso(
    id: int,
    data: IngresoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede editar ingresos")

    ingreso = db.query(Ingreso).filter(Ingreso.id == id).first()
    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(ingreso, field, value)

    db.commit()
    db.refresh(ingreso)
    return ingreso


@router.delete("/{id}")
def eliminar_ingreso(
    id: int,
    motivo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede eliminar ingresos")

    ingreso = db.query(Ingreso).filter(Ingreso.id == id).first()
    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    log = RegistroEliminado(
        tabla_afectada="ingresos",
        registro_id=id,
        motivo=motivo,
        usuario_id=current_user.id
    )
    db.add(log)
    audit = AuditoriaLog(
        usuario_id=current_user.id,
        accion="eliminacion",
        descripcion=f"Eliminó ingreso #{id}: {motivo}"
    )
    db.add(audit)
    db.delete(ingreso)
    db.commit()
    return {"mensaje": "Ingreso eliminado"}
