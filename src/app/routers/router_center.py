from fastapi.routing import APIRouter

from src.app.routers.contrato_router import contrato_router
from src.app.routers.usuario_router import usuario_router
from src.app.routers.pagamento_router import pagamento_router
from src.app.routers.manutencao_router import manutencao_router
from src.app.routers.veiculo_manutencao_router import veiculo_manutencao_router
from src.app.routers.veiculo_router import veiculo_router

router = APIRouter()

router.include_router(usuario_router)
router.include_router(contrato_router)
router.include_router(pagamento_router)
router.include_router(manutencao_router)
router.include_router(veiculo_router)
router.include_router(veiculo_manutencao_router)