from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from src.app.models.pagamento import Pagamento
from src.app.repositories.pagamento_repository import PagamentoRepository

pagamento_router = APIRouter()
pagamento_router.prefix = "/api/pagamentos"
pagamento_router.tags = ["Pagamentos"]


def get_pagamento_repository() -> PagamentoRepository:
    return PagamentoRepository()


@pagamento_router.post("/", response_model=Pagamento, status_code=201)
async def criar_pagamento(pagamento: Pagamento, pagamento_repo: PagamentoRepository = Depends(get_pagamento_repository)):
    try:
        pagamento_criado = await pagamento_repo.create(pagamento)
        if not pagamento_criado:
            raise HTTPException(status_code=500, detail="Erro ao criar pagamento")
        return pagamento_criado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@pagamento_router.get("/", response_model=List[Pagamento])
async def listar_pagamentos(
    data_inicial: Optional[datetime] = Query(None),
    data_final: Optional[datetime] = Query(None),
    pago: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    pagamento_repo: PagamentoRepository = Depends(get_pagamento_repository)
):
    return await pagamento_repo.get_all(data_inicial=data_inicial, data_final=data_final, pago=pago, page=skip // limit + 1, limit=limit)


@pagamento_router.get("/{pagamento_id}", response_model=Pagamento)
async def buscar_pagamento_por_id(
    pagamento_id: str,
    pagamento_repo: PagamentoRepository = Depends(get_pagamento_repository)
):
    pagamento = await pagamento_repo.get_by_id(pagamento_id)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return pagamento


@pagamento_router.put("/{pagamento_id}", response_model=Pagamento)
async def atualizar_pagamento(
    pagamento_id: str,
    pagamento: Pagamento,
    pagamento_repo: PagamentoRepository = Depends(get_pagamento_repository)
):
    pagamento_atualizado = await pagamento_repo.update(pagamento_id, pagamento)
    if not pagamento_atualizado:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado ou ID inválido")
    return pagamento_atualizado


@pagamento_router.delete("/{pagamento_id}", status_code=204)
async def deletar_pagamento(pagamento_id: str, pagamento_repo: PagamentoRepository = Depends(get_pagamento_repository)):
    if not await pagamento_repo.delete(pagamento_id):
        raise HTTPException(status_code=404, detail="Pagamento não encontrado ou ID inválido")
    return  

@pagamento_router.get("/pendentes/usuario")
async def obter_pagamentos_pendentes_por_usuario(
    usuario_id: Optional[str] = Query(None, description="Optional user ID to filter by"),
    pagamento_repo: "PagamentoRepository" = Depends(get_pagamento_repository)
):
    pagamentos = await pagamento_repo.get_pagamentos_pendentes_por_usuario(usuario_id=usuario_id)
    return pagamentos