from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.app.models.pagamento import Pagamento


class PagamentoDTO(BaseModel):
    id: Optional[str] = None
    valor: float
    forma_pagamento: str
    vencimento: datetime
    pago: bool

    @classmethod
    def from_model(cls, pagamento: Pagamento):
        return cls(
            id=str(pagamento.id),
            valor=pagamento.valor,
            forma_pagamento=pagamento.forma_pagamento,
            vencimento=pagamento.vencimento,
            pago=pagamento.pago
        )
        
    def to_model(self) -> Pagamento:
        return Pagamento(
            id=self.id,
            valor=self.valor,
            forma_pagamento=self.forma_pagamento,
            vencimento=self.vencimento,
            pago=self.pago
        )