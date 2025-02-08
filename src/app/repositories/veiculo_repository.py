import logging
from typing import Optional, List

from bson import ObjectId

from src.app.core.db.database import database
from src.app.models.pagination_result import PaginationResult
from src.app.models.veiculo import Veiculo


class VeiculoRepository:
    def __init__(self):
        self.logger = logging.getLogger("app_logger.repositories.veiculo_repository")
        self.collection = database.get_collection("veiculos")

    async def create(self, veiculo: Veiculo) -> Veiculo:
        try:
            veiculo_dict = veiculo.model_dump(by_alias=True, exclude={"id"})
            new_veiculo = await self.collection.insert_one(veiculo_dict)
            veiculo_created = await self.collection.find_one({"_id": new_veiculo.inserted_id})

            if not veiculo_created:
                self.logger.error("Erro ao criar veículo: Veículo não encontrado após inserção.")
                return None

            veiculo_created["_id"] = str(veiculo_created["_id"])
            return Veiculo(**veiculo_created)
        except Exception as e:
            self.logger.error(f"Erro ao criar veículo: {e}")
            return None

    async def get_all_no_pagination(self) -> List[Veiculo]:
        veiculos = await self.collection.find().to_list(length=1000)
        for veiculo in veiculos:
            veiculo["_id"] = str(veiculo["_id"])
        return [Veiculo(**veiculo) for veiculo in veiculos]

    async def get_by_id(self, veiculo_id: str) -> Optional[Veiculo]:
        try:
            veiculo = await self.collection.find_one({"_id": ObjectId(veiculo_id)})
            if not veiculo:
                return None
            veiculo["_id"] = str(veiculo["_id"])
            return Veiculo(**veiculo)
        except Exception as e:
            self.logger.error(f"Erro ao buscar veículo com ID {veiculo_id}: {e}")
            return None

    async def get_veiculos_com_manutencoes(self) -> List[Veiculo]:
        pipeline = [
            {
                "$lookup": {
                    "from": "veiculo_manutencoes",
                    "localField": "_id",
                    "foreignField": "veiculo_id",
                    "as": "manutencoes"
                }
            },
            {
                "$lookup": {
                    "from": "manutencoes",
                    "localField": "manutencoes.manutencao_id",
                    "foreignField": "_id",
                    "as": "manutencoes_detalhes"
                }
            }
        ]
        veiculos = await self.collection.aggregate(pipeline).to_list(length=1000)
        for veiculo in veiculos:
            veiculo["_id"] = str(veiculo["_id"])
        return [Veiculo(**veiculo) for veiculo in veiculos]

    async def get_veiculos_by_tipo_manutencao(self, tipo_manutencao: str) -> List[Veiculo]:
        pipeline = [
            {
                "$lookup": {
                    "from": "veiculo_manutencoes",
                    "localField": "_id",
                    "foreignField": "veiculo_id",
                    "as": "manutencoes"
                }
            },
            {
                "$lookup": {
                    "from": "manutencoes",
                    "localField": "manutencoes.manutencao_id",
                    "foreignField": "_id",
                    "as": "manutencoes_detalhes"
                }
            },
            {
                "$match": {
                    "manutencoes_detalhes.tipo_manutencao": {"$regex": tipo_manutencao, "$options": "i"}
                }
            }
        ]
        veiculos = await self.collection.aggregate(pipeline).to_list(length=1000)
        for veiculo in veiculos:
            veiculo["_id"] = str(veiculo["_id"])
        return [Veiculo(**veiculo) for veiculo in veiculos]

    async def get_quantidade_veiculos(self) -> int:
        return await self.collection.count_documents({})

    async def get_all(
        self,
        tipo: Optional[str] = None,
        marca: Optional[str] = None,
        modelo: Optional[str] = None,
        ano: Optional[int] = None,
        page: int = 1,
        limit: int = 10
    ) -> PaginationResult:
        query = {}
        if tipo:
            query["tipo"] = tipo
        if marca:
            query["marca"] = marca
        if modelo:
            query["modelo"] = modelo
        if ano:
            query["ano"] = ano

        total_items = await self.collection.count_documents(query)
        number_of_pages = (total_items + limit - 1) // limit

        cursor = self.collection.find(query).skip((page - 1) * limit).limit(limit)
        veiculos = []
        async for document in cursor:
            document["_id"] = str(document["_id"])
            veiculos.append(Veiculo(**document))

        return PaginationResult(
            page=page,
            limit=limit,
            total_items=total_items,
            number_of_pages=number_of_pages,
            data=veiculos
        )

    async def get_custo_medio_manutencoes_por_veiculo(self) -> List[dict]:
        pipeline = [
            {
                "$lookup": {
                    "from": "veiculo_manutencoes",
                    "localField": "_id",
                    "foreignField": "veiculo_id",
                    "as": "manutencoes"
                }
            },
            {
                "$lookup": {
                    "from": "manutencoes",
                    "localField": "manutencoes.manutencao_id",
                    "foreignField": "_id",
                    "as": "manutencoes_detalhes"
                }
            },
            {
                "$project": {
                    "modelo": 1,
                    "marca": 1,
                    "custo_medio": {"$avg": "$manutencoes_detalhes.custo"}
                }
            },
            {
                "$sort": {"custo_medio": -1}
            }
        ]
        return await self.collection.aggregate(pipeline).to_list(length=1000)

    async def update(self, veiculo_id: str, veiculo_data: dict) -> Optional[Veiculo]:
        try:
            update_result = await self.collection.update_one(
                {"_id": ObjectId(veiculo_id)},
                {"$set": veiculo_data}
            )
            if update_result.modified_count > 0:
                return await self.get_by_id(veiculo_id)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao atualizar veículo com ID {veiculo_id}: {e}")
            return None

    async def delete(self, veiculo_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(veiculo_id)})
        return result.deleted_count > 0