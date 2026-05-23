from pydantic import BaseModel


class UsuarioCreate(BaseModel):

    nombre: str

    correo: str

    contrasena: str

    rol: str


class UsuarioLogin(BaseModel):

    correo: str

    contrasena: str