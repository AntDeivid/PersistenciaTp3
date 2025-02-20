from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from src.app.dtos.veiculo_dto import VeiculoDTO
from src.app.models.pagination_result import PaginationResult
from src.app.repositories.veiculo_repository import VeiculoRepository

veiculo_router = APIRouter()
veiculo_router.prefix = "/api/veiculos"
veiculo_router.tags = ["Veículos"]

def get_veiculo_repository() -> VeiculoRepository:
    return VeiculoRepository()

@veiculo_router.post("/", response_model=VeiculoDTO, status_code=201)
async def create_veiculo(veiculo: VeiculoDTO, veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    created_veiculo = await veiculo_repository.create(veiculo)
    if not created_veiculo:
        raise HTTPException(status_code=500, detail="Erro ao criar veículo")
    return created_veiculo

@veiculo_router.get("/all-no-pagination", response_model=list[VeiculoDTO])
async def get_all_veiculos_no_pagination(veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    return await veiculo_repository.get_all_no_pagination()

@veiculo_router.get("/")
async def get_all_veiculos(
    tipo: Optional[str] = None,
    marca: Optional[str] = None,
    modelo: Optional[str] = None,
    ano: Optional[int] = None,
    page: int = 1,
    limit: int = 10,
    veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)
) -> PaginationResult:
    return await veiculo_repository.get_all(tipo, marca, modelo, ano, page, limit)

@veiculo_router.get("/{veiculo_id}", response_model=VeiculoDTO)
async def get_veiculo_by_id(veiculo_id: str, veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    veiculo = await veiculo_repository.get_by_id(veiculo_id)
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

@veiculo_router.get("/com-manutencoes", response_model=list[VeiculoDTO])
async def get_veiculos_com_manutencoes(veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    return await veiculo_repository.get_veiculos_com_manutencoes()

@veiculo_router.get("/by-tipo-manutencao/{tipo_manutencao}", response_model=list[VeiculoDTO])
async def get_veiculos_by_tipo_manutencao(tipo_manutencao: str, veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    return await veiculo_repository.get_veiculos_by_tipo_manutencao(tipo_manutencao)

@veiculo_router.get("/count")
async def count_veiculos(veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    return await veiculo_repository.get_quantidade_veiculos()

@veiculo_router.get("/custo-medio-manutencoes", response_model=list[dict])
async def get_custo_medio_manutencoes_por_veiculo(veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    return await veiculo_repository.get_custo_medio_manutencoes_por_veiculo()

@veiculo_router.put("/{veiculo_id}", response_model=VeiculoDTO)
async def update_veiculo(veiculo_id: str, veiculo_data: dict, veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    updated_veiculo = await veiculo_repository.update(veiculo_id, veiculo_data)
    if not updated_veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado ou ID inválido")
    return updated_veiculo

@veiculo_router.delete("/{veiculo_id}", status_code=204)
async def delete_veiculo(veiculo_id: str, veiculo_repository: VeiculoRepository = Depends(get_veiculo_repository)):
    if not await veiculo_repository.delete(veiculo_id):
        raise HTTPException(status_code=404, detail="Veículo não encontrado ou ID inválido")
    return