import logging
from typing import Optional, List, Dict, Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from src.app.core.db.database import database 
from src.app.models.usuario import Usuario

class UsuarioRepository:
    def __init__(self):
        self.collection = database.get_collection("usuarios")  
        self.logger = logging.getLogger(__name__)

    async def criar_usuario(self, usuario: Usuario) -> Usuario:
        try:
            usuario_dict = usuario.dict(by_alias=True, exclude={"id"}) 
            novo_usuario = await self.collection.insert_one(usuario_dict)
            usuario_criado = await self.collection.find_one({"_id": novo_usuario.inserted_id})

            if not usuario_criado:
                self.logger.error("Erro ao criar usuário: Usuário não encontrado após a inserção.")
                return None

            usuario_criado["_id"] = str(usuario_criado["_id"])  
            return Usuario(**usuario_criado) 
        except DuplicateKeyError as e:
            self.logger.error(f"Erro ao criar usuário: Email duplicado - {e}")
            raise ValueError("Email já cadastrado") from e 
        except Exception as e:
            self.logger.error(f"Erro ao criar usuário: {e}")
            return None

    async def listar_usuarios(self, skip: int = 0, limit: int = 10) -> List[Usuario]:
        usuarios = await self.collection.find().skip(skip).limit(limit).to_list(length=limit)
        
        for usuario in usuarios:
            usuario["_id"] = str(usuario["_id"])

        return [Usuario(**usuario) for usuario in usuarios]

    async def buscar_usuario_por_id(self, usuario_id: str) -> Optional[Usuario]:
        try:
            filtro = {"_id": ObjectId(usuario_id)} if ObjectId.is_valid(usuario_id) else {"_id": usuario_id}
            usuario = await self.collection.find_one(filtro)

            if not usuario:
                return None

            usuario["_id"] = str(usuario["_id"])
            return Usuario(**usuario) 

        except Exception as e:
            self.logger.error(f"Erro ao buscar usuário com ID {usuario_id}: {e}")
            return None


    async def atualizar_usuario(self, usuario_id: str, usuario: Usuario) -> Optional[Usuario]:
        try:
            if not ObjectId.is_valid(usuario_id):
                return None

            usuario_dict = usuario.dict(by_alias=True, exclude={"id"})
            resultado = await self.collection.update_one({"_id": ObjectId(usuario_id)}, {"$set": usuario_dict})

            if resultado.matched_count == 0:
                return None

            usuario_atualizado = await self.collection.find_one({"_id": ObjectId(usuario_id)})
            usuario_atualizado["_id"] = str(usuario_atualizado["_id"])
            return Usuario(**usuario_atualizado)

        except Exception as e:
            self.logger.error(f"Erro ao atualizar usuário com ID {usuario_id}: {e}")
            return None


    async def deletar_usuario(self, usuario_id: str) -> bool:
        try:
            if not ObjectId.is_valid(usuario_id):
                return False

            resultado = await self.collection.delete_one({"_id": ObjectId(usuario_id)})
            return resultado.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Erro ao deletar usuário com ID {usuario_id}: {e}")
            return False

    async def buscar_usuario_por_nome(self, nome: str) -> List[Usuario]:
      usuarios = await self.collection.find({"nome": {"$regex": nome, "$options": "i"}}).to_list(length=None)

      for usuario in usuarios:
          usuario["_id"] = str(usuario["_id"])

      return [Usuario(**usuario) for usuario in usuarios]


    async def total_usuarios(self) -> int:
        return await self.collection.count_documents({})