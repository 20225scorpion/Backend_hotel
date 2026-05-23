from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models.habitacion_model import Habitacion
from models.auditoria_model import AuditoriaLog
from models.registro_eliminado_model import RegistroEliminado
from models.user_model import Usuario
from schemas.habitacion_schema import HabitacionCreate, HabitacionUpdate, HabitacionOut

router = APIRouter(prefix="/habitaciones", tags=["habitaciones"])

ESTADOS_VALIDOS = {'libre', 'ocupada', 'limpieza', 'mantenimiento'}


@router.get("/", response_model=List[HabitacionOut])
def listar_habitaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(Habitacion).all()


@router.get("/{id}", response_model=HabitacionOut)
def obtener_habitacion(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    hab = db.query(Habitacion).filter(Habitacion.id == id).first()
    if not hab:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return hab


@router.post("/", response_model=HabitacionOut)
def crear_habitacion(
    data: HabitacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede crear habitaciones")

    existente = db.query(Habitacion).filter(Habitacion.numero == data.numero).first()
    if existente:
        raise HTTPException(status_code=400, detail="El número de habitación ya existe")

    hab = Habitacion(**data.model_dump())
    db.add(hab)
    db.commit()
    db.refresh(hab)
    return hab


@router.put("/{id}", response_model=HabitacionOut)
def actualizar_habitacion(
    id: int,
    data: HabitacionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "recepcionista", "aseador_principal"):
        raise HTTPException(status_code=403, detail="No tienes permisos para actualizar habitaciones")

    hab = db.query(Habitacion).filter(Habitacion.id == id).first()
    if not hab:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    # aseador_principal solo puede modificar el campo estado
    if current_user.rol == "aseador_principal":
        campos = data.model_dump(exclude_none=True)
        campos_no_permitidos = set(campos.keys()) - {"estado"}
        if campos_no_permitidos:
            raise HTTPException(status_code=403, detail="El aseador solo puede modificar el estado de la habitación")

    if data.estado and data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Opciones: {ESTADOS_VALIDOS}")

    old_estado = hab.estado
    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(hab, campo, valor)

    if data.estado and data.estado != old_estado:
        audit = AuditoriaLog(
            usuario_id=current_user.id,
            accion="cambio_estado",
            descripcion=f"Habitación #{hab.numero}: {old_estado} → {data.estado}"
        )
        db.add(audit)

    db.commit()
    db.refresh(hab)
    return hab


@router.delete("/{id}")
def eliminar_habitacion(
    id: int,
    motivo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede eliminar habitaciones")

    hab = db.query(Habitacion).filter(Habitacion.id == id).first()
    if not hab:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    reg = RegistroEliminado(
        tabla_afectada="habitaciones",
        registro_id=id,
        motivo=motivo,
        usuario_id=current_user.id
    )
    db.add(reg)
    audit = AuditoriaLog(
        usuario_id=current_user.id,
        accion="eliminacion",
        descripcion=f"Eliminó habitación #{hab.numero} (ID {id}): {motivo}"
    )
    db.add(audit)
    db.delete(hab)
    db.commit()
    return {"mensaje": f"Habitación {hab.numero} eliminada"}
