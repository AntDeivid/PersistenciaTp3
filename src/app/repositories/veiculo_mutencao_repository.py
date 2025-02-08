import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from src.app.core.db.database import database
from src.app.models.manutencao import Manutencao
from src.app.models.veiculo_manutencao import VeiculoManutencao


class VeiculoManutencaoRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.collection = database.get_collection("veiculo_manutencoes")

    async def create(self, veiculo_manutencao: VeiculoManutencao) -> VeiculoManutencao:
        try:
            veiculo_manutencao_dict = veiculo_manutencao.model_dump(by_alias=True, exclude={"id"})
            new_veiculo_manutencao = await self.collection.insert_one(veiculo_manutencao_dict)
            veiculo_manutencao_created = await self.collection.find_one(
                {"_id": new_veiculo_manutencao.inserted_id}
            )

            if not veiculo_manutencao_created:
                self.logger.error("Erro ao criar veículo_manutencao: Registro não encontrado após inserção.")
                return None

            veiculo_manutencao_created["_id"] = str(veiculo_manutencao_created["_id"])
            return VeiculoManutencao(**veiculo_manutencao_created)
        except Exception as e:
            self.logger.error(f"Erro ao criar veículo_manutencao: {e}")
            return None

    async def get_all(self) -> List[VeiculoManutencao]:
        veiculo_manutencoes = await self.collection.find().to_list(length=1000)
        for vm in veiculo_manutencoes:
            vm["_id"] = str(vm["_id"])
        return [VeiculoManutencao(**vm) for vm in veiculo_manutencoes]

    async def get_by_id(self, veiculo_manutencao_id: str) -> Optional[VeiculoManutencao]:
        try:
            veiculo_manutencao = await self.collection.find_one({"_id": ObjectId(veiculo_manutencao_id)})
            if not veiculo_manutencao:
                return None
            veiculo_manutencao["_id"] = str(veiculo_manutencao["_id"])
            return VeiculoManutencao(**veiculo_manutencao)
        except Exception as e:
            self.logger.error(f"Erro ao buscar veículo_manutencao com ID {veiculo_manutencao_id}: {e}")
            return None

    async def get_total_custo_manutencao_por_marca(self) -> List[dict]:
        pipeline = [
            {
                "$lookup": {
                    "from": "veiculos",
                    "localField": "veiculo_id",
                    "foreignField": "_id",
                    "as": "veiculo"
                }
            },
            {
                "$unwind": "$veiculo"
            },
            {
                "$lookup": {
                    "from": "manutencoes",
                    "localField": "manutencao_id",
                    "foreignField": "_id",
                    "as": "manutencao"
                }
            },
            {
                "$unwind": "$manutencao"
            },
            {
                "$group": {
                    "_id": "$veiculo.marca",
                    "custo_total": {"$sum": "$manutencao.custo"}
                }
            },
            {
                "$sort": {"custo_total": -1}
            }
        ]
        return await self.collection.aggregate(pipeline).to_list(length=1000)

    async def get_veiculos_com_mais_manutencoes(self, start_date: datetime, end_date: datetime) -> List[dict]:
        pipeline = [
            {
                "$lookup": {
                    "from": "manutencoes",
                    "localField": "manutencao_id",
                    "foreignField": "_id",
                    "as": "manutencao"
                }
            },
            {
                "$unwind": "$manutencao"
            },
            {
                "$match": {
                    "manutencao.data": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$lookup": {
                    "from": "veiculos",
                    "localField": "veiculo_id",
                    "foreignField": "_id",
                    "as": "veiculo"
                }
            },
            {
                "$unwind": "$veiculo"
            },
            {
                "$group": {
                    "_id": "$veiculo._id",
                    "modelo": {"$first": "$veiculo.modelo"},
                    "marca": {"$first": "$veiculo.marca"},
                    "num_manutencoes": {"$sum": 1}
                }
            },
            {
                "$sort": {"num_manutencoes": -1}
            }
        ]
        return await self.collection.aggregate(pipeline).to_list(length=1000)

    async def get_manutencao_mais_cara_por_veiculo(self) -> List[dict]:
        pipeline = [
            {
                "$lookup": {
                    "from": "manutencoes",
                    "localField": "manutencao_id",
                    "foreignField": "_id",
                    "as": "manutencao"
                }
            },
            {
                "$unwind": "$manutencao"
            },
            {
                "$lookup": {
                    "from": "veiculos",
                    "localField": "veiculo_id",
                    "foreignField": "_id",
                    "as": "veiculo"
                }
            },
            {
                "$unwind": "$veiculo"
            },
            {
                "$group": {
                    "_id": "$veiculo._id",
                    "modelo": {"$first": "$veiculo.modelo"},
                    "marca": {"$first": "$veiculo.marca"},
                    "max_custo": {"$max": "$manutencao.custo"}
                }
            },
            {
                "$lookup": {
                    "from": "manutencoes",
                    "localField": "max_custo",
                    "foreignField": "custo",
                    "as": "manutencao_mais_cara"
                }
            },
            {
                "$unwind": "$manutencao_mais_cara"
            },
            {
                "$project": {
                    "modelo": 1,
                    "marca": 1,
                    "tipo_manutencao": "$manutencao_mais_cara.tipo_manutencao",
                    "custo": "$manutencao_mais_cara.custo",
                    "observacao": "$manutencao_mais_cara.observacao"
                }
            }
        ]
        return await self.collection.aggregate(pipeline).to_list(length=1000)

    async def get_veiculos_com_maior_custo_manutencao(self) -> List[dict]:
        pipeline = [
            {
                "$lookup": {
                    "from": "manutencoes",
                    "localField": "manutencao_id",
                    "foreignField": "_id",
                    "as": "manutencao"
                }
            },
            {
                "$unwind": "$manutencao"
            },
            {
                "$lookup": {
                    "from": "veiculos",
                    "localField": "veiculo_id",
                    "foreignField": "_id",
                    "as": "veiculo"
                }
            },
            {
                "$unwind": "$veiculo"
            },
            {
                "$group": {
                    "_id": "$veiculo._id",
                    "modelo": {"$first": "$veiculo.modelo"},
                    "marca": {"$first": "$veiculo.marca"},
                    "custo_total": {"$sum": "$manutencao.custo"}
                }
            },
            {
                "$sort": {"custo_total": -1}
            }
        ]
        return await self.collection.aggregate(pipeline).to_list(length=1000)

    async def get_quantidade_veiculos_manutencao(self) -> int:
        return await self.collection.count_documents({})

    async def update(self, veiculo_manutencao_id: str, veiculo_manutencao_data: dict) -> Optional[VeiculoManutencao]:
        try:
            update_result = await self.collection.update_one(
                {"_id": ObjectId(veiculo_manutencao_id)},
                {"$set": veiculo_manutencao_data}
            )
            if update_result.modified_count > 0:
                return await self.get_by_id(veiculo_manutencao_id)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao atualizar veículo_manutencao com ID {veiculo_manutencao_id}: {e}")
            return None

    async def delete(self, veiculo_manutencao_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(veiculo_manutencao_id)})
        return result.deleted_count > 0