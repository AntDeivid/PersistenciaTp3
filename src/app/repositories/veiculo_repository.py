import logging
from typing import Optional, List

from bson import ObjectId

from src.app.core.db.database import database
from src.app.dtos.veiculo_dto import VeiculoDTO
from src.app.models.pagination_result import PaginationResult
from src.app.models.veiculo import Veiculo


class VeiculoRepository:
    def __init__(self):
        self.logger = logging.getLogger("app_logger.repositories.veiculo_repository")
        self.collection = database.get_collection("veiculos")

    async def create(self, veiculo: VeiculoDTO) -> VeiculoDTO:
        try:
            veiculo_dict = veiculo.model_dump(by_alias=True, exclude={"id"})
            new_veiculo = await self.collection.insert_one(veiculo_dict)
            veiculo_created = await self.collection.find_one({"_id": new_veiculo.inserted_id})

            if not veiculo_created:
                self.logger.error("Erro ao criar veículo: Veículo não encontrado após inserção.")
                return None

            saved = Veiculo(**veiculo_created)
            return VeiculoDTO.from_model(saved)
        except Exception as e:
            self.logger.error(f"Erro ao criar veículo: {e}")
            return None

    async def get_all_no_pagination(self) -> List[VeiculoDTO]:
        veiculos = await self.collection.find().to_list(length=1000)
        result = [Veiculo(**veiculo) for veiculo in veiculos]
        return [VeiculoDTO.from_model(r) for r in result]

    async def get_by_id(self, veiculo_id: str) -> Optional[VeiculoDTO]:
        try:
            veiculo = await self.collection.find_one({"_id": ObjectId(veiculo_id)})
            if not veiculo:
                return None
            return VeiculoDTO.from_model(Veiculo(**veiculo))
        except Exception as e:
            self.logger.error(f"Erro ao buscar veículo com ID {veiculo_id}: {e}")
            return None

    async def get_veiculos_by_tipo_manutencao(self, tipo_manutencao: str) -> List[VeiculoDTO]:
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
                "$unwind": "$manutencoes"
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
                "$unwind": "$manutencoes_detalhes"
            },
            {
                "$match": {
                    "manutencoes_detalhes.tipo_manutencao": {"$regex": tipo_manutencao, "$options": "i"}
                }
            },
            {
                "$group": {
                    "_id": "$_id",
                    "marca": {"$first": "$marca"},
                    "modelo": {"$first": "$modelo"},
                    "ano": {"$first": "$ano"},
                    "placa": {"$first": "$placa"},
                    "manutencoes": {"$push": "$manutencoes_detalhes"}
                }
            }
        ]
        veiculos = await self.collection.aggregate(pipeline).to_list(length=1000)
        return [VeiculoDTO.from_model(Veiculo(**veiculo)) for veiculo in veiculos]

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
            veiculos.append(Veiculo(**document))

        result = [VeiculoDTO.from_model(veiculo) for veiculo in veiculos]

        return PaginationResult(
            page=page,
            limit=limit,
            total_items=total_items,
            number_of_pages=number_of_pages,
            data=result
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
                "$unwind": "$manutencoes"
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
                "$unwind": "$manutencoes_detalhes"
            },
            {
                "$group": {
                    "_id": "$_id",
                    "modelo": {"$first": "$modelo"},
                    "marca": {"$first": "$marca"},
                    "custo_medio": {"$avg": "$manutencoes_detalhes.custo"}
                }
            },
            {
                "$sort": {"custo_medio": -1}
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1000)
        for veiculo in result:
            veiculo["_id"] = str(veiculo["_id"])

        return result

    async def update(self, veiculo_id: str, veiculo_data: dict) -> Optional[VeiculoDTO]:
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