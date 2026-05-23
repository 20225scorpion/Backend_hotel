from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models.habitacion_model import Habitacion
from models.huesped_model import Huesped
from models.hospedaje_model import Hospedaje
from models.ingreso_model import Ingreso
from models.user_model import Usuario
from models.auditoria_model import AuditoriaLog
from schemas.hospedaje_schema import HospedajeCreate, HospedajeOut

router = APIRouter(prefix="/hospedajes", tags=["hospedajes"])


@router.get("/", response_model=List[HospedajeOut])
def listar_hospedajes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(Hospedaje).order_by(Hospedaje.created_at.desc()).all()


@router.post("/", response_model=HospedajeOut)
def check_in(
    data: HospedajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "recepcionista"):
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar hospedajes")

    habitacion = db.query(Habitacion).filter(Habitacion.id == data.habitacion_id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    if habitacion.estado != "libre":
        raise HTTPException(
            status_code=400,
            detail=f"La habitación no está disponible (estado actual: {habitacion.estado})"
        )

    huesped_1 = db.query(Huesped).filter(Huesped.id == data.huesped_1_id).first()
    if not huesped_1:
        raise HTTPException(status_code=404, detail="Huésped 1 no encontrado")

    if data.huesped_2_id:
        huesped_2 = db.query(Huesped).filter(Huesped.id == data.huesped_2_id).first()
        if not huesped_2:
            raise HTTPException(status_code=404, detail="Huésped 2 no encontrado")

    hospedaje = Hospedaje(**data.model_dump(), usuario_id=current_user.id)
    db.add(hospedaje)
    db.flush()

    ingreso = Ingreso(
        hospedaje_id=hospedaje.id,
        monto=data.total_pagado,
        descripcion=f"Hospedaje habitación {habitacion.numero}",
        tipo="hospedaje",
        usuario_id=current_user.id
    )
    db.add(ingreso)

    habitacion.estado = "ocupada"

    audit = AuditoriaLog(
        usuario_id=current_user.id,
        accion="checkin",
        descripcion=f"Check-in hab. {habitacion.numero}, huésped {huesped_1.nombre}, ${data.total_pagado}"
    )
    db.add(audit)

    db.commit()
    db.refresh(hospedaje)
    return hospedaje


@router.put("/{id}/checkout", response_model=HospedajeOut)
def check_out(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "recepcionista"):
        raise HTTPException(status_code=403, detail="No tienes permisos para hacer checkout")

    hospedaje = db.query(Hospedaje).filter(Hospedaje.id == id).first()
    if not hospedaje:
        raise HTTPException(status_code=404, detail="Hospedaje no encontrado")

    habitacion = db.query(Habitacion).filter(Habitacion.id == hospedaje.habitacion_id).first()
    if habitacion:
        habitacion.estado = "limpieza"

    log = AuditoriaLog(
        usuario_id=current_user.id,
        accion="checkout",
        descripcion=f"Checkout hospedaje #{id}, habitación {habitacion.numero if habitacion else id}"
    )
    db.add(log)

    db.commit()
    db.refresh(hospedaje)
    return hospedaje
