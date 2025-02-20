import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from src.app.core.db.database import database  
from src.app.models.manutencao import Manutencao 
from src.app.dtos.manutencao_dto import ManutencaoDTO

logger = logging.getLogger('app_logger.manutencao_repository')

class ManutencaoRepository:
   
    def __init__(self):
        self.collection = database.get_collection("manutencoes")

    async def create(self, manutencao: Manutencao) -> Optional[ManutencaoDTO]:
        try:
            manutencao_dict = manutencao.dict(by_alias=True, exclude={"id"})
            nova_manutencao = await self.collection.insert_one(manutencao_dict)
            manutencao_criada = await self.collection.find_one({"_id": nova_manutencao.inserted_id})

            if not manutencao_criada:
                logger.error("Erro ao criar manutenção: Manutenção não encontrada após a inserção.")
                return None

            logger.info(f"Manutenção criada com sucesso: {manutencao_criada}")
            return ManutencaoDTO.from_model(Manutencao(**manutencao_criada))

        except DuplicateKeyError as e:
            logger.error(f"Erro ao criar manutenção: Manutenção duplicada - {e}")
            raise ValueError("Erro ao criar manutenção: Manutenção duplicada") from e
        except Exception as e:
            logger.error(f"Erro ao criar manutenção: {e}")
            return None

    async def get_all_no_pagination(self) -> List[ManutencaoDTO]:
        try:
            manutencoes = await self.collection.find().to_list(length=None)
            logger.info(f"Manutenções listadas sem paginação: {manutencoes}")
            result = [Manutencao(**manutencao) for manutencao in manutencoes]
            return [ManutencaoDTO.from_model(manutencao) for manutencao in result]
        except Exception as e:
            logger.error(f"Erro ao listar manutenções sem paginação: {e}")
            return []

    async def get_all(
        self,
        data_inicial: Optional[datetime] = None,
        data_final: Optional[datetime] = None,
        tipo_manutencao: Optional[str] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 10
    ) -> List[ManutencaoDTO]:
        try:
            filtro = {}
            if data_inicial and data_final:
                filtro["data"] = {"$gte": data_inicial, "$lte": data_final}
            elif data_inicial:
                filtro["data"] = data_inicial
            if tipo_manutencao:
                filtro["tipo_manutencao"] = tipo_manutencao

            logger.info(f"Buscando manutenções com filtros: {filtro}, página={page}, limite={limit}")

            skip = (page - 1) * limit
            manutencoes = await self.collection.find(filtro).skip(skip).limit(limit).to_list(length=limit)

            logger.info(f"Manutenções encontradas: {manutencoes}")
            result = [Manutencao(**manutencao) for manutencao in manutencoes]
            return [ManutencaoDTO.from_model(manutencao) for manutencao in result]
        except Exception as e:
            logger.error(f"Erro ao buscar manutenções: {e}")
            return []

    async def get_by_id(self, manutencao_id: str) -> Optional[ManutencaoDTO]:
        try:
            filtro = {"_id": ObjectId(manutencao_id)} if ObjectId.is_valid(manutencao_id) else {"_id": manutencao_id}
            manutencao = await self.collection.find_one(filtro)

            if not manutencao:
                logger.warning(f"Manutenção com ID {manutencao_id} não encontrada")
                return None

            logger.info(f"Manutenção encontrada com ID {manutencao_id}: {manutencao}")
            return ManutencaoDTO.from_model(Manutencao(**manutencao))
        except Exception as e:
            logger.error(f"Erro ao buscar manutenção com ID {manutencao_id}: {e}")
            return None

    async def update(self, manutencao_id: str, manutencao: Manutencao) -> Optional[ManutencaoDTO]:
        try:
            if not ObjectId.is_valid(manutencao_id):
                logger.warning(f"ID de manutenção inválido: {manutencao_id}")
                return None

            manutencao_dict = manutencao.dict(by_alias=True, exclude={"id"})
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(manutencao_id)},
                {"$set": manutencao_dict},
                return_document=ReturnDocument.AFTER  
            )

            if result:
                logger.info(f"Manutenção atualizada com sucesso: {result}")
                return ManutencaoDTO.from_model(Manutencao(**result))
            else:
                logger.warning(f"Manutenção com ID {manutencao_id} não encontrada para atualização")
                return None
        except Exception as e:
            logger.error(f"Erro ao atualizar manutenção com ID {manutencao_id}: {e}")
            return None

    async def delete(self, manutencao_id: str) -> bool:
        try:
            if not ObjectId.is_valid(manutencao_id):
                logger.warning(f"ID de manutenção inválido: {manutencao_id}")
                return False

            resultado = await self.collection.delete_one({"_id": ObjectId(manutencao_id)})
            if resultado.deleted_count > 0:
                logger.info(f"Manutenção com ID {manutencao_id} deletada com sucesso")
                return True
            else:
                logger.warning(f"Manutenção com ID {manutencao_id} não encontrada para deleção")
                return False
        except Exception as e:
            logger.error(f"Erro ao deletar manutenção com ID {manutencao_id}: {e}")
            return False

    async def get_tipos_manutencao_mais_frequentes(self) -> List[Dict[str, Any]]:
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$tipo_manutencao",
                        "frequencia": {"$sum": 1}
                    }
                },
                {
                    "$project": {
                        "_id": 0,  
                        "tipo_manutencao": "$_id",
                        "frequencia": 1
                    }
                },
                {
                    "$sort": {"frequencia": -1}
                }
            ]

            resultados = await self.collection.aggregate(pipeline).to_list(length=None)
            logger.info(f"Tipos de manutenção mais frequentes: {resultados}")
            return resultados
        except Exception as e:
            logger.error(f"Erro ao buscar tipos de manutenção mais frequentes: {e}")
            return []

    async def get_quantidade_manutencoes(self) -> int:
        try:
            quantidade = await self.collection.count_documents({})
            logger.info(f"Quantidade total de manutenções: {quantidade}")
            return quantidade
        except Exception as e:
            logger.error(f"Erro ao contar quantidade de manutenções: {e}")
            return 0