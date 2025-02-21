from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from src.app.dtos.contrato_dto import ContratoDTO
from src.app.models.pagination_result import PaginationResult
from src.app.repositories.contrato_repository import ContratoRepository

contrato_router = APIRouter()
contrato_router.prefix = "/api/contratos"
contrato_router.tags = ["Contratos"]

def get_contrato_repository() -> ContratoRepository:
    return ContratoRepository()

@contrato_router.post("/", response_model=ContratoDTO, status_code=201)
async def create_contract(contract: ContratoDTO, contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    created_contract = await contrato_repository.create(contract)
    if not created_contract:
        raise HTTPException(status_code=500, detail="Error creating contract")
    return created_contract

@contrato_router.get("/all-no-pagination", response_model=list[ContratoDTO])
async def get_all_contracts_no_pagination(contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    return await contrato_repository.get_all_no_pagination()

@contrato_router.get("/")
async def get_all_contracts(
        data_inicial: Optional[datetime] = None,
        data_final: Optional[datetime] = None,
        page: int = 1,
        limit: int = 10,
        contrato_repository: ContratoRepository = Depends(get_contrato_repository)
) -> PaginationResult:
    return await contrato_repository.get_all(data_inicial, data_final, page, limit)

@contrato_router.get("/by-user/{user_id}", response_model=list[ContratoDTO])
async def get_contracts_by_user(user_id: str, contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    contracts = await contrato_repository.get_contratos_by_usuario_id(user_id)
    return contracts

@contrato_router.get("/search")
async def search_contracts(
        placa: Optional[str] = None,
        nome_usuario: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        contrato_repository: ContratoRepository = Depends(get_contrato_repository)
) -> PaginationResult:
    return await contrato_repository.search(placa, nome_usuario, page, limit)

@contrato_router.get("/by-vehicle/{marca}")
async def get_contracts_by_vehicle(marca: str, pago: Optional[bool] = None, contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    contracts = await contrato_repository.get_contratos_by_veiculo_marca_pagamento_pago(marca, pago)
    return contracts

@contrato_router.get("/by-payment-month/{month}")
async def get_contracts_by_payment_month(month: datetime, usuario_id: Optional[str] = None, contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    contracts = await contrato_repository.get_contratos_by_pagamento_vencimento_month_and_usuario_id(month, usuario_id)
    return contracts

@contrato_router.get("/count")
async def count_contracts(contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    return await contrato_repository.get_quantidade_contratos()

@contrato_router.get("/{contract_id}", response_model=ContratoDTO)
async def get_contract_by_id(contract_id: str, contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    contract = await contrato_repository.get_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@contrato_router.put("/{contract_id}", response_model=ContratoDTO)
async def update_contract(contract_id: str, contract: ContratoDTO, contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    updated_contract = await contrato_repository.update(contract_id, contract)
    if not updated_contract:
        raise HTTPException(status_code=404, detail="Contract not found or invalid ID")
    return updated_contract

@contrato_router.delete("/{contract_id}", status_code=204)
async def delete_contract(contract_id: str, contrato_repository: ContratoRepository = Depends(get_contrato_repository)):
    if not await contrato_repository.delete(contract_id):
        raise HTTPException(status_code=404, detail="Contract not found or invalid ID")
    return