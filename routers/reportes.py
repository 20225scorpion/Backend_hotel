from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from deps import get_db, get_current_user
from models.ingreso_model import Ingreso
from models.gasto_model import Gasto
from models.hospedaje_model import Hospedaje
from models.habitacion_model import Habitacion
from models.user_model import Usuario

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/")
def obtener_reporte(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ("admin", "contador"):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver los reportes")

    total_ingresos = db.query(func.sum(Ingreso.monto)).scalar() or 0
    total_gastos = db.query(func.sum(Gasto.monto)).scalar() or 0
    utilidad = float(total_ingresos) - float(total_gastos)

    total_hospedajes = db.query(func.count(Hospedaje.id)).scalar() or 0
    hospedajes_activos = (
        db.query(func.count(Hospedaje.id))
        .join(Habitacion, Hospedaje.habitacion_id == Habitacion.id)
        .filter(Habitacion.estado == "ocupada")
        .scalar() or 0
    )
    hospedajes_finalizados = total_hospedajes - hospedajes_activos

    habitaciones = {}
    for estado in ("libre", "ocupada", "limpieza", "mantenimiento"):
        habitaciones[estado] = (
            db.query(func.count(Habitacion.id))
            .filter(Habitacion.estado == estado)
            .scalar() or 0
        )

    return {
        "total_ingresos": float(total_ingresos),
        "total_gastos": float(total_gastos),
        "utilidad": utilidad,
        "hospedajes": {
            "activos": hospedajes_activos,
            "finalizados": hospedajes_finalizados,
            "total": total_hospedajes,
        },
        "habitaciones": habitaciones,
    }
