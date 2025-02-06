from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from src.app.models.manutencao import Manutencao
from src.app.repositories.manutencao_repository import ManutencaoRepository

manutencao_router = APIRouter()
manutencao_router.prefix = "/api/manutencoes"
manutencao_router.tags = ["Manutenções"]


def get_manutencao_repository() -> ManutencaoRepository:
    return ManutencaoRepository()


@manutencao_router.post("/", response_model=Manutencao, status_code=201)
async def criar_manutencao(manutencao: Manutencao, manutencao_repo: ManutencaoRepository = Depends(get_manutencao_repository)):
    try:
        manutencao_criada = await manutencao_repo.create(manutencao)
        if not manutencao_criada:
            raise HTTPException(status_code=500, detail="Erro ao criar manutenção")
        return manutencao_criada
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@manutencao_router.get("/", response_model=List[Manutencao])
async def listar_manutencoes(
    data_inicial: Optional[datetime] = Query(None),
    data_final: Optional[datetime] = Query(None),
    tipo_manutencao: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    manutencao_repo: ManutencaoRepository = Depends(get_manutencao_repository)
):
    return await manutencao_repo.get_all(data_inicial=data_inicial, data_final=data_final, tipo_manutencao=tipo_manutencao, page=skip // limit + 1, limit=limit)


@manutencao_router.get("/{manutencao_id}", response_model=Manutencao)
async def buscar_manutencao_por_id(
    manutencao_id: str,
    manutencao_repo: ManutencaoRepository = Depends(get_manutencao_repository)
):
    manutencao = await manutencao_repo.get_by_id(manutencao_id)
    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    return manutencao


@manutencao_router.put("/{manutencao_id}", response_model=Manutencao)
async def atualizar_manutencao(
    manutencao_id: str,
    manutencao: Manutencao,
    manutencao_repo: ManutencaoRepository = Depends(get_manutencao_repository)
):
    manutencao_atualizada = await manutencao_repo.update(manutencao_id, manutencao)
    if not manutencao_atualizada:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada ou ID inválido")
    return manutencao_atualizada


@manutencao_router.delete("/{manutencao_id}", status_code=204)
async def deletar_manutencao(manutencao_id: str, manutencao_repo: ManutencaoRepository = Depends(get_manutencao_repository)):
    if not await manutencao_repo.delete(manutencao_id):
        raise HTTPException(status_code=404, detail="Manutenção não encontrada ou ID inválido")
    return  


@manutencao_router.get("/estatisticas/tipos_frequentes")
async def obter_tipos_manutencao_mais_frequentes(manutencao_repo: ManutencaoRepository = Depends(get_manutencao_repository)):
    tipos = await manutencao_repo.get_tipos_manutencao_mais_frequentes()
    return tipos

@manutencao_router.get("/estatisticas/total", response_model=int)
async def obter_total_manutencoes(manutencao_repo: ManutencaoRepository = Depends(get_manutencao_repository)):
    total = await manutencao_repo.get_quantidade_manutencoes()
    return total