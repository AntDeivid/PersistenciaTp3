from datetime import datetime
from typing import Optional

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