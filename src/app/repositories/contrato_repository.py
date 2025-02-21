import logging
from datetime import datetime, timedelta
from typing import List, Optional

from bson import ObjectId
from pymongo import ASCENDING

from src.app.core.db.database import database
from src.app.models.contrato import Contrato
from src.app.dtos.contrato_dto import ContratoDTO
from src.app.models.pagination_result import PaginationResult


class ContratoRepository:
    def __init__(self):
        self.logger = logging.getLogger("app_logger.repositories.contrato_repository")
        self.collection = database.get_collection("contratos")

    async def create(self, contrato_dto: ContratoDTO) -> Optional[ContratoDTO]:
        try:
            contrato_dict = contrato_dto.model_dump(by_alias=True)
            contrato_dict['usuario_id'] = ObjectId(contrato_dict['usuario_id'])
            contrato_dict['veiculo_id'] = ObjectId(contrato_dict['veiculo_id'])
            if contrato_dict.get('pagamento_id'):
                contrato_dict['pagamento_id'] = ObjectId(contrato_dict['pagamento_id'])
                
            new_contrato = await self.collection.insert_one(contrato_dict)
            contrato_created = await self.collection.find_one({"_id": new_contrato.inserted_id})

            if not contrato_created:
                self.logger.error("Error creating contract: Contract not found after insertion.")
                return None

            return ContratoDTO.from_model(Contrato(**contrato_created))
        except Exception as e:
            self.logger.error(f"Error creating contract: {e}")
            return None

    async def get_by_id(self, contrato_id: str) -> Optional[ContratoDTO]:
        try:
            _id = ObjectId(contrato_id)
            contrato = await self.collection.find_one({"_id": _id})

            if not contrato:
                return None

            return ContratoDTO.from_model(Contrato(**contrato))
        except Exception as e:
            self.logger.error(f"Error getting contract with ID {contrato_id}: {e}")
            return None

    async def get_all_no_pagination(self) -> List[ContratoDTO]:
        contratos = await self.collection.find().to_list(length=1000)
        return [ContratoDTO.from_model(Contrato(**contrato)) for contrato in contratos]

    async def get_all(self, data_inicial: Optional[datetime] = None, data_final: Optional[datetime] = None,
                      page: int = 1, limit: int = 10) -> PaginationResult:
        query = {}
        if data_inicial and data_final:
            query['data_inicio'] = {'$gte': data_inicial}
            query['data_fim'] = {'$lte': data_final}
        elif data_inicial:
            query['data_inicio'] = data_inicial

        total_items = await self.collection.count_documents(query)
        number_of_pages = (total_items + limit - 1) // limit

        cursor = self.collection.find(query).skip((page - 1) * limit).limit(limit)
        contratos = []
        async for document in cursor:
            contratos.append(ContratoDTO.from_model(Contrato(**document)))

        return PaginationResult(
            page=page,
            limit=limit,
            total_items=total_items,
            number_of_pages=number_of_pages,
            data=contratos
        )


    async def get_contratos_by_usuario_id(self, usuario_id: str) -> List[ContratoDTO]:
        contratos = []
        async for document in self.collection.find({"usuario_id": ObjectId(usuario_id)}):
            contratos.append(ContratoDTO.from_model(Contrato(**document)))
        return contratos

    
    async def search(self, placa: Optional[str] = None, nome_usuario: Optional[str] = None, page: int = 1,
                     limit: int = 10) -> PaginationResult:
        pipeline = []

        if not placa and not nome_usuario:
            pipeline.append({"$match": {}})

        if placa:
            pipeline.extend([
                {"$lookup": {
                    "from": "veiculos",
                    "localField": "veiculo_id",
                    "foreignField": "_id",
                    "as": "veiculo"
                }},
                {"$unwind": {"path": "$veiculo", "preserveNullAndEmptyArrays": True}},
                {"$match": {"veiculo.placa": placa}}
            ])

        if nome_usuario:
            pipeline.extend([
                {"$lookup": {
                    "from": "usuarios",
                    "localField": "usuario_id",
                    "foreignField": "_id",
                    "as": "usuario"
                }},
                {"$unwind": {"path": "$usuario", "preserveNullAndEmptyArrays": True}},
                {"$match": {"usuario.nome": nome_usuario}}
            ])

        count_pipeline = pipeline + [{"$count": "total_items"}]
        total_items_cursor = await self.collection.aggregate(count_pipeline).to_list(length=1)
        total_items = total_items_cursor[0]["total_items"] if total_items_cursor else 0

        # Paginação
        pagination_pipeline = pipeline + [
            {"$sort": {"_id": ASCENDING}},
            {"$skip": (page - 1) * limit},
            {"$limit": limit},
            {"$project": self._project_contrato()}
        ]

        contratos = await self.collection.aggregate(pagination_pipeline).to_list(length=limit)
        print(contratos)
        number_of_pages = (total_items + limit - 1) // limit

        for contrato in contratos:
            contrato["_id"] = str(contrato["_id"])
            if "usuario_id" in contrato and isinstance(contrato["usuario_id"], ObjectId):
                contrato["usuario_id"] = str(contrato["usuario_id"])
            if "veiculo_id" in contrato and isinstance(contrato["veiculo_id"], ObjectId):
                contrato["veiculo_id"] = str(contrato["veiculo_id"])
            if "pagamento_id" in contrato and isinstance(contrato["pagamento_id"], ObjectId):
                contrato["pagamento_id"] = str(contrato["pagamento_id"])

        print("contratos", contratos)

        return PaginationResult(
            page=page,
            limit=limit,
            total_items=total_items,
            number_of_pages=number_of_pages,
            data=contratos
        )

    async def get_contratos_by_veiculo_marca_pagamento_pago(self, marca: str, pagamento_pago: Optional[bool] = None) -> List[ContratoDTO]:
        pipeline = [
            {"$lookup": {"from": "veiculos", "localField": "veiculo_id", "foreignField": "_id", "as": "veiculo"}},
            {"$unwind": "$veiculo"},
            {"$match": {"veiculo.marca": marca}},
        ]

        if pagamento_pago is not None:
            pipeline.extend([
                {"$lookup": {"from": "pagamentos", "localField": "pagamento_id", "foreignField": "_id", "as": "pagamento"}},
                {"$unwind": {"path": "$pagamento", "preserveNullAndEmptyArrays": True}},
                {"$match": {"pagamento.pago": pagamento_pago}}
            ])

        # Ajuste final do pipeline para remover os arrays e projetar apenas os campos necessários para o formato Contrato
        pipeline.extend([{"$project": self._project_contrato()}])

        contratos = await self.collection.aggregate(pipeline).to_list(length=1000)
        return [ContratoDTO.from_model(Contrato(
            id=ObjectId(contrato["_id"]) if ObjectId.is_valid(contrato["_id"]) else None,
            usuario_id=ObjectId(contrato["usuario_id"]) if ObjectId.is_valid(contrato["usuario_id"]) else None,
            veiculo_id=ObjectId(contrato["veiculo_id"]) if ObjectId.is_valid(contrato["veiculo_id"]) else None,
            pagamento_id=ObjectId(contrato["pagamento_id"]) if contrato.get("pagamento_id") and ObjectId.is_valid(contrato["pagamento_id"]) else None,
            data_inicio=contrato["data_inicio"],
            data_fim=contrato["data_fim"]
        )) for contrato in contratos]

    async def get_contratos_by_pagamento_vencimento_month_and_usuario_id(self, vencimento_month: datetime, usuario_id: Optional[str] = None) -> List[ContratoDTO]:
        vencimento_inicio = vencimento_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        vencimento_fim = (vencimento_inicio + timedelta(days=31)).replace(day=1)

        pipeline = [
            {"$lookup": {"from": "pagamentos", "localField": "pagamento_id", "foreignField": "_id", "as": "pagamento"}},
            {"$unwind": "$pagamento"},
            {"$match": {"pagamento.vencimento": {"$gte": vencimento_inicio, "$lte": vencimento_fim}}}
        ]

        if usuario_id:
            pipeline.extend([{ "$match": {"usuario_id": ObjectId(usuario_id)} }])

        # Ajuste final do pipeline para remover os arrays e projetar apenas os campos necessários para o formato Contrato
        pipeline.extend([{"$project": self._project_contrato()}])

        contratos = await self.collection.aggregate(pipeline).to_list(length=1000)
        return [ContratoDTO.from_model(Contrato(
            id=ObjectId(contrato["_id"]) if ObjectId.is_valid(contrato["_id"]) else None,
            usuario_id=ObjectId(contrato["usuario_id"]) if ObjectId.is_valid(contrato["usuario_id"]) else None,
            veiculo_id=ObjectId(contrato["veiculo_id"]) if ObjectId.is_valid(contrato["veiculo_id"]) else None,
            pagamento_id=ObjectId(contrato["pagamento_id"]) if contrato.get("pagamento_id") and ObjectId.is_valid(contrato["pagamento_id"]) else None,
            data_inicio=contrato["data_inicio"],
            data_fim=contrato["data_fim"]
        )) for contrato in contratos]

    async def update(self, contrato_id: str, contrato_dto: ContratoDTO) -> Optional[ContratoDTO]:
        try:
            contrato = contrato_dto.to_model()
            contrato_dict = contrato.model_dump(by_alias=True)
            update_result = await self.collection.update_one({"_id": ObjectId(contrato_id)}, {"$set": contrato_dict})
            if update_result.modified_count > 0:
                return await self.get_by_id(contrato_id)  # Retorna o contrato atualizado
            else:
                return None
        except Exception as e:
            self.logger.error(f"Erro ao atualizar contrato com ID {contrato_id}: {e}")
            return None

    async def delete(self, contrato_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(contrato_id)})
        return result.deleted_count > 0

    async def get_quantidade_contratos(self) -> int:
        total_contratos = await self.collection.count_documents({})
        return total_contratos

    def _project_contrato(self):
        return {
            "_id": {"$toString": "$_id"},
            "usuario_id": 1,
            "veiculo_id": 1,
            "pagamento_id": 1,
            "data_inicio": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S", "date": "$data_inicio"}},
            "data_fim": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S", "date": "$data_fim"}}
        }