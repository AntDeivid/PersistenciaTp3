import logging
from datetime import datetime, timedelta
from typing import List, Optional

from bson import ObjectId
from pymongo import ASCENDING

from src.app.core.db.database import database
from src.app.models.contrato import Contrato
from src.app.models.pagination_result import PaginationResult


class ContratoRepository:
    def __init__(self):
        self.logger = logging.getLogger("app_logger.repositories.contrato_repository")
        self.collection = database.get_collection("contratos")

    async def create(self, contrato: Contrato) -> Contrato | None:
        try:
            contrato_dict = contrato.model_dump(by_alias=True, exclude={"id"})
            new_contrato = await self.collection.insert_one(contrato_dict)
            contrato_created = await self.collection.find_one({"_id": new_contrato.inserted_id})

            if not contrato_created:
                self.logger.error("Error creating contract: Contract not found after insertion.")
                return None

            contrato_created["_id"] = str(contrato_created["_id"])
            return Contrato(**contrato_created)
        except Exception as e:
            self.logger.error(f"Error creating contract: {e}")
            return None

    async def get_by_id(self, contrato_id: str) -> Contrato | None:
        try:
            _id = ObjectId(contrato_id)
            contrato = await self.collection.find_one({"_id": _id})

            if not contrato:
                return None

            contrato["_id"] = str(contrato["_id"])
            return Contrato(**contrato)
        except Exception as e:
            self.logger.error(f"Error getting contract with ID {contrato_id}: {e}")
            return None

    async def get_all_no_pagination(self) -> List[Contrato]:
        contratos = await self.collection.find().to_list(length=1000)

        for contrato in contratos:
            contrato["_id"] = str(contrato["_id"])

        return [Contrato(**contrato) for contrato in contratos]

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
            document["_id"] = str(document["_id"])
            contratos.append(Contrato(**document))

        return PaginationResult(
            page=page,
            limit=limit,
            total_items=total_items,
            number_of_pages=number_of_pages,
            data=contratos
        )

    async def get_contratos_by_usuario_id(self, usuario_id: str) -> List[Contrato]:
        contratos = []
        async for document in self.collection.find({"usuario_id": usuario_id}):
            document["_id"] = str(document["_id"])
            contratos.append(Contrato(**document))
        return contratos

    async def search(self, placa: Optional[str] = None, nome_usuario: Optional[str] = None, page: int = 1,
                     limit: int = 10) -> PaginationResult:
        pipeline = []

        # Se precisar filtrar por placa, adiciona os estágios necessários
        if placa:
            pipeline.extend([
                {"$lookup": {"from": "veiculos", "localField": "veiculo_id", "foreignField": "_id", "as": "veiculo"}},
                {"$unwind": "$veiculo"},  # Sem preserveNullAndEmptyArrays para garantir match correto
                {"$match": {"veiculo.placa": placa}}
            ])

        # Se precisar filtrar por nome de usuário, adiciona os estágios necessários
        if nome_usuario:
            pipeline.extend([
                {"$set": {"usuario_id": {"$toObjectId": "$usuario_id"}}},
                {"$lookup": {"from": "usuarios", "localField": "usuario_id", "foreignField": "_id", "as": "usuario"}},
                {"$unwind": "$usuario"},
                {"$match": {"usuario.nome": nome_usuario}}
            ])

        # Criar pipeline separada para contagem antes de aplicar paginação
        count_pipeline = pipeline + [{"$count": "total_items"}]
        total_items_cursor = await self.collection.aggregate(count_pipeline).to_list(length=1)
        total_items = total_items_cursor[0]["total_items"] if total_items_cursor else 0

        # Aplicar paginação na consulta principal
        pagination_pipeline = pipeline + [
            {"$sort": {"_id": ASCENDING}},  # Garante uma ordenação consistente
            {"$skip": (page - 1) * limit},
            {"$limit": limit},
            {"$project": self._project_contrato()}
        ]

        contratos = await self.collection.aggregate(pagination_pipeline).to_list(length=limit)
        number_of_pages = (total_items + limit - 1) // limit

        return PaginationResult(
            page=page,
            limit=limit,
            total_items=total_items,
            number_of_pages=number_of_pages,
            data=contratos
        )

    async def get_contratos_by_veiculo_marca_pagamento_pago(self, marca: str, pagamento_pago: Optional[bool] = None) -> List[Contrato]:
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
        return [Contrato(**contrato) for contrato in contratos]

    async def get_contratos_by_pagamento_vencimento_month_and_usuario_id(self, vencimento_month: datetime, usuario_id: Optional[str] = None) -> List[Contrato]:
        vencimento_inicio = vencimento_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        vencimento_fim = (vencimento_inicio + timedelta(days=31)).replace(day=1)

        pipeline = [
            {"$lookup": {"from": "pagamentos", "localField": "pagamento_id", "foreignField": "_id", "as": "pagamento"}},
            {"$unwind": "$pagamento"},
            {"$match": {"pagamento.vencimento": {"$gte": vencimento_inicio, "$lte": vencimento_fim}}}
        ]

        if usuario_id:
            pipeline.extend([{ "$match": {"usuario_id": usuario_id} }])

        # Ajuste final do pipeline para remover os arrays e projetar apenas os campos necessários para o formato Contrato
        pipeline.extend([{"$project": self._project_contrato()}])

        contratos = await self.collection.aggregate(pipeline).to_list(length=1000)
        return [Contrato(**contrato) for contrato in contratos]

    async def update(self, contrato_id: str, contrato: Contrato) -> Optional[Contrato]:
        try:
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
        return await self.collection.count_documents({})

    def _project_contrato(self):
        return {
            "_id": {"$toString": "$_id"},
            "usuario_id": 1,
            "veiculo_id": 1,
            "pagamento_id": 1,
            "data_inicio": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S", "date": "$data_inicio"}},
            "data_fim": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S", "date": "$data_fim"}}
        }