from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from auth.auth_bearer import verify_token
from models.user_model import Usuario


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
) -> Usuario:
    user = db.query(Usuario).filter(
        Usuario.correo == user_data["sub"]
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user
