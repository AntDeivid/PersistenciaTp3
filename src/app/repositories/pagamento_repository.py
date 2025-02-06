import logging
from datetime import datetime
from typing import Optional, List

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from src.app.core.db.database import database 
from src.app.models.pagamento import Pagamento 

logger = logging.getLogger('app_logger.pagamento_repository')

class PagamentoRepository:

    def __init__(self):
        self.collection = database.get_collection("pagamentos")
    
    async def create(self, pagamento: Pagamento) -> Optional[Pagamento]:
        try:
            pagamento_dict = pagamento.dict(by_alias=True, exclude={"id"})
            novo_pagamento = await self.collection.insert_one(pagamento_dict)
            pagamento_criado = await self.collection.find_one({"_id": novo_pagamento.inserted_id})

            if not pagamento_criado:
                logger.error("Erro ao criar pagamento: Pagamento não encontrado após inserção")
                return None

            pagamento_criado["_id"] = str(pagamento_criado["_id"])
            logger.info(f"Pagamento criado com sucesso: {pagamento_criado}")
            return Pagamento(**pagamento_criado)

        except DuplicateKeyError as e:
            logger.error(f"Erro ao criar pagamento: Pagamento duplicado - {e}")
            raise ValueError("Erro ao criar pagamento: Pagamento duplicado") from e  
        except Exception as e:
            logger.error(f"Erro ao criar pagamento: {e}")
            return None

    async def get_all_no_pagination(self) -> List[Pagamento]:
        try:
            pagamentos = await self.collection.find().to_list(length=None)
            for pagamento in pagamentos:
                pagamento["_id"] = str(pagamento["_id"])
            logger.info(f"Pagamentos listados sem paginação: {pagamentos}")
            return [Pagamento(**pagamento) for pagamento in pagamentos]
        except Exception as e:
            logger.error(f"Erro ao listar pagamentos sem paginação: {e}")
            return []

    async def get_all(
        self,
        data_inicial: Optional[datetime] = None,
        data_final: Optional[datetime] = None,
        pago: Optional[bool] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 10
    ) -> List[Pagamento]:
        try:
            filtro = {}
            if data_inicial and data_final:
                filtro["vencimento"] = {"$gte": data_inicial, "$lte": data_final}
            elif data_inicial:
                filtro["vencimento"] = data_inicial
            if pago is not None:
                filtro["pago"] = pago

            logger.info(f"Buscando pagamentos com filtros: {filtro}, página={page}, limite={limit}")

            skip = (page - 1) * limit
            pagamentos = await self.collection.find(filtro).skip(skip).limit(limit).to_list(length=limit)

            for pagamento in pagamentos:
                pagamento["_id"] = str(pagamento["_id"])
            logger.info(f"Pagamentos encontrados: {pagamentos}")
            return [Pagamento(**pagamento) for pagamento in pagamentos]
        except Exception as e:
            logger.error(f"Erro ao buscar pagamentos: {e}")
            return []

    async def get_by_id(self, pagamento_id: str) -> Optional[Pagamento]:
        try:
            filtro = {"_id": ObjectId(pagamento_id)} if ObjectId.is_valid(pagamento_id) else {"_id": pagamento_id}
            pagamento = await self.collection.find_one(filtro)

            if not pagamento:
                logger.warning(f"Pagamento com ID {pagamento_id} não encontrado")
                return None

            pagamento["_id"] = str(pagamento["_id"])
            logger.info(f"Pagamento encontrado com ID {pagamento_id}: {pagamento}")
            return Pagamento(**pagamento)
        except Exception as e:
            logger.error(f"Erro ao buscar pagamento com ID {pagamento_id}: {e}")
            return None

    async def update(self, pagamento_id: str, pagamento: Pagamento) -> Optional[Pagamento]:
        try:
            if not ObjectId.is_valid(pagamento_id):
                logger.warning(f"ID de pagamento inválido: {pagamento_id}")
                return None

            pagamento_dict = pagamento.dict(by_alias=True, exclude={"id"})
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(pagamento_id)},
                {"$set": pagamento_dict},
                return_document=ReturnDocument.AFTER  
            )

            if result:
                result["_id"] = str(result["_id"])
                logger.info(f"Pagamento atualizado com sucesso: {result}")
                return Pagamento(**result)
            else:
                logger.warning(f"Pagamento com ID {pagamento_id} não encontrado para atualização")
                return None
        except Exception as e:
            logger.error(f"Erro ao atualizar pagamento com ID {pagamento_id}: {e}")
            return None

    async def delete(self, pagamento_id: str) -> bool:
        try:
            if not ObjectId.is_valid(pagamento_id):
                logger.warning(f"ID de pagamento inválido: {pagamento_id}")
                return False

            resultado = await self.collection.delete_one({"_id": ObjectId(pagamento_id)})
            if resultado.deleted_count > 0:
                logger.info(f"Pagamento com ID {pagamento_id} deletado com sucesso")
                return True
            else:
                logger.warning(f"Pagamento com ID {pagamento_id} não encontrado para deleção")
                return False
        except Exception as e:
            logger.error(f"Erro ao deletar pagamento com ID {pagamento_id}: {e}")
            return False