from fastapi.routing import APIRouter

from src.app.routers.usuario_router import usuario_router
from src.app.routers.pagamento_router import pagamento_router

router = APIRouter()

router.include_router(usuario_router)
router.include_router(pagamento_router)
