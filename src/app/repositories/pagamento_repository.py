import logging
from datetime import datetime
from typing import Optional, List, Dict
from typing import Any

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from src.app.core.db.database import database
from src.app.dtos.pagamento_dto import PagamentoDTO  
from src.app.models.pagamento import Pagamento

logger = logging.getLogger('app_logger.pagamento_repository')


class PagamentoRepository:

    def __init__(self):
        self.collection = database.get_collection("pagamentos")

    async def create(self, pagamento: Pagamento) -> Optional[PagamentoDTO]:
        try:
            pagamento_dict = pagamento.dict(by_alias=True, exclude={"id"})
            novo_pagamento = await self.collection.insert_one(pagamento_dict)
            pagamento_criado = await self.collection.find_one({"_id": novo_pagamento.inserted_id})

            if not pagamento_criado:
                logger.error("Erro ao criar pagamento: Pagamento não encontrado após inserção")
                return None

            logger.info(f"Pagamento criado com sucesso: {pagamento_criado}")
            pagamento = Pagamento(**pagamento_criado)
            return PagamentoDTO.from_model(pagamento)

        except DuplicateKeyError as e:
            logger.error(f"Erro ao criar pagamento: Pagamento duplicado - {e}")
            raise ValueError("Erro ao criar pagamento: Pagamento duplicado") from e
        except Exception as e:
            logger.error(f"Erro ao criar pagamento: {e}")
            return None

    async def get_all_no_pagination(self) -> List[PagamentoDTO]:
        try:
            pagamentos = await self.collection.find().to_list(length=None)
            logger.info(f"Pagamentos listados sem paginação: {pagamentos}")
            result = [Pagamento(**pagamento) for pagamento in pagamentos]
            return [PagamentoDTO.from_model(pagamento) for pagamento in result]
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
    ) -> List[PagamentoDTO]:
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

            logger.info(f"Pagamentos encontrados: {pagamentos}")
            result = [Pagamento(**pagamento) for pagamento in pagamentos]
            return [PagamentoDTO.from_model(pagamento) for pagamento in result]
        except Exception as e:
            logger.error(f"Erro ao buscar pagamentos: {e}")
            return []

    async def get_by_id(self, pagamento_id: str) -> Optional[PagamentoDTO]:
        try:
            filtro = {"_id": ObjectId(pagamento_id)} if ObjectId.is_valid(pagamento_id) else {"_id": pagamento_id}
            pagamento = await self.collection.find_one(filtro)

            if not pagamento:
                logger.warning(f"Pagamento com ID {pagamento_id} não encontrado")
                return None

            logger.info(f"Pagamento encontrado com ID {pagamento_id}: {pagamento}")
            return PagamentoDTO.from_model(Pagamento(**pagamento))
        except Exception as e:
            logger.error(f"Erro ao buscar pagamento com ID {pagamento_id}: {e}")
            return None

    async def update(self, pagamento_id: str, pagamento: Pagamento) -> Optional[PagamentoDTO]:
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
                logger.info(f"Pagamento atualizado com sucesso: {result}")
                pagamento = Pagamento(**result)
                return PagamentoDTO.from_model(pagamento)
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

    from typing import Optional

    async def get_pagamentos_pendentes_por_usuario(self, usuario_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "contratos",
                        "localField": "_id",
                        "foreignField": "pagamento_id",
                        "as": "contrato"
                    }
                },
                {
                    "$unwind": "$contrato"
                },
                {
                    "$lookup": {
                        "from": "usuarios",
                        "localField": "contrato.usuario_id",
                        "foreignField": "_id",
                        "as": "usuario"
                    }
                },
                {
                    "$unwind": "$usuario"
                },
                {
                    "$match": {
                        "pago": False,
                        **({"usuario._id": ObjectId(usuario_id)} if usuario_id else {})
                    }
                },
                {
                    "$group": {
                        "_id": "$usuario._id",
                        "nome": {"$first": "$usuario.nome"},
                        "email": {"$first": "$usuario.email"},
                        "total_pendente": {"$sum": "$valor"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "nome": 1,
                        "email": 1,
                        "total_pendente": 1
                    }
                },
                {
                    "$sort": {
                        "total_pendente": -1
                    }
                }
            ]

            pagamentos_pendentes = await self.collection.aggregate(pipeline).to_list(length=None)
            logger.info(f"Pagamentos pendentes por usuário (usuario_id={usuario_id}): {pagamentos_pendentes}")
            return pagamentos_pendentes

        except Exception as e:
            logger.error(f"Erro ao buscar pagamentos pendentes por usuário (usuario_id={usuario_id}): {e}")
            return []