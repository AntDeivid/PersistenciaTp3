from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from src.app.models.usuario import Usuario
from src.app.repositories.usuario_repository import UsuarioRepository

usuario_router = APIRouter()
usuario_router.prefix = "/api/usuarios"
usuario_router.tags = ["Usuários"]


def get_usuario_repository() -> UsuarioRepository:
    return UsuarioRepository()


@usuario_router.post("/", response_model=Usuario, status_code=201)
async def criar_usuario(usuario: Usuario, usuario_repo: UsuarioRepository = Depends(get_usuario_repository)):
    try:
        usuario_criado = await usuario_repo.criar_usuario(usuario)
        if not usuario_criado:
            raise HTTPException(status_code=500, detail="Erro ao criar usuário")
        return usuario_criado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@usuario_router.get("/", response_model=List[Usuario])
async def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    usuario_repo: UsuarioRepository = Depends(get_usuario_repository)
):
    return await usuario_repo.listar_usuarios(skip=skip, limit=limit)


@usuario_router.get("/{usuario_id}", response_model=Usuario)
async def buscar_usuario_por_id(
    usuario_id: str,
    usuario_repo: UsuarioRepository = Depends(get_usuario_repository)
):
    usuario = await usuario_repo.buscar_usuario_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@usuario_router.put("/{usuario_id}", response_model=Usuario)
async def atualizar_usuario(
    usuario_id: str,
    usuario: Usuario,
    usuario_repo: UsuarioRepository = Depends(get_usuario_repository)
):
    usuario_atualizado = await usuario_repo.atualizar_usuario(usuario_id, usuario)
    if not usuario_atualizado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou ID inválido")
    return usuario_atualizado


@usuario_router.delete("/{usuario_id}", status_code=204)
async def deletar_usuario(usuario_id: str, usuario_repo: UsuarioRepository = Depends(get_usuario_repository)):
    if not await usuario_repo.deletar_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou ID inválido")
    return  


@usuario_router.get("/buscar/{nome}", response_model=List[Usuario])
async def buscar_usuario_por_nome(nome: str, usuario_repo: UsuarioRepository = Depends(get_usuario_repository)):
    usuarios = await usuario_repo.buscar_usuario_por_nome(nome)
    return usuarios

@usuario_router.get("/estatisticas/total", response_model=int)
async def obter_total_usuarios(usuario_repo: UsuarioRepository = Depends(get_usuario_repository)):
    total = await usuario_repo.total_usuarios()
    return total