import logging
from typing import Optional, List

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from src.app.core.db.database import database 
from src.app.models.usuario import Usuario

logger = logging.getLogger('app_logger.usuario_repository')

class UsuarioRepository:
    def __init__(self):
        self.collection = database.get_collection("usuarios")
        
    async def criar_usuario(self, usuario: Usuario) -> Optional[Usuario]:
        try:
            usuario_dict = usuario.dict(by_alias=True, exclude={"id"}) 
            novo_usuario = await self.collection.insert_one(usuario_dict)
            usuario_criado = await self.collection.find_one({"_id": novo_usuario.inserted_id})

            if not usuario_criado:
                logger.error("Erro ao criar usuário: Usuário não encontrado após inserção")
                return None

            usuario_criado["_id"] = str(usuario_criado["_id"])  
            logger.info(f"Usuário criado com sucesso: {usuario_criado}")
            return Usuario(**usuario_criado) 
        except DuplicateKeyError as e:
            logger.error(f"Erro ao criar usuário: Email já cadastrado - {e}")
            raise ValueError("Email já cadastrado") from e 
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return None

    async def listar_usuarios(self, skip: int = 0, limit: int = 10) -> List[Usuario]:
        try:
            usuarios = await self.collection.find().skip(skip).limit(limit).to_list(length=limit)
            
            for usuario in usuarios:
                usuario["_id"] = str(usuario["_id"])

            logger.info(f"Usuários listados com sucesso: {usuarios}")
            return [Usuario(**usuario) for usuario in usuarios]
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return []

    async def buscar_usuario_por_id(self, usuario_id: str) -> Optional[Usuario]:
        try:
            filtro = {"_id": ObjectId(usuario_id)} if ObjectId.is_valid(usuario_id) else {"_id": usuario_id}
            usuario = await self.collection.find_one(filtro)

            if not usuario:
                logger.warning(f"Usuário com ID {usuario_id} não encontrado")
                return None

            usuario["_id"] = str(usuario["_id"])
            logger.info(f"Usuário encontrado com ID {usuario_id}: {usuario}")
            return Usuario(**usuario) 
        except Exception as e:
            logger.error(f"Erro ao buscar usuário com ID {usuario_id}: {e}")
            return None

    async def atualizar_usuario(self, usuario_id: str, usuario: Usuario) -> Optional[Usuario]:
        try:
            if not ObjectId.is_valid(usuario_id):
                logger.warning(f"ID de usuário inválido: {usuario_id}")
                return None

            usuario_dict = usuario.dict(by_alias=True, exclude={"id"})
            resultado = await self.collection.update_one({"_id": ObjectId(usuario_id)}, {"$set": usuario_dict})

            if resultado.matched_count == 0:
                logger.warning(f"Usuário com ID {usuario_id} não encontrado para atualização")
                return None

            usuario_atualizado = await self.collection.find_one({"_id": ObjectId(usuario_id)})
            usuario_atualizado["_id"] = str(usuario_atualizado["_id"])
            logger.info(f"Usuário atualizado com sucesso: {usuario_atualizado}")
            return Usuario(**usuario_atualizado)
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário com ID {usuario_id}: {e}")
            return None

    async def deletar_usuario(self, usuario_id: str) -> bool:
        try:
            if not ObjectId.is_valid(usuario_id):
                logger.warning(f"ID de usuário inválido: {usuario_id}")
                return False

            resultado = await self.collection.delete_one({"_id": ObjectId(usuario_id)})
            if resultado.deleted_count > 0:
                logger.info(f"Usuário com ID {usuario_id} deletado com sucesso")
                return True
            else:
                logger.warning(f"Usuário com ID {usuario_id} não encontrado para deleção")
                return False
        except Exception as e:
            logger.error(f"Erro ao deletar usuário com ID {usuario_id}: {e}")
            return False

    async def buscar_usuario_por_nome(self, nome: str) -> List[Usuario]:
        try:
            usuarios = await self.collection.find({"nome": {"$regex": nome, "$options": "i"}}).to_list(length=None)

            for usuario in usuarios:
                usuario["_id"] = str(usuario["_id"])

            logger.info(f"Usuários encontrados com nome {nome}: {usuarios}")
            return [Usuario(**usuario) for usuario in usuarios]
        except Exception as e:
            logger.error(f"Erro ao buscar usuários por nome {nome}: {e}")
            return []

    async def total_usuarios(self) -> int:
        try:
            total = await self.collection.count_documents({})
            logger.info(f"Total de usuários: {total}")
            return total
        except Exception as e:
            logger.error(f"Erro ao contar total de usuários: {e}")
            return 0