from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from src.app.models.veiculo_manutencao import VeiculoManutencao
from src.app.repositories.veiculo_mutencao_repository import VeiculoManutencaoRepository

veiculo_manutencao_router = APIRouter()
veiculo_manutencao_router.prefix = "/api/veiculo-manutencoes"
veiculo_manutencao_router.tags = ["Veículo Manutenções"]

def get_veiculo_manutencao_repository() -> VeiculoManutencaoRepository:
    return VeiculoManutencaoRepository()

@veiculo_manutencao_router.post("/", response_model=VeiculoManutencao, status_code=201)
async def create_veiculo_manutencao(veiculo_manutencao: VeiculoManutencao, veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    created_veiculo_manutencao = await veiculo_manutencao_repository.create(veiculo_manutencao)
    if not created_veiculo_manutencao:
        raise HTTPException(status_code=500, detail="Erro ao criar veículo_manutencao")
    return created_veiculo_manutencao

@veiculo_manutencao_router.get("/", response_model=list[VeiculoManutencao])
async def get_all_veiculo_manutencoes(veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    return await veiculo_manutencao_repository.get_all()

@veiculo_manutencao_router.get("/{veiculo_manutencao_id}", response_model=VeiculoManutencao)
async def get_veiculo_manutencao_by_id(veiculo_manutencao_id: str, veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    veiculo_manutencao = await veiculo_manutencao_repository.get_by_id(veiculo_manutencao_id)
    if not veiculo_manutencao:
        raise HTTPException(status_code=404, detail="Veículo_manutencao não encontrado")
    return veiculo_manutencao

@veiculo_manutencao_router.get("/total-custo-por-marca", response_model=list[dict])
async def get_total_custo_manutencao_por_marca(veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    return await veiculo_manutencao_repository.get_total_custo_manutencao_por_marca()

@veiculo_manutencao_router.get("/veiculos-com-mais-manutencoes")
async def get_veiculos_com_mais_manutencoes(start_date: datetime, end_date: datetime, veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    return await veiculo_manutencao_repository.get_veiculos_com_mais_manutencoes(start_date, end_date)

@veiculo_manutencao_router.get("/manutencao-mais-cara-por-veiculo", response_model=list[dict])
async def get_manutencao_mais_cara_por_veiculo(veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    return await veiculo_manutencao_repository.get_manutencao_mais_cara_por_veiculo()

@veiculo_manutencao_router.get("/veiculos-com-maior-custo-manutencao", response_model=list[dict])
async def get_veiculos_com_maior_custo_manutencao(veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    return await veiculo_manutencao_repository.get_veiculos_com_maior_custo_manutencao()

@veiculo_manutencao_router.get("/count")
async def count_veiculo_manutencoes(veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    return await veiculo_manutencao_repository.get_quantidade_veiculos_manutencao()

@veiculo_manutencao_router.put("/{veiculo_manutencao_id}", response_model=VeiculoManutencao)
async def update_veiculo_manutencao(veiculo_manutencao_id: str, veiculo_manutencao_data: dict, veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    updated_veiculo_manutencao = await veiculo_manutencao_repository.update(veiculo_manutencao_id, veiculo_manutencao_data)
    if not updated_veiculo_manutencao:
        raise HTTPException(status_code=404, detail="Veículo_manutencao não encontrado ou ID inválido")
    return updated_veiculo_manutencao

@veiculo_manutencao_router.delete("/{veiculo_manutencao_id}", status_code=204)
async def delete_veiculo_manutencao(veiculo_manutencao_id: str, veiculo_manutencao_repository: VeiculoManutencaoRepository = Depends(get_veiculo_manutencao_repository)):
    if not await veiculo_manutencao_repository.delete(veiculo_manutencao_id):
        raise HTTPException(status_code=404, detail="Veículo_manutencao não encontrado ou ID inválido")
    return