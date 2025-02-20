from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel

from src.app.models.contrato import Contrato


class ContratoDTO(BaseModel):
    id: Optional[str] = None
    usuario_id: str
    veiculo_id: str
    pagamento_id: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime

    @classmethod
    def from_model(cls, contrato: Contrato):
        return cls(
            id=str(contrato.id),
            usuario_id=str(contrato.usuario_id),
            veiculo_id=str(contrato.veiculo_id),
            pagamento_id=str(contrato.pagamento_id) if contrato.pagamento_id else None,
            data_inicio=contrato.data_inicio,
            data_fim=contrato.data_fim
        )

    @classmethod
    def to_model(cls) -> Contrato:
        return Contrato(
            usuario_id=ObjectId(cls.usuario_id),
            veiculo_id=ObjectId(cls.veiculo_id),
            pagamento_id=ObjectId(cls.pagamento_id) if cls.pagamento_id else None,
            data_inicio=cls.data_inicio,
            data_fim=cls.data_fim
        )