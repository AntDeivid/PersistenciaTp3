from typing import Optional

from pydantic import BaseModel

from src.app.models.usuario import Usuario


class UsuarioDTO(BaseModel):
    id: Optional[str] = None
    nome: str
    email: str
    celular: Optional[str] = None
    cpf: str

    @classmethod
    def from_model(cls, usuario: Usuario):
        return cls(
            id=str(usuario.id),
            nome=usuario.nome,
            email=usuario.email,
            celular=usuario.celular,
            cpf=usuario.cpf
        )
    
    def to_model(self) -> Usuario:
        return Usuario(
            id=self.id,
            nome=self.nome,
            email=self.email,
            celular=self.celular,
            cpf=self.cpf
        )